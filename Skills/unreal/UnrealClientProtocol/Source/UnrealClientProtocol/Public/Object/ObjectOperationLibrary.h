// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ObjectOperationLibrary.generated.h"

UCLASS()
class UNREALCLIENTPROTOCOL_API UObjectOperationLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "UCP|Object")
	static FString GetObjectProperty(const FString& ObjectPath, const FString& PropertyName);

	UFUNCTION(BlueprintCallable, Category = "UCP|Object")
	static FString SetObjectProperty(const FString& ObjectPath, const FString& PropertyName, const FString& JsonValue);

	UFUNCTION(BlueprintCallable, Category = "UCP|Object")
	static FString DescribeObject(const FString& ObjectPath);

	UFUNCTION(BlueprintCallable, Category = "UCP|Object")
	static FString DescribeObjectProperty(const FString& ObjectPath, const FString& PropertyName);

	UFUNCTION(BlueprintCallable, Category = "UCP|Object")
	static FString DescribeObjectFunction(const FString& ObjectPath, const FString& FunctionName);

	UFUNCTION(BlueprintCallable, Category = "UCP|Object")
	static FString FindObjectInstances(const FString& ClassName, int32 Limit = 100);

	UFUNCTION(BlueprintCallable, Category = "UCP|Object")
	static FString FindDerivedClasses(const FString& ClassName, bool bRecursive = true, int32 Limit = 500);

	UFUNCTION(BlueprintCallable, Category = "UCP|Object")
	static FString ListComponents(const FString& ObjectPath);

	UFUNCTION(BlueprintCallable, Category = "UCP|Object")
	static FString FindObjectsByOuter(const FString& OuterPath, const FString& ClassName = TEXT(""), int32 Limit = 100);
};
