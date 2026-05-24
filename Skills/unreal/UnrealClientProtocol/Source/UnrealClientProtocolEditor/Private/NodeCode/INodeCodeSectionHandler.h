// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "NodeCode/NodeCodeTypes.h"

struct FNodeCodeSectionTypeInfo
{
	FString TypeName;
	ENodeCodeSectionFormat Format;
};

class INodeCodeSectionHandler
{
public:
	virtual ~INodeCodeSectionHandler() = default;

	virtual TArray<FNodeCodeSectionTypeInfo> GetSupportedSectionTypes() const = 0;

	virtual bool CanHandle(UObject* Asset, const FString& Type) const = 0;

	virtual TArray<FNodeCodeSectionIR> ListSections(UObject* Asset) = 0;

	virtual FNodeCodeSectionIR Read(UObject* Asset, const FString& Type, const FString& Name) = 0;

	virtual FNodeCodeDiffResult Write(UObject* Asset, const FNodeCodeSectionIR& Section) = 0;

	virtual bool CreateSection(UObject* Asset, const FString& Type, const FString& Name) = 0;

	virtual bool RemoveSection(UObject* Asset, const FString& Type, const FString& Name) = 0;

	virtual UObject* FindNodeByGuid(UObject* Asset, const FGuid& Guid) { return nullptr; }
};

class FNodeCodeSectionHandlerRegistry
{
public:
	static FNodeCodeSectionHandlerRegistry& Get();

	void Register(TSharedPtr<INodeCodeSectionHandler> Handler);

	INodeCodeSectionHandler* FindHandler(UObject* Asset, const FString& Type) const;

	TArray<FNodeCodeSectionIR> ListAllSections(UObject* Asset) const;

	ENodeCodeSectionFormat GetSectionFormat(const FString& TypeName) const;

	UObject* FindNodeByGuid(UObject* Asset, const FGuid& Guid) const;

private:
	TArray<TSharedPtr<INodeCodeSectionHandler>> Handlers;
	TMap<FString, ENodeCodeSectionFormat> TypeFormatMap;
};
