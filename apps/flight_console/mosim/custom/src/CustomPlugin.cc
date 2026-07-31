#include "CustomPlugin.h"

#include <QtCore/QApplicationStatic>
#include <QtCore/QFile>
#include <QtGui/QGuiApplication>
#include <QtQml/QQmlApplicationEngine>
#include <QtQml/QQmlContext>

#include "MoSimOperatorBridge.h"

Q_APPLICATION_STATIC(CustomPlugin, customPluginInstance)

CustomPlugin::CustomPlugin(QObject *parent)
    : QGCCorePlugin(parent)
    , _operatorBridge(new MoSimOperatorBridge(this))
{
    _showAdvancedUI = false;
    // Keep the CMake-safe executable name while presenting the operator-facing name.
    QGuiApplication::setApplicationName(QStringLiteral("MoSim Ground Control"));
    QGuiApplication::setApplicationDisplayName(QStringLiteral("MoSim Ground Control"));
}

CustomPlugin::~CustomPlugin()
{
    if (_qmlEngine && _selector) {
        _qmlEngine->removeUrlInterceptor(_selector);
    }
    delete _selector;
}

QGCCorePlugin *CustomPlugin::instance()
{
    return customPluginInstance();
}

QQmlApplicationEngine *CustomPlugin::createQmlApplicationEngine(QObject *parent)
{
    _qmlEngine = QGCCorePlugin::createQmlApplicationEngine(parent);
    _qmlEngine->rootContext()->setContextProperty(QStringLiteral("mosimOperator"), _operatorBridge);
    _selector = new CustomOverrideInterceptor();
    _qmlEngine->addUrlInterceptor(_selector);
    return _qmlEngine;
}

QUrl CustomOverrideInterceptor::intercept(const QUrl &url, DataType type)
{
    if ((type == DataType::QmlFile || type == DataType::UrlString) && url.scheme() == QStringLiteral("qrc")) {
        const QString overridePath = QStringLiteral(":/Custom%1").arg(url.path());
        if (QFile::exists(overridePath)) {
            QUrl result;
            result.setScheme(QStringLiteral("qrc"));
            result.setPath('/' + overridePath.mid(2));
            return result;
        }
    }
    return url;
}
