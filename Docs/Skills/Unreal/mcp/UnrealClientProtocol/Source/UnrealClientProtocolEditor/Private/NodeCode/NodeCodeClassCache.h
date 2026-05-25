// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"

class FNodeCodeClassCache
{
public:
	static FNodeCodeClassCache& Get();

	void RegisterBaseClass(UClass* BaseClass);

	UClass* FindClass(const FString& ClassName) const;

	FString GetSerializableName(UClass* InClass) const;

private:
	void EnsureBuilt() const;
	void Build();

	TArray<UClass*> BaseClasses;
	TMap<FName, UClass*> NameToClass;
	TSet<FName> AmbiguousNames;
	bool bBuilt = false;
};
