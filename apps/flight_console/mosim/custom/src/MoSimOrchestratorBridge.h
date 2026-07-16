#pragma once

#include <QtCore/QObject>
#include <QtCore/QProcess>
#include <QtCore/QTimer>

class MoSimOrchestratorBridge final : public QObject
{
    Q_OBJECT
    Q_PROPERTY(bool busy READ busy NOTIFY busyChanged)
    Q_PROPERTY(bool accepted READ accepted NOTIFY responseChanged)
    Q_PROPERTY(QString statusText READ statusText NOTIFY responseChanged)
    Q_PROPERTY(QString reasonCode READ reasonCode NOTIFY responseChanged)
    Q_PROPERTY(QString runId READ runId NOTIFY responseChanged)
    Q_PROPERTY(QString profileHash READ profileHash NOTIFY responseChanged)
    Q_PROPERTY(QString lifecycleState READ lifecycleState NOTIFY responseChanged)
    Q_PROPERTY(QString lastResponse READ lastResponse NOTIFY responseChanged)

public:
    explicit MoSimOrchestratorBridge(QObject *parent = nullptr);

    bool busy() const { return _process.state() != QProcess::NotRunning; }
    bool accepted() const { return _accepted; }
    QString statusText() const { return _statusText; }
    QString reasonCode() const { return _reasonCode; }
    QString runId() const { return _runId; }
    QString profileHash() const { return _profileHash; }
    QString lifecycleState() const { return _lifecycleState; }
    QString lastResponse() const { return _lastResponse; }

    Q_INVOKABLE void prepareRun(const QString &profilePath, const QString &controllerId, int vehicleCount,
                                double windSpeedMps);
    Q_INVOKABLE void startRun();
    Q_INVOKABLE void stopRun();
    Q_INVOKABLE void resetRun();
    Q_INVOKABLE void refreshState();
    Q_INVOKABLE void refreshTelemetry();
    Q_INVOKABLE void openModelContext();
    Q_INVOKABLE void getResultPacket();
    Q_INVOKABLE void applyWind(double value);
    Q_INVOKABLE void applyMotorEffectiveness(int rotorIndex, double value);
    Q_INVOKABLE void restoreInjection(const QString &target, int rotorIndex = 0);
    Q_INVOKABLE void prepareDisplays(const QStringList &displays);

signals:
    void busyChanged();
    void responseChanged();

private:
    QString discoverProjectRoot() const;
    void invoke(const QStringList &arguments);
    void invokeRunAction(const QString &action, const QStringList &extra = {});
    void finishWithError(const QString &reason, const QString &detail = {});
    void processFinished(int exitCode, QProcess::ExitStatus exitStatus);

    QProcess _process;
    QTimer _timeout;
    QString _projectRoot;
    bool _accepted = false;
    QString _statusText = QStringLiteral("Orchestrator idle");
    QString _reasonCode = QStringLiteral("idle");
    QString _runId;
    QString _profileHash;
    QString _lifecycleState = QStringLiteral("unknown");
    QString _lastResponse;
};
