// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FUCPServer;

class UNREALCLIENTPROTOCOL_API FUnrealClientProtocolModule : public IModuleInterface, public FTickableGameObject
{
public:
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

	virtual void Tick(float DeltaTime) override;
	virtual TStatId GetStatId() const override;
	virtual bool IsTickable() const override { return bIsRunning; }
	virtual bool IsTickableInEditor() const override { return true; }

	static FUnrealClientProtocolModule& Get()
	{
		return FModuleManager::GetModuleChecked<FUnrealClientProtocolModule>("UnrealClientProtocol");
	}

	static bool IsAvailable()
	{
		return FModuleManager::Get().IsModuleLoaded("UnrealClientProtocol");
	}

private:
	TUniquePtr<FUCPServer> Server;
	bool bIsRunning = false;
};
