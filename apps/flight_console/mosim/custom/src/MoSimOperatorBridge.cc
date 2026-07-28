#include "MoSimOperatorBridge.h"

#include <QtCore/QCoreApplication>
#include <QtCore/QDir>
#include <QtCore/QFile>
#include <QtCore/QFileInfo>
#include <QtCore/QJsonArray>
#include <QtCore/QJsonDocument>
#include <QtCore/QJsonObject>
#include <QtCore/QRegularExpression>
#include <QtGui/QClipboard>
#include <QtGui/QGuiApplication>

namespace {

QString nativePath(const QString &path)
{
    return QDir::toNativeSeparators(path);
}

QString decimalText(double value)
{
    QString text = QString::number(value, 'f', 6);
    while (text.contains(QLatin1Char('.')) && text.endsWith(QLatin1Char('0'))) {
        text.chop(1);
    }
    if (text.endsWith(QLatin1Char('.'))) {
        text.chop(1);
    }
    return text;
}

bool containsString(const QVariantList &values, const QString &needle)
{
    for (const QVariant &value : values) {
        if (value.toString() == needle) {
            return true;
        }
    }
    return false;
}

bool isSafeEnvironmentName(const QString &value)
{
    static const QRegularExpression pattern(QStringLiteral("^[A-Za-z_][A-Za-z0-9_]*$"));
    return pattern.match(value).hasMatch();
}

bool isSafeInvocationToken(const QString &value)
{
    // Invocation data is catalog-owned, but it is still copied into a shell.
    // Keep this narrow until a typed argument schema is introduced.
    static const QRegularExpression pattern(QStringLiteral("^[A-Za-z0-9_./:=+\\-]+$"));
    return !value.isEmpty() && pattern.match(value).hasMatch();
}

bool isQgcRunId(const QString &value)
{
    static const QRegularExpression pattern(QStringLiteral("^qgc-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$"));
    return pattern.match(value).hasMatch();
}

bool isActiveRunState(const QString &value)
{
    return value == QStringLiteral("launch_prepared")
        || value == QStringLiteral("running")
        || value == QStringLiteral("replaying");
}

bool isExpectedVehicleId(const QString &value, int vehicleCount)
{
    static const QRegularExpression pattern(QStringLiteral("^uav([1-9])$"));
    const QRegularExpressionMatch match = pattern.match(value);
    return vehicleCount >= 1 && match.hasMatch() && match.captured(1).toInt() <= vehicleCount;
}

bool isReadableFaultAck(const QVariantMap &ack, const QString &runId, int vehicleCount)
{
    const QString target = ack.value(QStringLiteral("target")).toString();
    if (ack.value(QStringLiteral("schema")).toString() != QStringLiteral("mosim.runtime_injection_ack.v1")
        || ack.value(QStringLiteral("run_id")).toString() != runId
        || ack.value(QStringLiteral("command_id")).toString().isEmpty()
        || !isExpectedVehicleId(ack.value(QStringLiteral("vehicle_id")).toString(), vehicleCount)
        || !ack.contains(QStringLiteral("accepted"))
        || !ack.contains(QStringLiteral("applied_at"))) {
        return false;
    }
    if (target == QStringLiteral("motor_effectiveness")) {
        const int rotorIndex = ack.value(QStringLiteral("rotor_index")).toInt();
        return rotorIndex >= 1 && rotorIndex <= 4;
    }
    return target == QStringLiteral("wind_speed_mps") || target == QStringLiteral("wind_direction_deg");
}

bool isReadableOperatorRuntimeStatus(const QVariantMap &status, const QVariantMap &manifest)
{
    const QString expectedBackend = manifest.value(QStringLiteral("controller_backend")).toString();
    if (expectedBackend.isEmpty()
        || status.value(QStringLiteral("schema")).toString() != QStringLiteral("mosim.operator_runtime_status.v1")
        || status.value(QStringLiteral("run_id")).toString() != manifest.value(QStringLiteral("run_id")).toString()
        || status.value(QStringLiteral("experiment_profile_id")).toString()
            != manifest.value(QStringLiteral("experiment_profile_id")).toString()
        || status.value(QStringLiteral("experiment_profile_hash")).toString()
            != manifest.value(QStringLiteral("experiment_profile_hash")).toString()
        || status.value(QStringLiteral("state")).toString().isEmpty()
        || status.value(QStringLiteral("reason_code")).toString().isEmpty()
        || !status.value(QStringLiteral("updated_at_unix_s")).canConvert<double>()) {
        return false;
    }
    if (status.value(QStringLiteral("controller_backend")).toString() != expectedBackend) {
        return false;
    }
    const QVariant observability = status.value(QStringLiteral("observability"));
    const QVariant alerts = status.value(QStringLiteral("alerts"));
    return (!observability.isValid() || observability.canConvert<QVariantMap>())
        && (!alerts.isValid() || alerts.canConvert<QVariantList>());
}

QString bashQuote(const QString &value)
{
    return QStringLiteral("'%1'").arg(value);
}

QString powerShellQuote(QString value)
{
    value.replace(QLatin1Char('\''), QStringLiteral("''"));
    return QStringLiteral("'%1'").arg(value);
}

QString wslPath(const QString &windowsPath)
{
    QString path = QDir::fromNativeSeparators(windowsPath);
    if (path.size() >= 3 && path.at(1) == QLatin1Char(':') && path.at(2) == QLatin1Char('/')) {
        path = QStringLiteral("/mnt/%1/%2").arg(path.left(1).toLower(), path.mid(3));
    }
    return path;
}

} // namespace

MoSimOperatorBridge::MoSimOperatorBridge(QObject *parent)
    : QObject(parent)
    , _projectRoot(discoverProjectRoot())
{
    refresh();
}

QVariantMap MoSimOperatorBridge::selectedProfile() const
{
    return profileForId(_selectedProfileId);
}

bool MoSimOperatorBridge::profileSelectionLocked() const
{
    return !_runManifest.value(QStringLiteral("experiment_profile_id")).toString().isEmpty();
}

QString MoSimOperatorBridge::discoverProjectRoot() const
{
    const QString configured = qEnvironmentVariable("MOSIM_PROJECT_ROOT");
    QStringList candidates;
    if (!configured.isEmpty()) {
        candidates << configured;
    }
    candidates << QDir::currentPath() << QCoreApplication::applicationDirPath();

    for (const QString &candidatePath : candidates) {
        QDir candidate(candidatePath);
        for (int depth = 0; depth < 14; ++depth) {
            if (candidate.exists(QStringLiteral("AGENTS.md"))
                && candidate.exists(QStringLiteral("Config/profiles/operator_profiles.json"))
                && candidate.exists(QStringLiteral("Scripts/ui/replay_rosbag_operator_map.py"))) {
                return candidate.absolutePath();
            }
            if (!candidate.cdUp()) {
                break;
            }
        }
    }
    return QString();
}

QString MoSimOperatorBridge::projectPath(const QString &relativePath) const
{
    return _projectRoot.isEmpty() ? QString() : QDir(_projectRoot).filePath(relativePath);
}

QVariantMap MoSimOperatorBridge::readJsonObject(const QString &path) const
{
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly)) {
        return {};
    }
    QJsonParseError error;
    const QJsonDocument document = QJsonDocument::fromJson(file.readAll(), &error);
    return error.error == QJsonParseError::NoError && document.isObject()
        ? document.object().toVariantMap()
        : QVariantMap{};
}

void MoSimOperatorBridge::loadCatalogs()
{
    _operatorProfiles.clear();
    _controllerFamilies.clear();
    _controllerSchemes.clear();
    _operatorMaps.clear();
    _operatorMap.clear();
    _runtimeBackendCatalog = readJsonObject(projectPath(QStringLiteral("Config/control_platform/runtime_backend_catalog.json")));
    const QVariantMap mapCatalog = readJsonObject(projectPath(QStringLiteral("Config/control_platform/operator_map_catalog.json")));
    for (const QVariant &value : mapCatalog.value(QStringLiteral("maps")).toList()) {
        const QVariantMap candidate = value.toMap();
        if (candidate.value(QStringLiteral("enabled")).toBool()) {
            _operatorMaps.append(candidate);
        }
    }

    const QVariantMap catalog = readJsonObject(projectPath(QStringLiteral("Config/profiles/operator_profiles.json")));
    for (const QVariant &value : catalog.value(QStringLiteral("profiles")).toList()) {
        QVariantMap profile = value.toMap();
        const QString profileId = profile.value(QStringLiteral("profile_id")).toString();
        const QString profilePath = profile.value(QStringLiteral("profile_path")).toString();
        if (profileId.isEmpty() || profilePath.isEmpty()) {
            continue;
        }
        const QVariantMap document = readJsonObject(projectPath(profilePath));
        const QVariantMap experiment = document.value(QStringLiteral("experiment_profile")).toMap();
        if (!experiment.isEmpty()) {
            profile.insert(QStringLiteral("controller_profile"), experiment.value(QStringLiteral("controller_profile")));
            profile.insert(QStringLiteral("vehicle_count"), experiment.value(QStringLiteral("vehicle_count"), 1));
            profile.insert(QStringLiteral("planner_profile"), experiment.value(QStringLiteral("planner_profile")));
            profile.insert(QStringLiteral("safety_profile"), experiment.value(QStringLiteral("safety_profile")));
            profile.insert(QStringLiteral("fault_profile"), experiment.value(QStringLiteral("fault_profile")));
            profile.insert(QStringLiteral("operator_map_id"), experiment.value(QStringLiteral("operator_map_id")));
        }
        const QString operatorMapId = profile.value(QStringLiteral("operator_map_id")).toString();
        if (profile.value(QStringLiteral("enabled")).toBool() && mapForId(operatorMapId).isEmpty()) {
            profile.insert(QStringLiteral("enabled"), false);
            profile.insert(QStringLiteral("disabled_reason"), QStringLiteral("Profile 未登记可用二维地图"));
        }
        const QVariantMap backend = runtimeBackendForProfile(profileId);
        profile.insert(QStringLiteral("runtime_command_available"), !backend.isEmpty());
        profile.insert(QStringLiteral("runtime_status"), backend.value(QStringLiteral("status")));
        if (profile.value(QStringLiteral("enabled")).toBool() && backend.isEmpty()) {
            profile.insert(QStringLiteral("enabled"), false);
            profile.insert(QStringLiteral("disabled_reason"), QStringLiteral("未登记可复制的运行入口"));
        }
        _operatorProfiles.append(profile);
    }

    for (int index = 0; index < _operatorMaps.size(); ++index) {
        QVariantMap map = _operatorMaps.at(index).toMap();
        const QString mapId = map.value(QStringLiteral("map_id")).toString();
        QVariantList compatibleProfileIds;
        int enabledProfileCount = 0;
        QString disabledReason;
        for (const QVariant &profileValue : _operatorProfiles) {
            const QVariantMap profile = profileValue.toMap();
            if (profile.value(QStringLiteral("operator_map_id")).toString() != mapId) {
                continue;
            }
            compatibleProfileIds.append(profile.value(QStringLiteral("profile_id")));
            if (profile.value(QStringLiteral("enabled")).toBool()) {
                ++enabledProfileCount;
            } else if (disabledReason.isEmpty()) {
                disabledReason = profile.value(QStringLiteral("disabled_reason")).toString();
            }
        }
        map.insert(QStringLiteral("compatible_profile_ids"), compatibleProfileIds);
        map.insert(QStringLiteral("compatible_profile_count"), compatibleProfileIds.size());
        map.insert(QStringLiteral("enabled_profile_count"), enabledProfileCount);
        map.insert(QStringLiteral("selectable"), enabledProfileCount > 0);
        if (compatibleProfileIds.isEmpty()) {
            map.insert(QStringLiteral("disabled_reason"), QStringLiteral("尚无已发布兼容 Profile"));
        } else if (enabledProfileCount == 0) {
            map.insert(
                QStringLiteral("disabled_reason"),
                disabledReason.isEmpty() ? QStringLiteral("兼容 Profile 尚未开放") : disabledReason);
        } else {
            map.insert(QStringLiteral("disabled_reason"), QString());
        }
        _operatorMaps[index] = map;
    }

    const QVariantMap controllerCatalog = readJsonObject(
        projectPath(QStringLiteral("Config/control_platform/control_scheme_catalog.json")));
    QVariantMap familyLabels;
    QVariantMap familyCounts;
    for (const QVariant &value : controllerCatalog.value(QStringLiteral("families")).toList()) {
        QVariantMap family = value.toMap();
        const QString category = family.value(QStringLiteral("category")).toString();
        if (category.isEmpty()) {
            continue;
        }
        family.insert(QStringLiteral("controller_count"), 0);
        familyLabels.insert(category, family.value(QStringLiteral("display_name_zh")).toString());
        _controllerFamilies.append(family);
    }

    for (const QVariant &value : controllerCatalog.value(QStringLiteral("schemes")).toList()) {
        QVariantMap scheme = value.toMap();
        const QString schemeId = scheme.value(QStringLiteral("scheme_id")).toString();
        const QString category = scheme.value(QStringLiteral("category")).toString();
        if (schemeId.isEmpty() || category.isEmpty()) {
            continue;
        }

        QVariantList publishedProfileIds;
        int enabledProfileCount = 0;
        QString disabledReason;
        for (const QVariant &profileValue : _operatorProfiles) {
            const QVariantMap profile = profileValue.toMap();
            if (profile.value(QStringLiteral("controller_scheme_id")).toString() != schemeId) {
                continue;
            }
            publishedProfileIds.append(profile.value(QStringLiteral("profile_id")));
            if (profile.value(QStringLiteral("enabled")).toBool()) {
                ++enabledProfileCount;
            } else if (disabledReason.isEmpty()) {
                disabledReason = profile.value(QStringLiteral("disabled_reason")).toString();
            }
        }

        scheme.insert(QStringLiteral("published_profile_ids"), publishedProfileIds);
        scheme.insert(QStringLiteral("published_profile_count"), publishedProfileIds.size());
        scheme.insert(QStringLiteral("enabled_profile_count"), enabledProfileCount);
        scheme.insert(QStringLiteral("selectable"), enabledProfileCount > 0);
        if (publishedProfileIds.isEmpty()) {
            scheme.insert(QStringLiteral("availability"), QStringLiteral("not_published"));
            scheme.insert(QStringLiteral("disabled_reason"), QStringLiteral("尚无已发布兼容 Profile"));
        } else if (enabledProfileCount == 0) {
            scheme.insert(QStringLiteral("availability"), QStringLiteral("profile_disabled"));
            scheme.insert(
                QStringLiteral("disabled_reason"),
                disabledReason.isEmpty() ? QStringLiteral("兼容 Profile 尚未开放") : disabledReason);
        } else {
            scheme.insert(QStringLiteral("availability"), QStringLiteral("published"));
            scheme.insert(QStringLiteral("disabled_reason"), QString());
        }
        _controllerSchemes.append(scheme);
        familyCounts.insert(category, familyCounts.value(category).toInt() + 1);
        if (!familyLabels.contains(category)) {
            QVariantMap family {
                {QStringLiteral("category"), category},
                {QStringLiteral("display_name_zh"), category == QStringLiteral("engineering_deployment_baseline")
                    ? QStringLiteral("工程部署基线")
                    : category},
                {QStringLiteral("controller_count"), 0},
            };
            _controllerFamilies.append(family);
            familyLabels.insert(category, family.value(QStringLiteral("display_name_zh")).toString());
        }
    }
    for (int index = 0; index < _controllerFamilies.size(); ++index) {
        QVariantMap family = _controllerFamilies.at(index).toMap();
        family.insert(
            QStringLiteral("controller_count"),
            familyCounts.value(family.value(QStringLiteral("category")).toString()).toInt());
        _controllerFamilies[index] = family;
    }

    if (profileForId(_selectedProfileId).isEmpty()) {
        _selectedProfileId.clear();
        for (const QVariant &value : _operatorProfiles) {
            const QVariantMap profile = value.toMap();
            if (profile.value(QStringLiteral("enabled")).toBool()) {
                _selectedProfileId = profile.value(QStringLiteral("profile_id")).toString();
                break;
            }
        }
        if (_selectedProfileId.isEmpty() && !_operatorProfiles.isEmpty()) {
            _selectedProfileId = _operatorProfiles.first().toMap().value(QStringLiteral("profile_id")).toString();
        }
    }
    const QString selectedScheme = controllerSchemeForProfile(_selectedProfileId);
    if (!selectedScheme.isEmpty()) {
        _selectedControllerSchemeId = selectedScheme;
    }
    syncSelectedMapFromProfile();
}

void MoSimOperatorBridge::loadActiveRun()
{
    _runId.clear();
    _runManifest.clear();
    _runtimeTelemetry.clear();
    _faultAcks.clear();
    if (_projectRoot.isEmpty()) {
        return;
    }

    const QVariantMap active = readJsonObject(projectPath(QStringLiteral("Results/ui_platform/qgc_active_run.json")));
    if (active.value(QStringLiteral("schema")).toString() != QStringLiteral("mosim.qgc_active_run_pointer.v1")
        || !isActiveRunState(active.value(QStringLiteral("state")).toString())) {
        return;
    }
    const QString runId = active.value(QStringLiteral("run_id")).toString();
    if (!isQgcRunId(runId)) {
        return;
    }
    const QString expectedRunDirectory = QStringLiteral("Results/runs/%1").arg(runId);
    if (active.value(QStringLiteral("run_directory")).toString() != expectedRunDirectory) {
        return;
    }
    const QString runDirectory = projectPath(QStringLiteral("Results/runs/%1").arg(runId));
    const QVariantMap manifest = readJsonObject(QDir(runDirectory).filePath(QStringLiteral("RUN_MANIFEST.json")));
    if (manifest.value(QStringLiteral("run_id")).toString() != runId) {
        return;
    }
    const QString frozenProfileId = manifest.value(QStringLiteral("experiment_profile_id")).toString();
    if (frozenProfileId.isEmpty() || frozenProfileId != active.value(QStringLiteral("experiment_profile_id")).toString()
        || profileForId(frozenProfileId).isEmpty()
        || manifest.value(QStringLiteral("experiment_profile_hash")).toString().isEmpty()
        || manifest.value(QStringLiteral("experiment_profile_hash")).toString()
            != active.value(QStringLiteral("experiment_profile_hash")).toString()
        || manifest.value(QStringLiteral("runtime_profile_id")).toString()
            != active.value(QStringLiteral("runtime_profile_id")).toString()) {
        return;
    }

    _runId = runId;
    _runManifest = manifest;
    _selectedProfileId = frozenProfileId;
    _selectedControllerSchemeId = controllerSchemeForProfile(frozenProfileId);
    const QVariantMap snapshot = manifest.value(QStringLiteral("operator_map_snapshot")).toMap();
    const QString snapshotHash = manifest.value(QStringLiteral("operator_map_snapshot_hash")).toString();
    if (!snapshot.isEmpty() && !snapshotHash.isEmpty()) {
        _operatorMap = snapshot;
        _operatorMap.insert(QStringLiteral("operator_map_snapshot_hash"), snapshotHash);
        _selectedMapId = snapshot.value(QStringLiteral("map_id")).toString();
    }
    const QVariantMap telemetry = readJsonObject(QDir(runDirectory).filePath(QStringLiteral("telemetry.json")));
    if (telemetry.value(QStringLiteral("run_id")).toString() == _runId) {
        QVariantMap acceptedTelemetry = telemetry;
        const QVariantMap runtimeStatus = telemetry.value(QStringLiteral("operator_runtime_status")).toMap();
        if (!runtimeStatus.isEmpty() && !isReadableOperatorRuntimeStatus(runtimeStatus, manifest)) {
            acceptedTelemetry.remove(QStringLiteral("operator_runtime_status"));
            acceptedTelemetry.insert(
                QStringLiteral("operator_runtime_status_rejected_reason"),
                QStringLiteral("operator_runtime_status_identity_mismatch"));
        }
        _runtimeTelemetry = acceptedTelemetry;
    }
    loadFaultAcks();
}

void MoSimOperatorBridge::loadFaultAcks()
{
    _faultAcks.clear();
    const int vehicleCount = _runManifest.value(QStringLiteral("vehicle_count")).toInt();
    if (_runId.isEmpty() || vehicleCount < 1) {
        return;
    }
    const QDir ackDirectory(QDir(activeRunDirectory()).filePath(QStringLiteral("injection_acks")));
    const QFileInfoList entries = ackDirectory.entryInfoList(
        QStringList{QStringLiteral("*.json")}, QDir::Files, QDir::Name);
    for (const QFileInfo &entry : entries) {
        const QVariantMap ack = readJsonObject(entry.absoluteFilePath());
        if (isReadableFaultAck(ack, _runId, vehicleCount)) {
            _faultAcks.append(ack);
        }
    }
}

void MoSimOperatorBridge::refresh()
{
    if (_projectRoot.isEmpty()) {
        setStatus(QStringLiteral("project_root_missing"), QStringLiteral("未找到 MoSim 项目根目录"));
        return;
    }
    loadCatalogs();
    loadActiveRun();
    if (_runId.isEmpty()) {
        setStatus(QStringLiteral("active_run_missing"), QStringLiteral("已加载操作配置，未检测到活动运行清单"));
    } else if (_runtimeTelemetry.isEmpty()) {
        setStatus(QStringLiteral("telemetry_pending"), QStringLiteral("已加载运行清单，等待真实遥测或 rosbag 回放"));
    } else {
        setStatus(QStringLiteral("telemetry_loaded"), QStringLiteral("已加载当前运行的地图遥测"));
    }
}

void MoSimOperatorBridge::refreshRuntimeState()
{
    const QString selected = _selectedProfileId;
    const QString selectedController = _selectedControllerSchemeId;
    loadActiveRun();
    if (_runId.isEmpty()) {
        _selectedProfileId = selected;
        _selectedControllerSchemeId = selectedController;
        syncSelectedMapFromProfile();
        _runtimeTelemetry.clear();
        setStatus(QStringLiteral("active_run_missing"), QStringLiteral("未检测到活动运行清单"));
        return;
    }
    if (_runtimeTelemetry.isEmpty()) {
        setStatus(QStringLiteral("telemetry_pending"), QStringLiteral("已冻结本次运行，等待真实遥测或 rosbag 回放"));
        return;
    }
    setStatus(QStringLiteral("telemetry_loaded"), QStringLiteral("已加载当前运行的地图遥测"));
}

QVariantMap MoSimOperatorBridge::profileForId(const QString &profileId) const
{
    for (const QVariant &value : _operatorProfiles) {
        const QVariantMap profile = value.toMap();
        if (profile.value(QStringLiteral("profile_id")).toString() == profileId) {
            return profile;
        }
    }
    return {};
}

QVariantMap MoSimOperatorBridge::controllerForId(const QString &schemeId) const
{
    for (const QVariant &value : _controllerSchemes) {
        const QVariantMap scheme = value.toMap();
        if (scheme.value(QStringLiteral("scheme_id")).toString() == schemeId) {
            return scheme;
        }
    }
    return {};
}

QVariantMap MoSimOperatorBridge::mapForId(const QString &mapId) const
{
    for (const QVariant &value : _operatorMaps) {
        const QVariantMap map = value.toMap();
        if (map.value(QStringLiteral("map_id")).toString() == mapId) {
            return map;
        }
    }
    return {};
}

QString MoSimOperatorBridge::controllerSchemeForProfile(const QString &profileId) const
{
    return profileForId(profileId).value(QStringLiteral("controller_scheme_id")).toString();
}

void MoSimOperatorBridge::syncSelectedMapFromProfile()
{
    const QString profileMapId = selectedProfile().value(QStringLiteral("operator_map_id")).toString();
    const QVariantMap map = mapForId(profileMapId);
    if (map.isEmpty()) {
        _selectedMapId.clear();
        _operatorMap.clear();
        return;
    }
    _selectedMapId = profileMapId;
    _operatorMap = map;
}

QVariantMap MoSimOperatorBridge::runtimeBackendForProfile(const QString &profileId) const
{
    for (const QVariant &value : _runtimeBackendCatalog.value(QStringLiteral("runtime_profiles")).toList()) {
        const QVariantMap backend = value.toMap();
        if (containsString(backend.value(QStringLiteral("experiment_profile_ids")).toList(), profileId)) {
            return backend;
        }
    }
    return {};
}

QString MoSimOperatorBridge::activeRunDirectory() const
{
    return _runId.isEmpty() ? QString() : projectPath(QStringLiteral("Results/runs/%1").arg(_runId));
}

QString MoSimOperatorBridge::renderRuntimeCommand(const QVariantMap &profile, const QVariantMap &backend) const
{
    const QString script = backend.value(QStringLiteral("project_script")).toString();
    const QVariantMap invocation = backend.value(QStringLiteral("operator_invocation")).toMap();
    if (script.isEmpty() || _projectRoot.isEmpty() || invocation.isEmpty()) {
        return QString();
    }
    const QString absoluteScript = projectPath(script);
    const QString preparationScript = projectPath(QStringLiteral("Scripts/ui/prepare_operator_run.py"));
    QVariantMap environment = invocation.value(QStringLiteral("shell_environment")).toMap();
    const QVariantMap metadata {
        {QStringLiteral("MOSIM_OPERATOR_PROFILE_ID"), profile.value(QStringLiteral("profile_id")).toString()},
        {QStringLiteral("MOSIM_CONTROLLER_PROFILE"), profile.value(QStringLiteral("controller_profile")).toString()},
        {QStringLiteral("MOSIM_VEHICLE_COUNT"), QString::number(profile.value(QStringLiteral("vehicle_count")).toInt())},
        {QStringLiteral("MOSIM_PLANNER_PROFILE"), profile.value(QStringLiteral("planner_profile")).toString()},
        {QStringLiteral("MOSIM_OPERATOR_MODE"), profile.value(QStringLiteral("operator_mode")).toString()},
        {QStringLiteral("MOSIM_RUNTIME_PROFILE_ID"), backend.value(QStringLiteral("runtime_profile_id")).toString()},
        {QStringLiteral("MOSIM_RUNTIME_OPERATION_ID"), backend.value(QStringLiteral("operation_id")).toString()},
    };
    for (auto iterator = metadata.cbegin(); iterator != metadata.cend(); ++iterator) {
        if (environment.contains(iterator.key())) {
            return QString();
        }
        environment.insert(iterator.key(), iterator.value());
    }
    const QString profileId = profile.value(QStringLiteral("profile_id")).toString();
    const QString runtimeProfileId = backend.value(QStringLiteral("runtime_profile_id")).toString();
    if (!isSafeInvocationToken(profileId) || !isSafeInvocationToken(runtimeProfileId)
        || !QFileInfo::exists(preparationScript)
        || environment.contains(QStringLiteral("MOSIM_OPERATOR_RUN_ID"))
        || environment.contains(QStringLiteral("MOSIM_OPERATOR_RUN_DIR"))
        || environment.contains(QStringLiteral("MOSIM_OPERATOR_RUN_MANIFEST"))) {
        return QString();
    }

    QStringList arguments;
    for (const QVariant &value : invocation.value(QStringLiteral("arguments")).toList()) {
        const QString argument = value.toString();
        if (!isSafeInvocationToken(argument)) {
            return QString();
        }
        arguments.append(argument);
    }
    for (auto iterator = environment.cbegin(); iterator != environment.cend(); ++iterator) {
        const QString value = iterator.value().toString();
        if (!isSafeEnvironmentName(iterator.key()) || !isSafeInvocationToken(value)) {
            return QString();
        }
    }

    if (script.endsWith(QStringLiteral(".ps1"), Qt::CaseInsensitive)) {
        QStringList statements;
        statements.append(QStringLiteral("$runId = & python %1 --profile-id %2 --runtime-profile-id %3 --print-run-id")
            .arg(powerShellQuote(nativePath(preparationScript)), powerShellQuote(profileId), powerShellQuote(runtimeProfileId)));
        statements.append(QStringLiteral("if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }"));
        statements.append(QStringLiteral("$env:MOSIM_OPERATOR_RUN_ID = $runId"));
        statements.append(QStringLiteral("$env:MOSIM_OPERATOR_RUN_DIR = %1 + '\\' + $runId")
            .arg(powerShellQuote(nativePath(projectPath(QStringLiteral("Results/runs"))))));
        statements.append(QStringLiteral("$env:MOSIM_OPERATOR_RUN_MANIFEST = $env:MOSIM_OPERATOR_RUN_DIR + '\\RUN_MANIFEST.json'"));
        for (auto iterator = environment.cbegin(); iterator != environment.cend(); ++iterator) {
            statements.append(QStringLiteral("$env:%1 = %2")
                .arg(iterator.key(), powerShellQuote(iterator.value().toString())));
        }
        QString command = QStringLiteral("& %1").arg(powerShellQuote(nativePath(absoluteScript)));
        for (const QString &argument : arguments) {
            command += QLatin1Char(' ') + argument;
        }
        statements.append(command);
        const QString commandBody = QStringLiteral("& { %1 }").arg(statements.join(QStringLiteral("; ")));
        if (commandBody.contains(QLatin1Char('"')) || commandBody.contains(QLatin1Char('\r')) || commandBody.contains(QLatin1Char('\n'))) {
            return QString();
        }
        return QStringLiteral("powershell.exe -NoProfile -ExecutionPolicy Bypass -Command \"%1\"").arg(commandBody);
    }
    if (script.endsWith(QStringLiteral(".sh"), Qt::CaseInsensitive)) {
        const QString wslRoot = wslPath(_projectRoot);
        const QString distribution = backend.value(QStringLiteral("wsl_distribution"), QStringLiteral("Ubuntu-20.04")).toString();
        if (wslRoot.contains(QLatin1Char('\'')) || wslRoot.contains(QLatin1Char('"')) || !isSafeInvocationToken(distribution)) {
            return QString();
        }
        const QString wslRunsRoot = wslPath(projectPath(QStringLiteral("Results/runs")));
        if (wslRunsRoot.contains(QLatin1Char('\'')) || wslRunsRoot.contains(QLatin1Char('"'))) {
            return QString();
        }
        QStringList statements {
            QStringLiteral("cd %1").arg(bashQuote(wslRoot)),
            QStringLiteral("MOSIM_OPERATOR_RUN_ID=$(python3 %1 --profile-id %2 --runtime-profile-id %3 --print-run-id)")
                .arg(bashQuote(QStringLiteral("Scripts/ui/prepare_operator_run.py")), bashQuote(profileId), bashQuote(runtimeProfileId)),
            QStringLiteral("export MOSIM_OPERATOR_RUN_ID"),
            QStringLiteral("export MOSIM_OPERATOR_RUN_DIR=%1${MOSIM_OPERATOR_RUN_ID}").arg(bashQuote(wslRunsRoot + QLatin1Char('/'))),
            QStringLiteral("export MOSIM_OPERATOR_RUN_MANIFEST=${MOSIM_OPERATOR_RUN_DIR}'/RUN_MANIFEST.json'"),
        };
        for (auto iterator = environment.cbegin(); iterator != environment.cend(); ++iterator) {
            statements.append(QStringLiteral("export %1=%2")
                .arg(iterator.key(), bashQuote(iterator.value().toString())));
        }
        QString command = QStringLiteral("bash %1").arg(bashQuote(script));
        for (const QString &argument : arguments) {
            command += QLatin1Char(' ') + bashQuote(argument);
        }
        statements.append(command);
        const QString commandBody = statements.join(QStringLiteral(" && "));
        if (commandBody.contains(QLatin1Char('"')) || commandBody.contains(QLatin1Char('\r')) || commandBody.contains(QLatin1Char('\n'))) {
            return QString();
        }
        return QStringLiteral("wsl.exe -d \"%1\" -- bash -lc \"%2\"").arg(distribution, commandBody);
    }
    return QString();
}

void MoSimOperatorBridge::setStatus(const QString &reasonCode, const QString &statusText)
{
    _reasonCode = reasonCode;
    _statusText = statusText;
    emit stateChanged();
}

void MoSimOperatorBridge::copyCommand(const QString &command, const QString &label)
{
    if (command.isEmpty()) {
        setStatus(QStringLiteral("command_unavailable"), QStringLiteral("没有可复制的命令"));
        return;
    }
    _lastCommand = command;
    if (QClipboard *clipboard = QGuiApplication::clipboard()) {
        clipboard->setText(command);
        setStatus(QStringLiteral("command_copied"), label + QStringLiteral("已复制到系统剪贴板"));
        return;
    }
    setStatus(QStringLiteral("clipboard_unavailable"), label + QStringLiteral("已生成，请从命令框手动复制"));
}

void MoSimOperatorBridge::selectProfile(const QString &profileId)
{
    const QString frozenProfileId = _runManifest.value(QStringLiteral("experiment_profile_id")).toString();
    if (!frozenProfileId.isEmpty() && profileId != frozenProfileId) {
        setStatus(QStringLiteral("profile_locked_by_run_manifest"), QStringLiteral("当前 RunManifest 已冻结 Profile，不能切换任务"));
        return;
    }
    const QVariantMap profile = profileForId(profileId);
    if (profile.isEmpty()) {
        setStatus(QStringLiteral("profile_not_found"), QStringLiteral("未找到所选 Profile"));
        return;
    }
    if (!profile.value(QStringLiteral("enabled")).toBool()) {
        setStatus(QStringLiteral("profile_disabled"), profile.value(QStringLiteral("disabled_reason")).toString());
        return;
    }
    _selectedProfileId = profileId;
    _selectedControllerSchemeId = controllerSchemeForProfile(profileId);
    syncSelectedMapFromProfile();
    setStatus(QStringLiteral("profile_selected"), QStringLiteral("已选择已发布 Profile"));
}

void MoSimOperatorBridge::selectControllerScheme(const QString &schemeId)
{
    if (profileSelectionLocked()) {
        setStatus(QStringLiteral("profile_locked_by_run_manifest"), QStringLiteral("当前 RunManifest 已冻结 Profile，不能切换控制器"));
        return;
    }
    const QVariantMap scheme = controllerForId(schemeId);
    if (scheme.isEmpty()) {
        setStatus(QStringLiteral("controller_not_found"), QStringLiteral("未找到所选控制器"));
        return;
    }
    if (!scheme.value(QStringLiteral("selectable")).toBool()) {
        setStatus(
            QStringLiteral("controller_not_published"),
            scheme.value(QStringLiteral("disabled_reason")).toString());
        return;
    }

    const QString currentTaskKey = selectedProfile().value(QStringLiteral("task_key")).toString();
    QVariantMap selected;
    for (const QVariant &value : scheme.value(QStringLiteral("published_profile_ids")).toList()) {
        const QVariantMap candidate = profileForId(value.toString());
        if (candidate.value(QStringLiteral("enabled")).toBool()
            && candidate.value(QStringLiteral("task_key")).toString() == currentTaskKey) {
            selected = candidate;
            break;
        }
    }
    if (selected.isEmpty()) {
        for (const QVariant &value : scheme.value(QStringLiteral("published_profile_ids")).toList()) {
            const QVariantMap candidate = profileForId(value.toString());
            if (candidate.value(QStringLiteral("enabled")).toBool()) {
                selected = candidate;
                break;
            }
        }
    }
    if (selected.isEmpty()) {
        setStatus(QStringLiteral("controller_not_published"), QStringLiteral("控制器没有可用的已发布 Profile"));
        return;
    }
    _selectedProfileId = selected.value(QStringLiteral("profile_id")).toString();
    _selectedControllerSchemeId = schemeId;
    syncSelectedMapFromProfile();
    setStatus(QStringLiteral("controller_selected"), QStringLiteral("已选择控制器并绑定兼容任务 Profile"));
}

void MoSimOperatorBridge::selectOperatorMap(const QString &mapId)
{
    if (profileSelectionLocked()) {
        setStatus(
            QStringLiteral("map_locked_by_run_manifest"),
            QStringLiteral("当前 RunManifest 已冻结地图，不能切换二维地图"));
        return;
    }
    const QVariantMap map = mapForId(mapId);
    if (map.isEmpty()) {
        setStatus(QStringLiteral("map_not_found"), QStringLiteral("未找到所选二维地图"));
        return;
    }
    if (!map.value(QStringLiteral("selectable")).toBool()) {
        setStatus(
            QStringLiteral("map_not_published"),
            map.value(QStringLiteral("disabled_reason")).toString());
        return;
    }

    const QVariantMap current = selectedProfile();
    const QString currentControllerId = current.value(QStringLiteral("controller_scheme_id")).toString();
    const QString currentTaskKey = current.value(QStringLiteral("task_key")).toString();
    QVariantMap fallback;
    QVariantMap selected;
    for (const QVariant &profileValue : _operatorProfiles) {
        const QVariantMap candidate = profileValue.toMap();
        if (!candidate.value(QStringLiteral("enabled")).toBool()
            || candidate.value(QStringLiteral("operator_map_id")).toString() != mapId) {
            continue;
        }
        if (fallback.isEmpty()) {
            fallback = candidate;
        }
        if (candidate.value(QStringLiteral("controller_scheme_id")).toString() != currentControllerId) {
            continue;
        }
        if (selected.isEmpty()) {
            selected = candidate;
        }
        if (candidate.value(QStringLiteral("task_key")).toString() == currentTaskKey) {
            selected = candidate;
            break;
        }
    }
    if (selected.isEmpty()) {
        selected = fallback;
    }
    if (selected.isEmpty()) {
        setStatus(QStringLiteral("map_no_compatible_profile"), QStringLiteral("所选地图没有可用的已发布 Profile"));
        return;
    }

    _selectedProfileId = selected.value(QStringLiteral("profile_id")).toString();
    _selectedControllerSchemeId = selected.value(QStringLiteral("controller_scheme_id")).toString();
    _selectedMapId = mapId;
    _operatorMap = map;
    setStatus(QStringLiteral("map_selected"), QStringLiteral("已选择地图并绑定兼容 Profile"));
}

void MoSimOperatorBridge::copySelectedLaunchCommand()
{
    if (profileSelectionLocked()) {
        setStatus(QStringLiteral("run_manifest_already_active"), QStringLiteral("当前 RunManifest 已冻结，请勿重复启动运行时"));
        return;
    }
    const QVariantMap profile = selectedProfile();
    if (profile.isEmpty()) {
        setStatus(QStringLiteral("profile_not_selected"), QStringLiteral("请先选择 Profile"));
        return;
    }
    if (!profile.value(QStringLiteral("enabled")).toBool()) {
        setStatus(QStringLiteral("profile_disabled"), profile.value(QStringLiteral("disabled_reason")).toString());
        return;
    }
    const QVariantMap backend = runtimeBackendForProfile(_selectedProfileId);
    copyCommand(renderRuntimeCommand(profile, backend), QStringLiteral("运行命令"));
}

void MoSimOperatorBridge::copyClearActiveRunCommand()
{
    if (!profileSelectionLocked()) {
        setStatus(QStringLiteral("active_run_missing"), QStringLiteral("当前没有需要结束的运行清单"));
        return;
    }
    const QString command = QStringLiteral("python \"%1\" --clear-active")
        .arg(nativePath(projectPath(QStringLiteral("Scripts/ui/prepare_operator_run.py"))));
    copyCommand(command, QStringLiteral("清除运行清单命令"));
}

void MoSimOperatorBridge::stageWind(const QString &vehicleId, double speedMps)
{
    if (vehicleId.isEmpty() || speedMps < 0.0 || speedMps > 20.0) {
        setStatus(QStringLiteral("fault_value_invalid"), QStringLiteral("风扰参数超出允许范围"));
        return;
    }
    _pendingFault = {
        {QStringLiteral("target"), QStringLiteral("wind_speed_mps")},
        {QStringLiteral("vehicle_id"), vehicleId},
        {QStringLiteral("value"), speedMps},
    };
    setStatus(QStringLiteral("fault_staged"), QStringLiteral("风扰已暂存，尚未写入运行时"));
}

void MoSimOperatorBridge::stageMotorEffectiveness(const QString &vehicleId, int rotorIndex, double effectiveness)
{
    if (vehicleId.isEmpty() || rotorIndex < 1 || rotorIndex > 4 || effectiveness < 0.0 || effectiveness > 1.0) {
        setStatus(QStringLiteral("fault_value_invalid"), QStringLiteral("电机故障参数超出允许范围"));
        return;
    }
    _pendingFault = {
        {QStringLiteral("target"), QStringLiteral("motor_effectiveness")},
        {QStringLiteral("vehicle_id"), vehicleId},
        {QStringLiteral("rotor_index"), rotorIndex},
        {QStringLiteral("value"), effectiveness},
    };
    setStatus(QStringLiteral("fault_staged"), QStringLiteral("电机故障已暂存，尚未写入运行时"));
}

void MoSimOperatorBridge::clearPendingFault()
{
    _pendingFault.clear();
    setStatus(QStringLiteral("fault_cleared"), QStringLiteral("已清除待应用故障"));
}

void MoSimOperatorBridge::copyStagedFaultCommand()
{
    if (_pendingFault.isEmpty()) {
        setStatus(QStringLiteral("fault_not_staged"), QStringLiteral("请先暂存故障参数"));
        return;
    }
    const QString runDirectory = activeRunDirectory();
    if (runDirectory.isEmpty() || _runManifest.isEmpty()) {
        setStatus(QStringLiteral("active_run_missing"), QStringLiteral("故障命令需要当前 RunManifest"));
        return;
    }
    QStringList command {
        QStringLiteral("python"),
        QStringLiteral("\"%1\"").arg(nativePath(projectPath(QStringLiteral("Scripts/ui/write_operator_fault_request.py")))),
        QStringLiteral("--run-dir"), QStringLiteral("\"%1\"").arg(nativePath(runDirectory)),
        QStringLiteral("--target"), _pendingFault.value(QStringLiteral("target")).toString(),
        QStringLiteral("--vehicle-id"), _pendingFault.value(QStringLiteral("vehicle_id")).toString(),
        QStringLiteral("--value"), decimalText(_pendingFault.value(QStringLiteral("value")).toDouble()),
        QStringLiteral("--apply-mode"), QStringLiteral("set"),
        QStringLiteral("--restore-policy"), QStringLiteral("manual"),
    };
    if (_pendingFault.contains(QStringLiteral("rotor_index"))) {
        command << QStringLiteral("--rotor-index") << QString::number(_pendingFault.value(QStringLiteral("rotor_index")).toInt());
    }
    copyCommand(command.join(QLatin1Char(' ')), QStringLiteral("故障应用命令"));
}

void MoSimOperatorBridge::copyRestoreNormalCommand(const QString &vehicleId)
{
    const QString runDirectory = activeRunDirectory();
    if (vehicleId.isEmpty() || runDirectory.isEmpty() || _runManifest.isEmpty()) {
        setStatus(QStringLiteral("active_run_missing"), QStringLiteral("恢复命令需要当前 RunManifest 和目标飞机"));
        return;
    }
    const QString command = QStringLiteral("python \"%1\" --run-dir \"%2\" --restore-normal --vehicle-id %3")
        .arg(nativePath(projectPath(QStringLiteral("Scripts/ui/write_operator_fault_request.py"))),
             nativePath(runDirectory), vehicleId);
    copyCommand(command, QStringLiteral("恢复正常命令"));
}

void MoSimOperatorBridge::copyRosbagReplayCommand()
{
    const QString runDirectory = activeRunDirectory();
    if (runDirectory.isEmpty() || _runManifest.isEmpty()) {
        setStatus(QStringLiteral("active_run_missing"), QStringLiteral("回放命令需要当前 RunManifest"));
        return;
    }
    const QString command = QStringLiteral(
        "python \"%1\" --run-dir \"%2\" --manifest \"%2\\RUN_MANIFEST.json\" "
        "--bag \"C:\\path\\to\\run.bag\" --odom-topic \"uav1=/uav1/mavros/local_position/odom\" "
        "--coordinate-evidence \"C:\\path\\to\\coordinate_evidence.json\"")
        .arg(nativePath(projectPath(QStringLiteral("Scripts/ui/replay_rosbag_operator_map.py"))), nativePath(runDirectory));
    copyCommand(command, QStringLiteral("rosbag 回放命令"));
}

void MoSimOperatorBridge::copyLastCommand()
{
    copyCommand(_lastCommand, QStringLiteral("当前命令"));
}
