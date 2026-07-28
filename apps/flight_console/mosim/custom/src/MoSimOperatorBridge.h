#pragma once

#include <QtCore/QObject>
#include <QtCore/QVariantList>
#include <QtCore/QVariantMap>

// QGC owns flight interaction. This bridge only reads frozen local artifacts
// and places explicitly rendered commands on the user's clipboard.
class MoSimOperatorBridge final : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QVariantList operatorProfiles READ operatorProfiles NOTIFY stateChanged)
    Q_PROPERTY(QVariantList controllerFamilies READ controllerFamilies NOTIFY stateChanged)
    Q_PROPERTY(QVariantList controllerSchemes READ controllerSchemes NOTIFY stateChanged)
    Q_PROPERTY(QVariantList operatorMaps READ operatorMaps NOTIFY stateChanged)
    Q_PROPERTY(QVariantMap selectedProfile READ selectedProfile NOTIFY stateChanged)
    Q_PROPERTY(QString selectedProfileId READ selectedProfileId NOTIFY stateChanged)
    Q_PROPERTY(QString selectedControllerSchemeId READ selectedControllerSchemeId NOTIFY stateChanged)
    Q_PROPERTY(QString selectedMapId READ selectedMapId NOTIFY stateChanged)
    Q_PROPERTY(QVariantMap operatorMap READ operatorMap NOTIFY stateChanged)
    Q_PROPERTY(QVariantMap runManifest READ runManifest NOTIFY stateChanged)
    Q_PROPERTY(QVariantMap runtimeTelemetry READ runtimeTelemetry NOTIFY stateChanged)
    Q_PROPERTY(QVariantList faultAcks READ faultAcks NOTIFY stateChanged)
    Q_PROPERTY(QVariantMap pendingFault READ pendingFault NOTIFY stateChanged)
    Q_PROPERTY(QString runId READ runId NOTIFY stateChanged)
    Q_PROPERTY(bool profileSelectionLocked READ profileSelectionLocked NOTIFY stateChanged)
    Q_PROPERTY(QString statusText READ statusText NOTIFY stateChanged)
    Q_PROPERTY(QString reasonCode READ reasonCode NOTIFY stateChanged)
    Q_PROPERTY(QString lastCommand READ lastCommand NOTIFY stateChanged)

public:
    explicit MoSimOperatorBridge(QObject *parent = nullptr);

    QVariantList operatorProfiles() const { return _operatorProfiles; }
    QVariantList controllerFamilies() const { return _controllerFamilies; }
    QVariantList controllerSchemes() const { return _controllerSchemes; }
    QVariantList operatorMaps() const { return _operatorMaps; }
    QVariantMap selectedProfile() const;
    QString selectedProfileId() const { return _selectedProfileId; }
    QString selectedControllerSchemeId() const { return _selectedControllerSchemeId; }
    QString selectedMapId() const { return _selectedMapId; }
    QVariantMap operatorMap() const { return _operatorMap; }
    QVariantMap runManifest() const { return _runManifest; }
    QVariantMap runtimeTelemetry() const { return _runtimeTelemetry; }
    QVariantList faultAcks() const { return _faultAcks; }
    QVariantMap pendingFault() const { return _pendingFault; }
    QString runId() const { return _runId; }
    bool profileSelectionLocked() const;
    QString statusText() const { return _statusText; }
    QString reasonCode() const { return _reasonCode; }
    QString lastCommand() const { return _lastCommand; }

    Q_INVOKABLE void refresh();
    Q_INVOKABLE void refreshRuntimeState();
    Q_INVOKABLE void selectProfile(const QString &profileId);
    Q_INVOKABLE void selectControllerScheme(const QString &schemeId);
    Q_INVOKABLE void selectOperatorMap(const QString &mapId);
    Q_INVOKABLE void copySelectedLaunchCommand();
    Q_INVOKABLE void copyClearActiveRunCommand();
    Q_INVOKABLE void stageWind(const QString &vehicleId, double speedMps);
    Q_INVOKABLE void stageMotorEffectiveness(const QString &vehicleId, int rotorIndex, double effectiveness);
    Q_INVOKABLE void clearPendingFault();
    Q_INVOKABLE void copyStagedFaultCommand();
    Q_INVOKABLE void copyRestoreNormalCommand(const QString &vehicleId);
    Q_INVOKABLE void copyRosbagReplayCommand();
    Q_INVOKABLE void copyLastCommand();

signals:
    void stateChanged();

private:
    QString discoverProjectRoot() const;
    QString projectPath(const QString &relativePath) const;
    QVariantMap readJsonObject(const QString &path) const;
    void loadCatalogs();
    void loadActiveRun();
    void loadFaultAcks();
    QVariantMap profileForId(const QString &profileId) const;
    QVariantMap controllerForId(const QString &schemeId) const;
    QVariantMap mapForId(const QString &mapId) const;
    QVariantMap runtimeBackendForProfile(const QString &profileId) const;
    QString controllerSchemeForProfile(const QString &profileId) const;
    void syncSelectedMapFromProfile();
    QString activeRunDirectory() const;
    QString renderRuntimeCommand(const QVariantMap &profile, const QVariantMap &backend) const;
    void copyCommand(const QString &command, const QString &label);
    void setStatus(const QString &reasonCode, const QString &statusText);

    QString _projectRoot;
    QVariantList _operatorProfiles;
    QVariantList _controllerFamilies;
    QVariantList _controllerSchemes;
    QVariantList _operatorMaps;
    QVariantMap _runtimeBackendCatalog;
    QVariantMap _operatorMap;
    QVariantMap _runManifest;
    QVariantMap _runtimeTelemetry;
    QVariantList _faultAcks;
    QVariantMap _pendingFault;
    QString _selectedProfileId;
    QString _selectedControllerSchemeId;
    QString _selectedMapId;
    QString _runId;
    QString _statusText = QStringLiteral("正在读取 MoSim 操作配置");
    QString _reasonCode = QStringLiteral("initializing");
    QString _lastCommand;
};
