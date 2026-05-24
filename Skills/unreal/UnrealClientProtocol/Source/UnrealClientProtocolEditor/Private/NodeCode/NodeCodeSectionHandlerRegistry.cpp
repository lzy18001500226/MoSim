// MIT License - Copyright (c) 2025 Italink

#include "NodeCode/INodeCodeSectionHandler.h"

FNodeCodeSectionHandlerRegistry& FNodeCodeSectionHandlerRegistry::Get()
{
	static FNodeCodeSectionHandlerRegistry Instance;
	return Instance;
}

void FNodeCodeSectionHandlerRegistry::Register(TSharedPtr<INodeCodeSectionHandler> Handler)
{
	if (Handler.IsValid())
	{
		Handlers.Add(Handler);

		for (const FNodeCodeSectionTypeInfo& Info : Handler->GetSupportedSectionTypes())
		{
			TypeFormatMap.Add(Info.TypeName, Info.Format);
		}
	}
}

INodeCodeSectionHandler* FNodeCodeSectionHandlerRegistry::FindHandler(UObject* Asset, const FString& Type) const
{
	for (const auto& Handler : Handlers)
	{
		if (Handler->CanHandle(Asset, Type))
		{
			return Handler.Get();
		}
	}
	return nullptr;
}

TArray<FNodeCodeSectionIR> FNodeCodeSectionHandlerRegistry::ListAllSections(UObject* Asset) const
{
	TArray<FNodeCodeSectionIR> AllSections;
	TSet<INodeCodeSectionHandler*> VisitedHandlers;

	for (const auto& Handler : Handlers)
	{
		if (!Handler->CanHandle(Asset, TEXT("")))
		{
			continue;
		}

		if (VisitedHandlers.Contains(Handler.Get()))
		{
			continue;
		}
		VisitedHandlers.Add(Handler.Get());

		TArray<FNodeCodeSectionIR> Sections = Handler->ListSections(Asset);
		AllSections.Append(Sections);
	}

	for (FNodeCodeSectionIR& S : AllSections)
	{
		S.Format = GetSectionFormat(S.Type);
	}

	return AllSections;
}

UObject* FNodeCodeSectionHandlerRegistry::FindNodeByGuid(UObject* Asset, const FGuid& Guid) const
{
	for (const auto& Handler : Handlers)
	{
		if (Handler->CanHandle(Asset, TEXT("")))
		{
			UObject* Found = Handler->FindNodeByGuid(Asset, Guid);
			if (Found)
			{
				return Found;
			}
		}
	}
	return nullptr;
}

ENodeCodeSectionFormat FNodeCodeSectionHandlerRegistry::GetSectionFormat(const FString& TypeName) const
{
	if (const ENodeCodeSectionFormat* Found = TypeFormatMap.Find(TypeName))
	{
		return *Found;
	}
	return ENodeCodeSectionFormat::Graph;
}
