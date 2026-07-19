#include "MoSimOrchestratorBridge.h"

#include <QtCore/QDir>
#include <QtCore/QFileInfo>
#include <QtCore/QFile>
#include <QtCore/QSaveFile>
#include <QtCore/QDateTime>
#include <QtCore/QJsonDocument>
#include <QtCore/QJsonArray>
#include <QtCore/QJsonObject>
#include <QtCore/QProcessEnvironment>
#include <QtGui/QWindow>

#include "Comms/LinkInterface.h"
#include "Comms/LinkManager.h"
#include "Comms/MAVLinkProtocol.h"
#include "Vehicle/MultiVehicleManager.h"
#include "Vehicle/Vehicle.h"

#ifdef Q_OS_WIN
#include <qt_windows.h>

namespace {
struct UnrealWindowSearch
{
    DWORD processId = 0;
    HWND bestWindow = nullptr;
    qint64 bestArea = 0;
    HWND fallbackWindow = nullptr;
    qint64 fallbackArea = 0;
    HWND hiddenWindow = nullptr;
    qint64 hiddenArea = 0;
    int matchingWindows = 0;
    int visibleWindows = 0;
    int ownedWindows = 0;
    int minimizedWindows = 0;
};

BOOL CALLBACK findLargestVisibleWindow(HWND window, LPARAM contextValue)
{
    auto *context = reinterpret_cast<UnrealWindowSearch *>(contextValue);
    DWORD processId = 0;
    GetWindowThreadProcessId(window, &processId);
    if (processId != context->processId) {
        return TRUE;
    }
    ++context->matchingWindows;
    RECT client{};
    if (!GetClientRect(window, &client)) {
        return TRUE;
    }
    const qint64 area = qint64(client.right - client.left) * qint64(client.bottom - client.top);
    if (!IsWindowVisible(window)) {
        if (area > context->hiddenArea) {
            context->hiddenArea = area;
            context->hiddenWindow = window;
        }
        return TRUE;
    }
    ++context->visibleWindows;
    if (IsIconic(window)) {
        ++context->minimizedWindows;
        return TRUE;
    }
    if (area > context->fallbackArea) {
        context->fallbackArea = area;
        context->fallbackWindow = window;
    }
    if (GetWindow(window, GW_OWNER) != nullptr) {
        ++context->ownedWindows;
        return TRUE;
    }
    if (area > context->bestArea) {
        context->bestArea = area;
        context->bestWindow = window;
    }
    return TRUE;
}
}
#endif

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
    _operationPoll.setInterval(750);
    connect(&_operationPoll, &QTimer::timeout, this, [this]() {
        if (!busy() && !_runId.isEmpty() && !_operationId.isEmpty() && _operationState == QStringLiteral("running")) {
            invokeRunAction(QStringLiteral("get_operation_progress"),
                            {QStringLiteral("--operation-id"), _operationId});
        }
    });
    _unrealDiscovery.setInterval(500);
    connect(&_unrealDiscovery, &QTimer::timeout, this, &MoSimOrchestratorBridge::discoverUnrealWindow);
    _qgcObservability.setInterval(500);
    connect(&_qgcObservability, &QTimer::timeout, this, &MoSimOrchestratorBridge::writeQgcObservability);
    connect(MAVLinkProtocol::instance(), &MAVLinkProtocol::messageReceived, this,
            [this](LinkInterface *, const mavlink_message_t &message) {
                ++_qgcMessagesWindow;
                ++_qgcMessagesTotal;
                if (message.msgid == MAVLINK_MSG_ID_HEARTBEAT) {
                    ++_qgcHeartbeatsWindow;
                    ++_qgcHeartbeatsTotal;
                }
            });
    _qgcMetricWindow.start();
    _qgcObservability.start();
    loadOperatorMap();
    recoverRunIdentity();
    QTimer::singleShot(0, this, &MoSimOrchestratorBridge::refreshControllers);
}

MoSimOrchestratorBridge::~MoSimOrchestratorBridge()
{
    resetUnrealWindowRegion();
}

void MoSimOrchestratorBridge::loadOperatorMap()
{
    const QString catalogPath = QDir(_projectRoot).filePath(
        QStringLiteral("Config/control_platform/operator_map_catalog.json"));
    QFile catalogFile(catalogPath);
    if (!catalogFile.open(QIODevice::ReadOnly)) {
        return;
    }
    const QJsonDocument document = QJsonDocument::fromJson(catalogFile.readAll());
    if (!document.isObject()) {
        return;
    }
    const QJsonArray maps = document.object().value(QStringLiteral("maps")).toArray();
    for (const QJsonValue &value : maps) {
        const QJsonObject map = value.toObject();
        if (map.value(QStringLiteral("enabled")).toBool(false)) {
            _operatorMap = map.toVariantMap();
            return;
        }
    }
}

void MoSimOrchestratorBridge::recoverRunIdentity()
{
    const QString activePath = QDir(_projectRoot).filePath(
        QStringLiteral("Results/ui_platform/model_studio_active_run.json"));
    QFile activeFile(activePath);
    if (!activeFile.open(QIODevice::ReadOnly)) {
        return;
    }
    const QJsonDocument document = QJsonDocument::fromJson(activeFile.readAll());
    if (!document.isObject()) {
        return;
    }
    const QJsonObject active = document.object();
    _runId = active.value(QStringLiteral("run_id")).toString();
    _profileHash = active.value(QStringLiteral("profile_hash")).toString();
    _startupRunRecoveryPending = !_runId.isEmpty();
}

void MoSimOrchestratorBridge::resetQgcObservability(const QString &runId)
{
    _qgcMetricRunId = runId;
    _qgcRxBytesWindow = 0;
    _qgcTxBytesWindow = 0;
    _qgcMessagesWindow = 0;
    _qgcHeartbeatsWindow = 0;
    _qgcRxBytesTotal = 0;
    _qgcTxBytesTotal = 0;
    _qgcMessagesTotal = 0;
    _qgcHeartbeatsTotal = 0;
    _qgcMetricWindow.restart();
}

void MoSimOrchestratorBridge::attachQgcLinks()
{
    const QList<SharedLinkInterfacePtr> links = LinkManager::instance()->links();
    for (const SharedLinkInterfacePtr &sharedLink : links) {
        LinkInterface *link = sharedLink.get();
        if (!link || _observedQgcLinks.contains(link)) {
            continue;
        }
        _observedQgcLinks.insert(link);
        connect(link, &LinkInterface::bytesReceived, this,
                [this](LinkInterface *, const QByteArray &data) {
                    _qgcRxBytesWindow += static_cast<quint64>(data.size());
                    _qgcRxBytesTotal += static_cast<quint64>(data.size());
                });
        connect(link, &LinkInterface::bytesSent, this,
                [this](LinkInterface *, const QByteArray &data) {
                    _qgcTxBytesWindow += static_cast<quint64>(data.size());
                    _qgcTxBytesTotal += static_cast<quint64>(data.size());
                });
        connect(link, &QObject::destroyed, this, [this, link]() { _observedQgcLinks.remove(link); });
    }
}

void MoSimOrchestratorBridge::writeQgcObservability()
{
    attachQgcLinks();
    if (_runId.isEmpty()) {
        return;
    }
    if (_qgcMetricRunId != _runId) {
        resetQgcObservability(_runId);
        return;
    }

    const double windowSeconds = qMax(0.001, _qgcMetricWindow.elapsed() / 1000.0);
    Vehicle *vehicle = MultiVehicleManager::instance()->activeVehicle();
    QJsonObject vehicleCounters{
        {QStringLiteral("state"), vehicle ? QStringLiteral("available") : QStringLiteral("unavailable")},
    };
    if (vehicle) {
        vehicleCounters.insert(QStringLiteral("vehicle_id"), vehicle->id());
        vehicleCounters.insert(QStringLiteral("messages_received"), static_cast<qint64>(vehicle->messagesReceived()));
        vehicleCounters.insert(QStringLiteral("messages_lost"), static_cast<qint64>(vehicle->messagesLost()));
        vehicleCounters.insert(QStringLiteral("mavlink_loss_percent"), vehicle->mavlinkLossPercent());
    } else {
        vehicleCounters.insert(QStringLiteral("reason"), QStringLiteral("active_vehicle_unavailable"));
    }

    const QJsonObject metric{
        {QStringLiteral("schema"), QStringLiteral("mosim.qgc_mavlink_observability.v1")},
        {QStringLiteral("run_id"), _runId},
        {QStringLiteral("state"), QStringLiteral("available")},
        {QStringLiteral("window_s"), windowSeconds},
        {QStringLiteral("telemetry_message_rate_hz"), _qgcMessagesWindow / windowSeconds},
        {QStringLiteral("heartbeat_rate_hz"), _qgcHeartbeatsWindow / windowSeconds},
        {QStringLiteral("rx_transport_bytes_per_s"), _qgcRxBytesWindow / windowSeconds},
        {QStringLiteral("tx_transport_bytes_per_s"), _qgcTxBytesWindow / windowSeconds},
        {QStringLiteral("messages_observed_total"), static_cast<qint64>(_qgcMessagesTotal)},
        {QStringLiteral("heartbeats_observed_total"), static_cast<qint64>(_qgcHeartbeatsTotal)},
        {QStringLiteral("rx_transport_bytes_total"), static_cast<qint64>(_qgcRxBytesTotal)},
        {QStringLiteral("tx_transport_bytes_total"), static_cast<qint64>(_qgcTxBytesTotal)},
        {QStringLiteral("connected_link_count"), LinkManager::instance()->links().size()},
        {QStringLiteral("vehicle_counters"), vehicleCounters},
        {QStringLiteral("rtt_ms"), QJsonObject{{QStringLiteral("state"), QStringLiteral("unavailable")},
                                                {QStringLiteral("reason"), QStringLiteral("no_correlated_qgc_ping_measurement")}}},
        {QStringLiteral("ui_fps"), QJsonObject{{QStringLiteral("state"), QStringLiteral("unavailable")},
                                                {QStringLiteral("reason"), QStringLiteral("qt_quick_render_instrumentation_not_attached")}}},
        {QStringLiteral("claim_boundary"), QStringLiteral("Transport byte counters include MAVLink framing but not inferred UDP/IP overhead.")},
        {QStringLiteral("updated_at_unix"), QDateTime::currentMSecsSinceEpoch() / 1000.0},
    };

    const QString outputPath = QDir(_projectRoot).filePath(
        QStringLiteral("Results/ui_platform/orchestrator_runs/%1/observability/mavlink_qgc.json").arg(_runId));
    QDir().mkpath(QFileInfo(outputPath).absolutePath());
    QSaveFile output(outputPath);
    if (output.open(QIODevice::WriteOnly | QIODevice::Text)) {
        output.write(QJsonDocument(metric).toJson(QJsonDocument::Indented));
        output.commit();
    }
    _qgcRxBytesWindow = 0;
    _qgcTxBytesWindow = 0;
    _qgcMessagesWindow = 0;
    _qgcHeartbeatsWindow = 0;
    _qgcMetricWindow.restart();
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
    _pendingAction = arguments.value(0);
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
                                         int vehicleCount, double windSpeedMps, bool manualControl)
{
    invoke({QStringLiteral("prepare_run"), QStringLiteral("--profile-path"), profilePath,
            QStringLiteral("--controller-id"), controllerId, QStringLiteral("--vehicle-count"),
            QString::number(vehicleCount), QStringLiteral("--wind-speed-mps"), QString::number(windSpeedMps),
            QStringLiteral("--manual-control"), manualControl ? QStringLiteral("true") : QStringLiteral("false")});
}

void MoSimOrchestratorBridge::writeManualControl(bool enabled, double forwardMps, double lateralMps)
{
    const QString path = QDir(_projectRoot).filePath(
        QStringLiteral("Results/ui_platform/manual_control/manual_control.json"));
    QDir().mkpath(QFileInfo(path).absolutePath());
    QJsonObject payload;
    payload.insert(QStringLiteral("schema"), QStringLiteral("mosim.manual_velocity_command.v1"));
    payload.insert(QStringLiteral("run_id"), _runId);
    payload.insert(QStringLiteral("enabled"), enabled);
    payload.insert(QStringLiteral("forward_mps"), qBound(-0.5, forwardMps, 0.5));
    payload.insert(QStringLiteral("lateral_mps"), qBound(-0.5, lateralMps, 0.5));
    payload.insert(QStringLiteral("timestamp_s"), QDateTime::currentMSecsSinceEpoch() / 1000.0);
    QSaveFile file(path);
    if (file.open(QIODevice::WriteOnly)) {
        file.write(QJsonDocument(payload).toJson(QJsonDocument::Compact));
        file.commit();
    }
}

void MoSimOrchestratorBridge::setManualControlEnabled(bool enabled)
{
    writeManualControl(enabled, 0.0, 0.0);
}

void MoSimOrchestratorBridge::updateManualVelocity(double forwardMps, double lateralMps)
{
    writeManualControl(true, forwardMps, lateralMps);
}

void MoSimOrchestratorBridge::startRun() { invokeRunAction(QStringLiteral("start_run")); }
void MoSimOrchestratorBridge::requestSafeStop() { invokeRunAction(QStringLiteral("request_safe_stop")); }
void MoSimOrchestratorBridge::stopRun() { invokeRunAction(QStringLiteral("stop_run")); }
void MoSimOrchestratorBridge::resetRun() { invokeRunAction(QStringLiteral("reset_run")); }
void MoSimOrchestratorBridge::refreshState() { invokeRunAction(QStringLiteral("get_run_state")); }
void MoSimOrchestratorBridge::refreshTelemetry() { invokeRunAction(QStringLiteral("get_telemetry")); }
void MoSimOrchestratorBridge::openModelContext() { invokeRunAction(QStringLiteral("open_model_context")); }
void MoSimOrchestratorBridge::getResultPacket() { invokeRunAction(QStringLiteral("get_result_packet")); }

void MoSimOrchestratorBridge::applyWind(const QString &vehicleId, double value)
{
    invokeRunAction(QStringLiteral("apply_injection"),
                    {QStringLiteral("--target"), QStringLiteral("wind_speed_mps"),
                     QStringLiteral("--vehicle-id"), vehicleId,
                     QStringLiteral("--value"), QString::number(value)});
}

void MoSimOrchestratorBridge::applyMotorEffectiveness(const QString &vehicleId, int rotorIndex, double value)
{
    invokeRunAction(QStringLiteral("apply_injection"),
                    {QStringLiteral("--target"), QStringLiteral("motor_effectiveness"),
                     QStringLiteral("--vehicle-id"), vehicleId,
                     QStringLiteral("--rotor-index"), QString::number(rotorIndex),
                     QStringLiteral("--value"), QString::number(value)});
}

void MoSimOrchestratorBridge::restoreInjection(const QString &vehicleId, const QString &target, int rotorIndex)
{
    QStringList extra{QStringLiteral("--target"), target, QStringLiteral("--vehicle-id"), vehicleId,
                      QStringLiteral("--value"), QStringLiteral("0")};
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

void MoSimOrchestratorBridge::attachDisplays()
{
    if (_displaySessionId.isEmpty()) {
        finishWithError(QStringLiteral("display_session_missing"));
        return;
    }
    invoke({QStringLiteral("attach_display"), QStringLiteral("--session-id"), _displaySessionId});
}

void MoSimOrchestratorBridge::detachDisplays()
{
    if (_displaySessionId.isEmpty()) {
        finishWithError(QStringLiteral("display_session_missing"));
        return;
    }
    invoke({QStringLiteral("detach_display"), QStringLiteral("--session-id"), _displaySessionId});
}

void MoSimOrchestratorBridge::refreshControllers() { invoke({QStringLiteral("list_controllers")}); }
void MoSimOrchestratorBridge::closeAllRviz() { invokeRunAction(QStringLiteral("close_all_rviz")); }
void MoSimOrchestratorBridge::startUeRecording() { invokeRunAction(QStringLiteral("start_ue_recording")); }
void MoSimOrchestratorBridge::stopUeRecording() { invokeRunAction(QStringLiteral("stop_ue_recording")); }

void MoSimOrchestratorBridge::refreshUnrealEmbedding()
{
    if (_runId.isEmpty() || _displaySessionId.isEmpty()) {
        clearUnrealWindow(QStringLiteral("not_attached"), QStringLiteral("display_session_missing"));
        return;
    }
    _unrealDiscoveryAttempt = 0;
    _unrealEmbedState = QStringLiteral("waiting_for_window");
    _unrealEmbedReason.clear();
    emit unrealWindowChanged();
    discoverUnrealWindow();
    if (_unrealWindow == nullptr) {
        _unrealDiscovery.start();
    }
}

void MoSimOrchestratorBridge::confirmUnrealContainerReady()
{
#ifdef Q_OS_WIN
    if (_unrealWindow == nullptr) {
        return;
    }
    const HWND window = reinterpret_cast<HWND>(static_cast<quintptr>(_unrealWindow->winId()));
    if (!IsWindow(window)) {
        clearUnrealWindow(QStringLiteral("blocked"), QStringLiteral("unreal_window_invalid_after_wrap"));
        return;
    }

    // WindowContainer reparents the foreign HWND asynchronously. Showing it
    // before that happens is exactly the standalone-window flash this gate
    // prevents.
    if (GetParent(window) == nullptr && _unrealContainerReadyAttempt < 200) {
        ++_unrealContainerReadyAttempt;
        QTimer::singleShot(50, this, &MoSimOrchestratorBridge::confirmUnrealContainerReady);
        return;
    }
    if (GetParent(window) == nullptr) {
        _unrealEmbedState = QStringLiteral("blocked");
        _unrealEmbedReason = QStringLiteral("unreal_container_parent_timeout");
        emit unrealWindowChanged();
        return;
    }
    ShowWindow(window, _unrealPresentationSuppressed ? SW_HIDE : SW_SHOWNA);
    _unrealContainerReadyAttempt = 0;
    _unrealEmbedState = QStringLiteral("embedded");
    _unrealEmbedReason.clear();
    emit unrealWindowChanged();
#endif
}

void MoSimOrchestratorBridge::setUnrealPresentationSuppressed(bool suppressed)
{
    _unrealPresentationSuppressed = suppressed;
#ifdef Q_OS_WIN
    if (_unrealWindow == nullptr) {
        return;
    }
    const HWND window = reinterpret_cast<HWND>(static_cast<quintptr>(_unrealWindow->winId()));
    if (!IsWindow(window)) {
        return;
    }
    if (suppressed) {
        ShowWindow(window, SW_HIDE);
    } else if (GetParent(window) != nullptr) {
        ShowWindow(window, SW_SHOWNA);
    }
#endif
}

void MoSimOrchestratorBridge::cycleUnrealView() { postUnrealKey(0x51); }
void MoSimOrchestratorBridge::zoomUnrealIn() { postUnrealKey(0xBB); }
void MoSimOrchestratorBridge::zoomUnrealOut() { postUnrealKey(0xBD); }

void MoSimOrchestratorBridge::orbitUnreal(double deltaX, double deltaY)
{
    // QML receives mouse deltas from the overlay while UE is a native child
    // window. Use a one-pixel accumulator so short drag events are not lost.
    constexpr double PixelsPerNudge = 1.0;
    constexpr int MaxNudgesPerEvent = 16;
    _unrealOrbitRemainderX += qBound(-64.0, deltaX, 64.0);
    _unrealOrbitRemainderY += qBound(-64.0, deltaY, 64.0);

    int nudgeCount = 0;
    while (qAbs(_unrealOrbitRemainderX) >= PixelsPerNudge && nudgeCount < MaxNudgesPerEvent) {
        const bool dragRight = _unrealOrbitRemainderX > 0.0;
        postUnrealKey(dragRight ? 0x7D : 0x7C); // F14 / F13
        _unrealOrbitRemainderX += dragRight ? -PixelsPerNudge : PixelsPerNudge;
        ++nudgeCount;
    }
    while (qAbs(_unrealOrbitRemainderY) >= PixelsPerNudge && nudgeCount < MaxNudgesPerEvent) {
        const bool dragDown = _unrealOrbitRemainderY > 0.0;
        postUnrealKey(dragDown ? 0x7F : 0x7E); // F16 / F15
        _unrealOrbitRemainderY += dragDown ? -PixelsPerNudge : PixelsPerNudge;
        ++nudgeCount;
    }
}

void MoSimOrchestratorBridge::setUnrealOverlayHole(double x, double y, double width, double height,
                                                    double surfaceWidth, double surfaceHeight, bool enabled)
{
#ifdef Q_OS_WIN
    if (_unrealWindow == nullptr) {
        return;
    }
    const HWND window = reinterpret_cast<HWND>(static_cast<quintptr>(_unrealWindow->winId()));
    if (!IsWindow(window)) {
        return;
    }
    if (!enabled || width <= 0.0 || height <= 0.0 || surfaceWidth <= 0.0 || surfaceHeight <= 0.0) {
        resetUnrealWindowRegion();
        return;
    }

    RECT client{};
    if (!GetClientRect(window, &client)) {
        return;
    }
    const int clientWidth = client.right - client.left;
    const int clientHeight = client.bottom - client.top;
    if (clientWidth <= 0 || clientHeight <= 0) {
        return;
    }

    const double scaleX = double(clientWidth) / surfaceWidth;
    const double scaleY = double(clientHeight) / surfaceHeight;
    const int holeLeft = qBound(0, qRound(x * scaleX), clientWidth);
    const int holeTop = qBound(0, qRound(y * scaleY), clientHeight);
    const int holeRight = qBound(holeLeft, qRound((x + width) * scaleX), clientWidth);
    const int holeBottom = qBound(holeTop, qRound((y + height) * scaleY), clientHeight);

    HRGN visibleRegion = CreateRectRgn(0, 0, clientWidth, clientHeight);
    HRGN overlayHole = CreateRectRgn(holeLeft, holeTop, holeRight, holeBottom);
    if (visibleRegion == nullptr || overlayHole == nullptr) {
        if (visibleRegion != nullptr) {
            DeleteObject(visibleRegion);
        }
        if (overlayHole != nullptr) {
            DeleteObject(overlayHole);
        }
        return;
    }
    CombineRgn(visibleRegion, visibleRegion, overlayHole, RGN_DIFF);
    DeleteObject(overlayHole);
    if (SetWindowRgn(window, visibleRegion, TRUE) == 0) {
        DeleteObject(visibleRegion);
    }
#else
    Q_UNUSED(x);
    Q_UNUSED(y);
    Q_UNUSED(width);
    Q_UNUSED(height);
    Q_UNUSED(surfaceWidth);
    Q_UNUSED(surfaceHeight);
    Q_UNUSED(enabled);
#endif
}

void MoSimOrchestratorBridge::resetUnrealWindowRegion()
{
#ifdef Q_OS_WIN
    if (_unrealWindow == nullptr) {
        return;
    }
    const HWND window = reinterpret_cast<HWND>(static_cast<quintptr>(_unrealWindow->winId()));
    if (IsWindow(window)) {
        SetWindowRgn(window, nullptr, TRUE);
    }
#endif
}

void MoSimOrchestratorBridge::postUnrealKey(int virtualKey)
{
#ifdef Q_OS_WIN
    if (_unrealWindow == nullptr) {
        return;
    }
    const HWND window = reinterpret_cast<HWND>(static_cast<quintptr>(_unrealWindow->winId()));
    PostMessage(window, WM_KEYDOWN, static_cast<WPARAM>(virtualKey), 0);
    PostMessage(window, WM_KEYUP, static_cast<WPARAM>(virtualKey), 0);
#else
    Q_UNUSED(virtualKey);
#endif
}

void MoSimOrchestratorBridge::clearUnrealWindow(const QString &state, const QString &reason)
{
    _unrealDiscovery.stop();
    QWindow *oldWindow = _unrealWindow;
    resetUnrealWindowRegion();
    _unrealWindow = nullptr;
    _unrealEmbedState = state;
    _unrealEmbedReason = reason;
    emit unrealWindowChanged();
    if (oldWindow != nullptr) {
        oldWindow->deleteLater();
    }
}

void MoSimOrchestratorBridge::discoverUnrealWindow()
{
#ifndef Q_OS_WIN
    clearUnrealWindow(QStringLiteral("unsupported"), QStringLiteral("native_embedding_requires_windows"));
#else
    const QString processPath = QDir(_projectRoot).filePath(
        QStringLiteral("Results/ui_platform/orchestrator_runs/%1/displays/%2/DISPLAY_PROCESSES.json")
            .arg(_runId, _displaySessionId));
    QFile processFile(processPath);
    qint64 unrealProcessId = 0;
    if (processFile.open(QIODevice::ReadOnly)) {
        const QJsonDocument processDocument = QJsonDocument::fromJson(processFile.readAll());
        QJsonArray records;
        if (processDocument.isArray()) {
            records = processDocument.array();
        } else if (processDocument.isObject()) {
            records.append(processDocument.object());
        }
        for (const QJsonValue &value : records) {
            const QJsonObject record = value.toObject();
            if (record.value(QStringLiteral("kind")).toString() == QStringLiteral("unreal")) {
                unrealProcessId = record.value(QStringLiteral("pid")).toInteger();
                break;
            }
        }
    }

    UnrealWindowSearch search;
    search.processId = static_cast<DWORD>(unrealProcessId);
    if (search.processId != 0) {
        EnumWindows(findLargestVisibleWindow, reinterpret_cast<LPARAM>(&search));
        if (search.bestWindow == nullptr && search.fallbackWindow == nullptr) {
            EnumChildWindows(GetDesktopWindow(), findLargestVisibleWindow,
                             reinterpret_cast<LPARAM>(&search));
        }
    }
    if (search.bestWindow == nullptr) {
        search.bestWindow = search.fallbackWindow;
        search.bestArea = search.fallbackArea;
    }
    if (search.bestWindow == nullptr && search.hiddenWindow != nullptr && search.hiddenArea > 10000) {
        search.bestWindow = search.hiddenWindow;
        search.bestArea = search.hiddenArea;
    }
    if (search.bestWindow != nullptr) {
        const WId nativeId = static_cast<WId>(reinterpret_cast<quintptr>(search.bestWindow));
        if (_unrealWindow != nullptr && _unrealWindow->winId() == nativeId) {
            _unrealDiscovery.stop();
            return;
        }
        // Keep the native window hidden until QML's WindowContainer has
        // established the parent relationship.
        ShowWindow(search.bestWindow, SW_HIDE);
        _unrealContainerReadyAttempt = 0;
        clearUnrealWindow(QStringLiteral("attaching"));
        _unrealWindow = QWindow::fromWinId(nativeId);
        if (_unrealWindow == nullptr) {
            _unrealEmbedState = QStringLiteral("blocked");
            _unrealEmbedReason = QStringLiteral("foreign_window_wrapper_failed");
        } else {
            _unrealEmbedState = QStringLiteral("window_discovered_hidden");
            _unrealEmbedReason.clear();
        }
        emit unrealWindowChanged();
        return;
    }

    ++_unrealDiscoveryAttempt;
    const QString discoveryReason = unrealProcessId == 0
        ? QStringLiteral("unreal_process_pending")
        : QStringLiteral("unreal_window_pending_pid_%1_matches_%2_visible_%3_owned_%4_minimized_%5")
              .arg(unrealProcessId)
              .arg(search.matchingWindows)
              .arg(search.visibleWindows)
              .arg(search.ownedWindows)
              .arg(search.minimizedWindows);
    // A cold Unreal Editor launch can exceed one minute while shaders and
    // assets initialize. Keep discovery bounded, but do not time out before
    // the managed window is available.
    if (_unrealDiscoveryAttempt >= 360) {
        clearUnrealWindow(QStringLiteral("blocked"),
                          QStringLiteral("unreal_window_discovery_timeout:%1").arg(discoveryReason));
    } else if (_unrealEmbedState != QStringLiteral("waiting_for_window") ||
               _unrealEmbedReason != discoveryReason) {
        _unrealEmbedState = QStringLiteral("waiting_for_window");
        _unrealEmbedReason = discoveryReason;
        emit unrealWindowChanged();
    }
#endif
}

void MoSimOrchestratorBridge::finishWithError(const QString &reason, const QString &detail)
{
    _timeout.stop();
    _accepted = false;
    _reasonCode = reason;
    _statusText = detail.isEmpty() ? reason : reason + QStringLiteral(": ") + detail;
    _lastResponse = _statusText;
    _pendingAction.clear();
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
    const QString completedAction = _pendingAction;
    const QJsonObject response = document.object();
    _accepted = response.value(QStringLiteral("accepted")).toBool(false);
    _reasonCode = response.value(QStringLiteral("reason_code")).toString(QStringLiteral("unknown"));
    const QString previousRunId = _runId;
    _runId = response.value(QStringLiteral("run_id")).toString(_runId);
    if (_runId != previousRunId) {
        resetQgcObservability(_runId);
        _runtimeTelemetry.clear();
    }
    _profileHash = response.value(QStringLiteral("profile_hash")).toString(_profileHash);
    const QJsonObject manifest = response.value(QStringLiteral("manifest")).toObject();
    if (!manifest.isEmpty()) {
        _lifecycleState = manifest.value(QStringLiteral("lifecycle_state")).toString(_lifecycleState);
        _experimentProfileId = manifest.value(QStringLiteral("experiment_profile_id")).toString(_experimentProfileId);
        _selectedControllerId = manifest.value(QStringLiteral("controller_id")).toString(_selectedControllerId);
        _selectedVehicleCount = manifest.value(QStringLiteral("vehicle_count")).toInt(_selectedVehicleCount);
    }
    const QJsonObject session = response.value(QStringLiteral("session")).toObject();
    if (!session.isEmpty()) {
        _displaySessionId = session.value(QStringLiteral("session_id")).toString(_displaySessionId);
        const QJsonArray displays = session.value(QStringLiteral("displays")).toArray();
        bool includesUnreal = false;
        for (const QJsonValue &display : displays) {
            includesUnreal = includesUnreal || display.toString() == QStringLiteral("unreal");
        }
        const QString sessionState = session.value(QStringLiteral("state")).toString();
        if ((completedAction == QStringLiteral("attach_display") || completedAction == QStringLiteral("get_run_state"))
            && sessionState == QStringLiteral("attached") && includesUnreal && _accepted) {
            QTimer::singleShot(0, this, &MoSimOrchestratorBridge::refreshUnrealEmbedding);
        } else if (completedAction == QStringLiteral("detach_display") || sessionState == QStringLiteral("detached")) {
            clearUnrealWindow(QStringLiteral("not_attached"));
        }
    }
    const QJsonArray controllers = response.value(QStringLiteral("controllers")).toArray();
    if (!controllers.isEmpty() || _pendingAction == QStringLiteral("list_controllers")) {
        _controllers = controllers.toVariantList();
        _registryHash = response.value(QStringLiteral("registry_hash")).toString();
    }
    const QJsonObject operation = response.value(QStringLiteral("operation")).toObject();
    if (!operation.isEmpty()) {
        _operationId = operation.value(QStringLiteral("operation_id")).toString(_operationId);
        _operationState = operation.value(QStringLiteral("state")).toString(QStringLiteral("unknown"));
        _operationStage = operation.value(QStringLiteral("stage_label")).toString();
        _operationProgress = operation.value(QStringLiteral("progress_percent")).isDouble()
            ? operation.value(QStringLiteral("progress_percent")).toInt()
            : -1;
        _operationAttempt = operation.value(QStringLiteral("attempt")).toInt();
        _operationMaxAttempts = operation.value(QStringLiteral("max_attempts")).toInt();
        if (_operationState == QStringLiteral("running")) {
            _operationPoll.start();
        } else {
            _operationPoll.stop();
        }
    }
    const QJsonObject recording = response.value(QStringLiteral("recording")).toObject();
    if (!recording.isEmpty()) {
        _recordingActive = recording.value(QStringLiteral("active")).toBool(false);
        _recordingPath = recording.value(QStringLiteral("output_path")).toString(_recordingPath);
    }
    if (completedAction == QStringLiteral("get_telemetry")) {
        const QJsonObject telemetry = response.value(QStringLiteral("telemetry")).toObject();
        const QString telemetryRunId = telemetry.value(QStringLiteral("run_id")).toString();
        if (_accepted && !telemetry.isEmpty() && telemetryRunId == _runId) {
            _runtimeTelemetry = telemetry.toVariantMap();
        } else {
            _runtimeTelemetry.clear();
        }
    } else if (completedAction == QStringLiteral("reset_run") ||
               completedAction == QStringLiteral("stop_run")) {
        _runtimeTelemetry.clear();
    }
    _statusText = (_accepted ? QStringLiteral("Accepted: ") : QStringLiteral("Rejected: ")) + _reasonCode;
    _lastResponse = QString::fromUtf8(document.toJson(QJsonDocument::Indented));
    _pendingAction.clear();
    emit responseChanged();
    emit busyChanged();
    if (completedAction == QStringLiteral("list_controllers") && _startupRunRecoveryPending) {
        _startupRunRecoveryPending = false;
        QTimer::singleShot(0, this, [this]() {
            invoke({QStringLiteral("get_run_state"), QStringLiteral("--run-id"), _runId});
        });
    }
}
