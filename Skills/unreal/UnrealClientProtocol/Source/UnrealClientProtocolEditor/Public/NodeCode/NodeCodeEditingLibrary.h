// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "NodeCodeEditingLibrary.generated.h"

UCLASS()
class UNodeCodeEditingLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "UCP|NodeCode")
	static FString Outline(const FString& AssetPath);

	UFUNCTION(BlueprintCallable, Category = "UCP|NodeCode")
	static FString ReadGraph(const FString& AssetPath, const FString& Section = TEXT(""));

	UFUNCTION(BlueprintCallable, Category = "UCP|NodeCode")
	static FString WriteGraph(const FString& AssetPath, const FString& Section, const FString& GraphText);

	UFUNCTION(BlueprintCallable, Category = "UCP|NodeCode")
	static FString ResolveNodeId(const FString& AssetPath, const FString& NodeId);
};
