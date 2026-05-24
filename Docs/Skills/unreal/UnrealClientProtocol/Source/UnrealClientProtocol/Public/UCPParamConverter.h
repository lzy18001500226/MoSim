// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "Dom/JsonObject.h"
#include "Dom/JsonValue.h"

class FProperty;
class UFunction;
class UObject;

class UNREALCLIENTPROTOCOL_API FUCPParamConverter
{
public:
	static FString JsonToParams(
		UFunction* Function,
		const TSharedPtr<FJsonObject>& ParamsJson,
		uint8* ParamBuffer,
		UObject* ContextObject);

	static TSharedPtr<FJsonObject> ParamsToJson(
		UFunction* Function,
		const uint8* ParamBuffer);

	static TSharedPtr<FJsonValue> PropertyToJsonValue(
		FProperty* Property,
		const void* ValuePtr);

	static FString JsonValueToProperty(
		const TSharedPtr<FJsonValue>& JsonVal,
		FProperty* Property,
		void* ValuePtr);

	static FProperty* FindPropertyByNameFlexible(UClass* Class, const FString& PropertyName);

private:
	static UObject* ResolveObjectPath(const FString& Path, UClass* ExpectedClass);
	static UWorld* GetBestWorld();
};
