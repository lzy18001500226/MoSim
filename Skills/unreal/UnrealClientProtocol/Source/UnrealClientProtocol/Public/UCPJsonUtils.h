// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "Dom/JsonObject.h"
#include "Dom/JsonValue.h"
#include "Serialization/JsonWriter.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/UObjectGlobals.h"

namespace UCPUtils
{

inline FString JsonToString(const TSharedPtr<FJsonObject>& Obj)
{
	FString Out;
	auto Writer = TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&Out);
	FJsonSerializer::Serialize(Obj.ToSharedRef(), Writer);
	return Out;
}

inline FString JsonArrayToString(const TArray<TSharedPtr<FJsonValue>>& Arr)
{
	FString Out;
	auto Writer = TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&Out);
	FJsonSerializer::Serialize(Arr, Writer);
	return Out;
}

inline UObject* LoadObject(const FString& Path)
{
	UObject* Obj = StaticFindObject(UObject::StaticClass(), nullptr, *Path);
	if (!Obj)
	{
		Obj = StaticLoadObject(UObject::StaticClass(), nullptr, *Path);
	}
	return Obj;
}

}
