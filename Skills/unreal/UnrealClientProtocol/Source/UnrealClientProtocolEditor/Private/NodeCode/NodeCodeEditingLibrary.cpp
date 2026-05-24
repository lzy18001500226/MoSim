// MIT License - Copyright (c) 2025 Italink

#include "NodeCode/NodeCodeEditingLibrary.h"
#include "NodeCode/INodeCodeSectionHandler.h"
#include "NodeCode/NodeCodeTextFormat.h"
#include "NodeCode/NodeCodeClassCache.h"
#include "NodeCode/NodeCodeTypes.h"

#include "Blueprint/BlueprintSectionHandler.h"
#include "Material/MaterialSectionHandler.h"
#include "Widget/WidgetTreeSectionHandler.h"
#include "Niagara/NiagaraSectionHandler.h"

#include "EdGraph/EdGraphNode.h"
#include "Materials/MaterialExpression.h"
#include "Components/Widget.h"
#include "NiagaraNode.h"

#include "Dom/JsonObject.h"
#include "Serialization/JsonWriter.h"
#include "Serialization/JsonSerializer.h"
#include "ScopedTransaction.h"

DEFINE_LOG_CATEGORY_STATIC(LogNodeCodeEditing, Log, All);

struct FNodeCodeHandlerAutoRegister
{
	FNodeCodeHandlerAutoRegister()
	{
		auto& ClassCache = FNodeCodeClassCache::Get();
		ClassCache.RegisterBaseClass(UEdGraphNode::StaticClass());
		ClassCache.RegisterBaseClass(UMaterialExpression::StaticClass());
		ClassCache.RegisterBaseClass(UWidget::StaticClass());
		ClassCache.RegisterBaseClass(UNiagaraNode::StaticClass());

		auto& Registry = FNodeCodeSectionHandlerRegistry::Get();
		Registry.Register(MakeShared<FBlueprintSectionHandler>());
		Registry.Register(MakeShared<FMaterialSectionHandler>());
		Registry.Register(MakeShared<FWidgetTreeSectionHandler>());
		Registry.Register(MakeShared<FNiagaraSectionHandler>());
	}
};

static FNodeCodeHandlerAutoRegister GAutoRegisterHandlers;

static UObject* LoadAsset(const FString& AssetPath)
{
	return StaticLoadObject(UObject::StaticClass(), nullptr, *AssetPath);
}

FString UNodeCodeEditingLibrary::Outline(const FString& AssetPath)
{
	UObject* Asset = LoadAsset(AssetPath);
	if (!Asset)
	{
		UE_LOG(LogNodeCodeEditing, Error, TEXT("Outline: Asset not found: %s"), *AssetPath);
		return FString();
	}

	TArray<FNodeCodeSectionIR> Sections = FNodeCodeSectionHandlerRegistry::Get().ListAllSections(Asset);

	TSharedPtr<FJsonObject> Root = MakeShared<FJsonObject>();
	TArray<TSharedPtr<FJsonValue>> SectionValues;
	for (const FNodeCodeSectionIR& Section : Sections)
	{
		SectionValues.Add(MakeShared<FJsonValueString>(Section.GetHeader()));
	}
	Root->SetArrayField(TEXT("sections"), SectionValues);

	FString OutputString;
	TSharedRef<TJsonWriter<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>> Writer =
		TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&OutputString);
	FJsonSerializer::Serialize(Root.ToSharedRef(), Writer);
	return OutputString;
}

FString UNodeCodeEditingLibrary::ReadGraph(const FString& AssetPath, const FString& Section)
{
	UObject* Asset = LoadAsset(AssetPath);
	if (!Asset)
	{
		UE_LOG(LogNodeCodeEditing, Error, TEXT("ReadGraph: Asset not found: %s"), *AssetPath);
		return FString();
	}

	FNodeCodeDocumentIR Document;

	auto& Registry = FNodeCodeSectionHandlerRegistry::Get();

	if (Section.IsEmpty())
	{
		TArray<FNodeCodeSectionIR> AllSections = Registry.ListAllSections(Asset);
		for (const FNodeCodeSectionIR& SectionInfo : AllSections)
		{
			INodeCodeSectionHandler* Handler = Registry.FindHandler(Asset, SectionInfo.Type);
			if (Handler)
			{
				FNodeCodeSectionIR S = Handler->Read(Asset, SectionInfo.Type, SectionInfo.Name);
				S.Format = Registry.GetSectionFormat(S.Type);
				Document.Sections.Add(MoveTemp(S));
			}
		}
	}
	else
	{
		FString Type, Name;
		if (NodeCodeUtils::ParseSectionHeader(FString::Printf(TEXT("[%s]"), *Section), Type, Name))
		{
			INodeCodeSectionHandler* Handler = Registry.FindHandler(Asset, Type);
			if (Handler)
			{
				FNodeCodeSectionIR S = Handler->Read(Asset, Type, Name);
				S.Format = Registry.GetSectionFormat(S.Type);
				Document.Sections.Add(MoveTemp(S));
			}
			else
			{
				UE_LOG(LogNodeCodeEditing, Error, TEXT("ReadGraph: No handler for section type: %s"), *Type);
			}
		}
		else
		{
			UE_LOG(LogNodeCodeEditing, Error, TEXT("ReadGraph: Invalid section format: %s"), *Section);
		}
	}

	return FNodeCodeTextFormat::DocumentToText(Document);
}

FString UNodeCodeEditingLibrary::WriteGraph(const FString& AssetPath, const FString& Section, const FString& GraphText)
{
	UObject* Asset = LoadAsset(AssetPath);
	if (!Asset)
	{
		UE_LOG(LogNodeCodeEditing, Error, TEXT("WriteGraph: Asset not found: %s"), *AssetPath);
		return FString();
	}

	if (GraphText.IsEmpty() && !Section.IsEmpty())
	{
		FNodeCodeDiffResult RemoveResult;
		FString Type, Name;
		if (NodeCodeUtils::ParseSectionHeader(FString::Printf(TEXT("[%s]"), *Section), Type, Name))
		{
			INodeCodeSectionHandler* Handler = FNodeCodeSectionHandlerRegistry::Get().FindHandler(Asset, Type);
			if (Handler && Handler->RemoveSection(Asset, Type, Name))
			{
				RemoveResult.NodesRemoved.Add(FString::Printf(TEXT("Removed section: %s"), *Section));
			}
			else
			{
				RemoveResult.NodesModified.Add(FString::Printf(TEXT("Failed to remove section: %s"), *Section));
			}
		}
		return FNodeCodeTextFormat::DiffResultToJson(RemoveResult);
	}

	FNodeCodeDocumentIR Document;

	if (!Section.IsEmpty())
	{
		FString Type, Name;
		if (NodeCodeUtils::ParseSectionHeader(FString::Printf(TEXT("[%s]"), *Section), Type, Name))
		{
			FNodeCodeSectionIR SectionIR = FNodeCodeTextFormat::ParseSection(GraphText, Type, Name);
			Document.Sections.Add(MoveTemp(SectionIR));
		}
	}
	else
	{
		Document = FNodeCodeTextFormat::ParseDocument(GraphText);
	}

	FNodeCodeDiffResult CombinedResult;

	for (const FNodeCodeSectionIR& SectionIR : Document.Sections)
	{
		INodeCodeSectionHandler* Handler = FNodeCodeSectionHandlerRegistry::Get().FindHandler(Asset, SectionIR.Type);
		if (!Handler)
		{
			UE_LOG(LogNodeCodeEditing, Error, TEXT("WriteGraph: No handler for section type: %s"), *SectionIR.Type);
			continue;
		}

		bool bSectionExists = false;
		TArray<FNodeCodeSectionIR> ExistingSections = Handler->ListSections(Asset);
		for (const FNodeCodeSectionIR& Existing : ExistingSections)
		{
			if (Existing.Type == SectionIR.Type && Existing.Name == SectionIR.Name)
			{
				bSectionExists = true;
				break;
			}
		}

		if (!bSectionExists && SectionIR.Format == ENodeCodeSectionFormat::Graph)
		{
			if (!Handler->CreateSection(Asset, SectionIR.Type, SectionIR.Name))
			{
				UE_LOG(LogNodeCodeEditing, Warning, TEXT("WriteGraph: Could not create section [%s:%s]"), *SectionIR.Type, *SectionIR.Name);
			}
		}

		FNodeCodeDiffResult SectionResult = Handler->Write(Asset, SectionIR);

		CombinedResult.NodesAdded.Append(SectionResult.NodesAdded);
		CombinedResult.NodesRemoved.Append(SectionResult.NodesRemoved);
		CombinedResult.NodesModified.Append(SectionResult.NodesModified);
		CombinedResult.LinksAdded.Append(SectionResult.LinksAdded);
		CombinedResult.LinksRemoved.Append(SectionResult.LinksRemoved);
		CombinedResult.CompileErrors.Append(SectionResult.CompileErrors);
	}

	return FNodeCodeTextFormat::DiffResultToJson(CombinedResult);
}

FString UNodeCodeEditingLibrary::ResolveNodeId(const FString& AssetPath, const FString& NodeId)
{
	UObject* Asset = LoadAsset(AssetPath);
	if (!Asset)
	{
		UE_LOG(LogNodeCodeEditing, Error, TEXT("ResolveNodeId: Asset not found: %s"), *AssetPath);
		return FString();
	}

	FGuid Guid = NodeCodeUtils::Base62ToGuid(NodeId);
	if (!Guid.IsValid())
	{
		UE_LOG(LogNodeCodeEditing, Error, TEXT("ResolveNodeId: Invalid NodeId: %s"), *NodeId);
		return FString();
	}

	UObject* Found = FNodeCodeSectionHandlerRegistry::Get().FindNodeByGuid(Asset, Guid);
	if (Found)
	{
		return Found->GetPathName();
	}

	return FString();
}
