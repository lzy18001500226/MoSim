#pragma once

#include <QtCore/QObject>
#include <QtCore/QElapsedTimer>
#include <QtCore/QProcess>
#include <QtCore/QSet>
#include <QtCore/QTimer>
#include <QtCore/QVariantList>
#include <QtGui/QWindow>

class MoSimOrchestratorBridge final : public QObject
{
    Q_OBJECT
    Q_PROPERTY(bool busy READ busy NOTIFY busyChanged)
    Q_PROPERTY(bool accepted READ accepted NOTIFY responseChanged)
    Q_PROPERTY(QString statusText READ statusText NOTIFY responseChanged)
    Q_PROPERTY(QString reasonCode READ reasonCode NOTIFY responseChanged)
    Q_PROPERTY(QString runId READ runId NOTIFY responseChanged)
    Q_PROPERTY(QString profileHash READ profileHash NOTIFY responseChanged)
    Q_PROPERTY(QString experimentProfileId READ experimentProfileId NOTIFY responseChanged)
    Q_PROPERTY(QString selectedControllerId READ selectedControllerId NOTIFY responseChanged)
    Q_PROPERTY(int selectedVehicleCount READ selectedVehicleCount NOTIFY responseChanged)
    Q_PROPERTY(QString lifecycleState READ lifecycleState NOTIFY responseChanged)
    Q_PROPERTY(QString displaySessionId READ displaySessionId NOTIFY responseChanged)
    Q_PROPERTY(QVariantList controllers READ controllers NOTIFY responseChanged)
    Q_PROPERTY(QString registryHash READ registryHash NOTIFY responseChanged)
    Q_PROPERTY(QString operationId READ operationId NOTIFY responseChanged)
    Q_PROPERTY(QString operationState READ operationState NOTIFY responseChanged)
    Q_PROPERTY(QString operationStage READ operationStage NOTIFY responseChanged)
    Q_PROPERTY(int operationProgress READ operationProgress NOTIFY responseChanged)
    Q_PROPERTY(int operationAttempt READ operationAttempt NOTIFY responseChanged)
    Q_PROPERTY(int operationMaxAttempts READ operationMaxAttempts NOTIFY responseChanged)
    Q_PROPERTY(bool recordingActive READ recordingActive NOTIFY responseChanged)
    Q_PROPERTY(QString recordingPath READ recordingPath NOTIFY responseChanged)
    Q_PROPERTY(QWindow *unrealWindow READ unrealWindow NOTIFY unrealWindowChanged)
    Q_PROPERTY(QString unrealEmbedState READ unrealEmbedState NOTIFY unrealWindowChanged)
    Q_PROPERTY(QString unrealEmbedReason READ unrealEmbedReason NOTIFY unrealWindowChanged)
    Q_PROPERTY(QVariantMap operatorMap READ operatorMap CONSTANT)
    Q_PROPERTY(QVariantMap runtimeTelemetry READ runtimeTelemetry NOTIFY responseChanged)
    Q_PROPERTY(QString lastResponse READ lastResponse NOTIFY responseChanged)

public:
    explicit MoSimOrchestratorBridge(QObject *parent = nullptr);
    ~MoSimOrchestratorBridge() override;

    bool busy() const { return _process.state() != QProcess::NotRunning; }
    bool accepted() const { return _accepted; }
    QString statusText() const { return _statusText; }
    QString reasonCode() const { return _reasonCode; }
    QString runId() const { return _runId; }
    QString profileHash() const { return _profileHash; }
    QString experimentProfileId() const { return _experimentProfileId; }
    QString selectedControllerId() const { return _selectedControllerId; }
    int selectedVehicleCount() const { return _selectedVehicleCount; }
    QString lifecycleState() const { return _lifecycleState; }
    QString displaySessionId() const { return _displaySessionId; }
    QVariantList controllers() const { return _controllers; }
    QString registryHash() const { return _registryHash; }
    QString operationId() const { return _operationId; }
    QString operationState() const { return _operationState; }
    QString operationStage() const { return _operationStage; }
    int operationProgress() const { return _operationProgress; }
    int operationAttempt() const { return _operationAttempt; }
    int operationMaxAttempts() const { return _operationMaxAttempts; }
    bool recordingActive() const { return _recordingActive; }
    QString recordingPath() const { return _recordingPath; }
    QWindow *unrealWindow() const { return _unrealWindow; }
    QString unrealEmbedState() const { return _unrealEmbedState; }
    QString unrealEmbedReason() const { return _unrealEmbedReason; }
    QVariantMap operatorMap() const { return _operatorMap; }
    QVariantMap runtimeTelemetry() const { return _runtimeTelemetry; }
    QString lastResponse() const { return _lastResponse; }

    Q_INVOKABLE void prepareRun(const QString &profilePath, const QString &controllerId, int vehicleCount,
                                double windSpeedMps, bool manualControl = false);
    Q_INVOKABLE void setManualControlEnabled(bool enabled);
    Q_INVOKABLE void updateManualVelocity(double forwardMps, double lateralMps);
    Q_INVOKABLE void startRun();
    Q_INVOKABLE void requestSafeStop();
    Q_INVOKABLE void stopRun();
    Q_INVOKABLE void resetRun();
    Q_INVOKABLE void refreshState();
    Q_INVOKABLE void refreshTelemetry();
    Q_INVOKABLE void openModelContext();
    Q_INVOKABLE void getResultPacket();
    Q_INVOKABLE void applyWind(const QString &vehicleId, double value);
    Q_INVOKABLE void applyMotorEffectiveness(const QString &vehicleId, int rotorIndex, double value);
    Q_INVOKABLE void restoreInjection(const QString &vehicleId, const QString &target, int rotorIndex = 0);
    Q_INVOKABLE void prepareDisplays(const QStringList &displays);
    Q_INVOKABLE void attachDisplays();
    Q_INVOKABLE void detachDisplays();
    Q_INVOKABLE void refreshControllers();
    Q_INVOKABLE void closeAllRviz();
    Q_INVOKABLE void startUeRecording();
    Q_INVOKABLE void stopUeRecording();
    Q_INVOKABLE void refreshUnrealEmbedding();
    Q_INVOKABLE void confirmUnrealContainerReady();
    Q_INVOKABLE void setUnrealPresentationSuppressed(bool suppressed);
    Q_INVOKABLE void cycleUnrealView();
    Q_INVOKABLE void zoomUnrealIn();
    Q_INVOKABLE void zoomUnrealOut();
    Q_INVOKABLE void orbitUnreal(double deltaX, double deltaY);
    Q_INVOKABLE void setUnrealOverlayHole(double x, double y, double width, double height,
                                          double surfaceWidth, double surfaceHeight, bool enabled);

signals:
    void busyChanged();
    void responseChanged();
    void unrealWindowChanged();

private:
    QString discoverProjectRoot() const;
    void invoke(const QStringList &arguments);
    void invokeRunAction(const QString &action, const QStringList &extra = {});
    void finishWithError(const QString &reason, const QString &detail = {});
    void processFinished(int exitCode, QProcess::ExitStatus exitStatus);
    void discoverUnrealWindow();
    void recoverRunIdentity();
    void clearUnrealWindow(const QString &state, const QString &reason = {});
    void postUnrealKey(int virtualKey);
    void resetUnrealWindowRegion();
    void loadOperatorMap();
    void writeManualControl(bool enabled, double forwardMps, double lateralMps);
    void writeQgcObservability();
    void resetQgcObservability(const QString &runId);
    void attachQgcLinks();

    QProcess _process;
    QTimer _timeout;
    QTimer _operationPoll;
    QTimer _unrealDiscovery;
    QTimer _qgcObservability;
    QString _projectRoot;
    bool _accepted = false;
    QString _statusText = QStringLiteral("Orchestrator idle");
    QString _reasonCode = QStringLiteral("idle");
    QString _runId;
    QString _profileHash;
    QString _experimentProfileId;
    QString _selectedControllerId;
    int _selectedVehicleCount = 0;
    QString _lifecycleState = QStringLiteral("unknown");
    QString _displaySessionId;
    QVariantList _controllers;
    QString _registryHash;
    QString _operationId;
    QString _operationState = QStringLiteral("idle");
    QString _operationStage = QStringLiteral("Idle");
    int _operationProgress = -1;
    int _operationAttempt = 0;
    int _operationMaxAttempts = 0;
    bool _recordingActive = false;
    QString _recordingPath;
    QWindow *_unrealWindow = nullptr;
    QString _unrealEmbedState = QStringLiteral("not_attached");
    QString _unrealEmbedReason;
    QVariantMap _operatorMap;
    QVariantMap _runtimeTelemetry;
    int _unrealDiscoveryAttempt = 0;
    int _unrealContainerReadyAttempt = 0;
    bool _unrealPresentationSuppressed = false;
    double _unrealOrbitRemainderX = 0.0;
    double _unrealOrbitRemainderY = 0.0;
    bool _startupRunRecoveryPending = false;
    QElapsedTimer _qgcMetricWindow;
    QSet<QObject *> _observedQgcLinks;
    QString _qgcMetricRunId;
    quint64 _qgcRxBytesWindow = 0;
    quint64 _qgcTxBytesWindow = 0;
    quint64 _qgcMessagesWindow = 0;
    quint64 _qgcHeartbeatsWindow = 0;
    quint64 _qgcRxBytesTotal = 0;
    quint64 _qgcTxBytesTotal = 0;
    quint64 _qgcMessagesTotal = 0;
    quint64 _qgcHeartbeatsTotal = 0;
    QString _pendingAction;
    QString _lastResponse;
};
