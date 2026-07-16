#include "MoSimOrchestratorBridge.h"

#include <QtCore/QDir>
#include <QtCore/QFileInfo>
#include <QtCore/QJsonDocument>
#include <QtCore/QJsonObject>
#include <QtCore/QProcessEnvironment>

MoSimOrchestratorBridge::MoSimOrchestratorBridge(QObject *parent)
    : QObject(parent)
    , _projectRoot(discoverProjectRoot())
{
    _process.setProcessChannelMode(QProcess::SeparateChannels);
    connect(&_process, &QProcess::started, this, &MoSimOrchestratorBridge::busyChanged);
    connect(&_process, qOverload<int, QProcess::ExitStatus>(&QProcess::finished),
            this, &MoSimOrchestratorBridge::processFinished);
    connect(&_process, &QProcess::errorOccurred, this, [this](QProcess::ProcessError error) {
        if (error == QProcess::FailedToStart) {
            finishWithError(QStringLiteral("orchestrator_client_start_failed"), _process.errorString());
        }
    });
    _timeout.setSingleShot(true);
    _timeout.setInterval(6000);
    connect(&_timeout, &QTimer::timeout, this, [this]() {
        _process.kill();
        finishWithError(QStringLiteral("orchestrator_client_timeout"));
    });
}

QString MoSimOrchestratorBridge::discoverProjectRoot() const
{
    const QString configured = qEnvironmentVariable("MOSIM_PROJECT_ROOT");
    if (!configured.isEmpty()) {
        return QDir(configured).absolutePath();
    }
    QDir candidate(QDir::currentPath());
    for (int depth = 0; depth < 8; ++depth) {
        if (candidate.exists(QStringLiteral("AGENTS.md")) &&
            candidate.exists(QStringLiteral("Scripts/ui/orchestrator_client.py"))) {
            return candidate.absolutePath();
        }
        if (!candidate.cdUp()) {
            break;
        }
    }
    return QStringLiteral("C:/Users/HP/Desktop/MoSim");
}

void MoSimOrchestratorBridge::invoke(const QStringList &arguments)
{
    if (busy()) {
        finishWithError(QStringLiteral("orchestrator_client_busy"));
        return;
    }
    const QString script = QDir(_projectRoot).filePath(QStringLiteral("Scripts/ui/orchestrator_client.py"));
    if (!QFileInfo::exists(script)) {
        finishWithError(QStringLiteral("orchestrator_client_missing"), script);
        return;
    }
    const QString python = qEnvironmentVariable("MOSIM_PYTHON", QStringLiteral("python"));
    QStringList complete{script};
    complete.append(arguments);
    complete << QStringLiteral("--format") << QStringLiteral("json");
    _statusText = QStringLiteral("Request pending");
    _reasonCode = QStringLiteral("request_pending");
    emit responseChanged();
    _process.setWorkingDirectory(_projectRoot);
    _process.start(python, complete);
    _timeout.start();
}

void MoSimOrchestratorBridge::invokeRunAction(const QString &action, const QStringList &extra)
{
    if (_runId.isEmpty()) {
        finishWithError(QStringLiteral("active_run_missing"));
        return;
    }
    QStringList arguments{action, QStringLiteral("--run-id"), _runId};
    arguments.append(extra);
    invoke(arguments);
}

void MoSimOrchestratorBridge::prepareRun(const QString &profilePath, const QString &controllerId,
                                         int vehicleCount, double windSpeedMps)
{
    invoke({QStringLiteral("prepare_run"), QStringLiteral("--profile-path"), profilePath,
            QStringLiteral("--controller-id"), controllerId, QStringLiteral("--vehicle-count"),
            QString::number(vehicleCount), QStringLiteral("--wind-speed-mps"), QString::number(windSpeedMps)});
}

void MoSimOrchestratorBridge::startRun() { invokeRunAction(QStringLiteral("start_run")); }
void MoSimOrchestratorBridge::stopRun() { invokeRunAction(QStringLiteral("stop_run")); }
void MoSimOrchestratorBridge::resetRun() { invokeRunAction(QStringLiteral("reset_run")); }
void MoSimOrchestratorBridge::refreshState() { invokeRunAction(QStringLiteral("get_run_state")); }
void MoSimOrchestratorBridge::refreshTelemetry() { invokeRunAction(QStringLiteral("get_telemetry")); }
void MoSimOrchestratorBridge::openModelContext() { invokeRunAction(QStringLiteral("open_model_context")); }
void MoSimOrchestratorBridge::getResultPacket() { invokeRunAction(QStringLiteral("get_result_packet")); }

void MoSimOrchestratorBridge::applyWind(double value)
{
    invokeRunAction(QStringLiteral("apply_injection"),
                    {QStringLiteral("--target"), QStringLiteral("wind_speed_mps"),
                     QStringLiteral("--value"), QString::number(value)});
}

void MoSimOrchestratorBridge::applyMotorEffectiveness(int rotorIndex, double value)
{
    invokeRunAction(QStringLiteral("apply_injection"),
                    {QStringLiteral("--target"), QStringLiteral("motor_effectiveness"),
                     QStringLiteral("--rotor-index"), QString::number(rotorIndex),
                     QStringLiteral("--value"), QString::number(value)});
}

void MoSimOrchestratorBridge::restoreInjection(const QString &target, int rotorIndex)
{
    QStringList extra{QStringLiteral("--target"), target, QStringLiteral("--value"), QStringLiteral("0")};
    if (rotorIndex > 0) {
        extra << QStringLiteral("--rotor-index") << QString::number(rotorIndex);
    }
    invokeRunAction(QStringLiteral("restore_injection"), extra);
}

void MoSimOrchestratorBridge::prepareDisplays(const QStringList &displays)
{
    QStringList extra;
    for (const QString &display : displays) {
        extra << QStringLiteral("--display") << display;
    }
    invokeRunAction(QStringLiteral("prepare_display_session"), extra);
}

void MoSimOrchestratorBridge::finishWithError(const QString &reason, const QString &detail)
{
    _timeout.stop();
    _accepted = false;
    _reasonCode = reason;
    _statusText = detail.isEmpty() ? reason : reason + QStringLiteral(": ") + detail;
    _lastResponse = _statusText;
    emit responseChanged();
    emit busyChanged();
}

void MoSimOrchestratorBridge::processFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    Q_UNUSED(exitCode)
    _timeout.stop();
    const QByteArray output = _process.readAllStandardOutput();
    QJsonParseError parseError;
    const QJsonDocument document = QJsonDocument::fromJson(output, &parseError);
    if (exitStatus != QProcess::NormalExit || !document.isObject()) {
        finishWithError(QStringLiteral("orchestrator_response_invalid"),
                        parseError.errorString() + QString::fromUtf8(_process.readAllStandardError()));
        return;
    }
    const QJsonObject response = document.object();
    _accepted = response.value(QStringLiteral("accepted")).toBool(false);
    _reasonCode = response.value(QStringLiteral("reason_code")).toString(QStringLiteral("unknown"));
    _runId = response.value(QStringLiteral("run_id")).toString(_runId);
    _profileHash = response.value(QStringLiteral("profile_hash")).toString(_profileHash);
    const QJsonObject manifest = response.value(QStringLiteral("manifest")).toObject();
    if (!manifest.isEmpty()) {
        _lifecycleState = manifest.value(QStringLiteral("lifecycle_state")).toString(_lifecycleState);
    }
    _statusText = (_accepted ? QStringLiteral("Accepted: ") : QStringLiteral("Rejected: ")) + _reasonCode;
    _lastResponse = QString::fromUtf8(document.toJson(QJsonDocument::Indented));
    emit responseChanged();
    emit busyChanged();
}
