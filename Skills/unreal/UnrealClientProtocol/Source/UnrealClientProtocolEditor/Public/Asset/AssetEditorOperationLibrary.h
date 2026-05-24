// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "AssetRegistry/IAssetRegistry.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "AssetEditorOperationLibrary.generated.h"

UCLASS()
class UAssetEditorOperationLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "UCP|Asset|Editor")
	static TScriptInterface<IAssetRegistry> GetAssetRegistry();

	UFUNCTION(BlueprintCallable, Category = "UCP|Asset|Editor")
	static int32 ForceDeleteAssets(const TArray<FString>& AssetPaths);

	UFUNCTION(BlueprintCallable, Category = "UCP|Asset|Editor")
	static bool FixupReferencers(const TArray<FString>& AssetPaths);
};
