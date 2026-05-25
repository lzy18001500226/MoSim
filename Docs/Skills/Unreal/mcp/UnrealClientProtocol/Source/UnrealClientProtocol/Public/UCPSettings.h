// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "UCPSettings.generated.h"

UCLASS(config = UCP, defaultconfig, meta = (DisplayName = "UCP"))
class UUCPSettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	UUCPSettings()
		: bEnabled(true)
		, Port(9876)
		, bLoopbackOnly(true)
	{
		CategoryName = TEXT("Plugins");
		SectionName = TEXT("UCP");
	}

	UPROPERTY(config, EditAnywhere, Category = "Server")
	bool bEnabled;

	UPROPERTY(config, EditAnywhere, Category = "Server", meta = (ClampMin = "1024", ClampMax = "65535"))
	int32 Port;

	UPROPERTY(config, EditAnywhere, Category = "Security")
	bool bLoopbackOnly;

	UPROPERTY(config, EditAnywhere, Category = "Security")
	TArray<FString> AllowedClassPrefixes;

	UPROPERTY(config, EditAnywhere, Category = "Security")
	TArray<FString> BlockedFunctions;
};
