// MIT License - Copyright (c) 2025 Italink

#include "UCPModule.h"
#include "UCPServer.h"
#include "UCPSettings.h"

#define LOCTEXT_NAMESPACE "FUnrealClientProtocolModule"

void FUnrealClientProtocolModule::StartupModule()
{
	const UUCPSettings* Settings = GetDefault<UUCPSettings>();
	if (!Settings->bEnabled)
	{
		UE_LOG(LogTemp, Log, TEXT("[UCP] Plugin is disabled in settings."));
		return;
	}

	Server = MakeUnique<FUCPServer>(Settings->Port);
	if (Server->Start())
	{
		bIsRunning = true;
		UE_LOG(LogTemp, Log, TEXT("[UCP] Server started on port %d"), Settings->Port);
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("[UCP] Failed to start server on port %d"), Settings->Port);
		Server.Reset();
	}
}

void FUnrealClientProtocolModule::ShutdownModule()
{
	bIsRunning = false;
	if (Server)
	{
		Server->Stop();
		Server.Reset();
	}
	UE_LOG(LogTemp, Log, TEXT("[UCP] Server stopped."));
}

void FUnrealClientProtocolModule::Tick(float DeltaTime)
{
	if (Server)
	{
		Server->Tick();
	}
}

TStatId FUnrealClientProtocolModule::GetStatId() const
{
	RETURN_QUICK_DECLARE_CYCLE_STAT(FUnrealClientProtocolModule, STATGROUP_Tickables);
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FUnrealClientProtocolModule, UnrealClientProtocol)
