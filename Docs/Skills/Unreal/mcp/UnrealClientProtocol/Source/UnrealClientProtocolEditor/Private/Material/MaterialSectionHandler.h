// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "NodeCode/INodeCodeSectionHandler.h"

class FMaterialSectionHandler : public INodeCodeSectionHandler
{
public:
	virtual TArray<FNodeCodeSectionTypeInfo> GetSupportedSectionTypes() const override;
	virtual bool CanHandle(UObject* Asset, const FString& Type) const override;
	virtual TArray<FNodeCodeSectionIR> ListSections(UObject* Asset) override;
	virtual FNodeCodeSectionIR Read(UObject* Asset, const FString& Type, const FString& Name) override;
	virtual FNodeCodeDiffResult Write(UObject* Asset, const FNodeCodeSectionIR& Section) override;
	virtual bool CreateSection(UObject* Asset, const FString& Type, const FString& Name) override;
	virtual bool RemoveSection(UObject* Asset, const FString& Type, const FString& Name) override;
	virtual UObject* FindNodeByGuid(UObject* Asset, const FGuid& Guid) override;
};
