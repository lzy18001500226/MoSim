#pragma once

#include <QtQml/QQmlAbstractUrlInterceptor>

#include "QGCCorePlugin.h"

class MoSimOperatorBridge;
class QQmlApplicationEngine;

class CustomPlugin final : public QGCCorePlugin
{
    Q_OBJECT
public:
    explicit CustomPlugin(QObject *parent = nullptr);
    ~CustomPlugin() override;

    static QGCCorePlugin *instance();
    QQmlApplicationEngine *createQmlApplicationEngine(QObject *parent) final;
    QString brandImageIndoor() const final { return QString(); }
    QString brandImageOutdoor() const final { return QString(); }

private:
    QQmlApplicationEngine *_qmlEngine = nullptr;
    class CustomOverrideInterceptor *_selector = nullptr;
    MoSimOperatorBridge *_operatorBridge = nullptr;
};

class CustomOverrideInterceptor final : public QQmlAbstractUrlInterceptor
{
public:
    QUrl intercept(const QUrl &url, DataType type) final;
};
