// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ObjectEditorOperationLibrary.generated.h"

UCLASS()
class UObjectEditorOperationLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "UCP|Object|Editor")
	static FString UndoTransaction(const FString& Keyword = TEXT(""));

	UFUNCTION(BlueprintCallable, Category = "UCP|Object|Editor")
	static FString RedoTransaction(const FString& Keyword = TEXT(""));

	UFUNCTION(BlueprintCallable, Category = "UCP|Object|Editor")
	static FString GetTransactionState();

	UFUNCTION(BlueprintCallable, Category = "UCP|Object|Editor")
	static bool ForceReplaceReferences(const FString& ReplacementObjectPath, const TArray<FString>& ObjectsToReplacePaths);
};
