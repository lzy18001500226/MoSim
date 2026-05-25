// MIT License - Copyright (c) 2025 Italink

#include "Blueprint/BlueprintGraphDiffer.h"
#include "Blueprint/BlueprintGraphSerializer.h"
#include "Blueprint/IBlueprintNodeEncoder.h"
#include "NodeCode/NodeCodeTypes.h"

#include "Engine/Blueprint.h"
#include "EdGraph/EdGraph.h"
#include "EdGraph/EdGraphNode.h"
#include "EdGraph/EdGraphPin.h"
#include "EdGraphSchema_K2.h"
#include "K2Node.h"
#include "K2Node_FunctionEntry.h"
#include "K2Node_FunctionResult.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "UObject/UnrealType.h"
#include "ScopedTransaction.h"

DEFINE_LOG_CATEGORY_STATIC(LogUCPBlueprint, Log, All);

struct FBPPinPair
{
	UEdGraphPin* FromPin = nullptr;
	UEdGraphPin* ToPin = nullptr;

	bool operator==(const FBPPinPair& Other) const { return FromPin == Other.FromPin && ToPin == Other.ToPin; }
	friend uint32 GetTypeHash(const FBPPinPair& P) { return HashCombine(::GetTypeHash(P.FromPin), ::GetTypeHash(P.ToPin)); }
};

// ---- Apply ----

FNodeCodeDiffResult FBlueprintGraphDiffer::Apply(UBlueprint* Blueprint, UEdGraph* Graph, const FNodeCodeGraphIR& NewIR)
{
	FNodeCodeDiffResult Result;

	if (!Blueprint || !Graph)
	{
		UE_LOG(LogUCPBlueprint, Error, TEXT("Apply: Blueprint or Graph is null"));
		return Result;
	}

	FNodeCodeGraphIR OldIR = FBlueprintGraphSerializer::BuildIR(Graph);

	TMap<int32, int32> NewToOld;
	MatchNodes(OldIR, NewIR, NewToOld);

	TSet<int32> MatchedOldIndices;
	for (auto& Pair : NewToOld)
	{
		MatchedOldIndices.Add(Pair.Value);
	}

	FScopedTransaction Transaction(NSLOCTEXT("UCPBlueprintGraph", "WriteGraph", "UCP: Write Blueprint Graph"));

	Graph->Modify();

	// Phase 1: Delete
	for (int32 OldIdx = 0; OldIdx < OldIR.Nodes.Num(); ++OldIdx)
	{
		if (MatchedOldIndices.Contains(OldIdx))
		{
			continue;
		}

		const FNodeCodeNodeIR& OldNode = OldIR.Nodes[OldIdx];
		UEdGraphNode* OldGraphNode = Cast<UEdGraphNode>(OldNode.SourceObject);
		if (OldGraphNode)
		{
			if (Cast<UK2Node_FunctionEntry>(OldGraphNode) || Cast<UK2Node_FunctionResult>(OldGraphNode))
			{
				continue;
			}
			Graph->RemoveNode(OldGraphNode);
			Result.NodesRemoved.Add(FString::Printf(TEXT("N_%s %s"), *OldNode.Index, *OldNode.ClassName));
		}
	}

	// Phase 2: Create
	TMap<FString, UEdGraphNode*> NewIndexToNode;

	for (int32 NewIdx = 0; NewIdx < NewIR.Nodes.Num(); ++NewIdx)
	{
		const FNodeCodeNodeIR& NewNode = NewIR.Nodes[NewIdx];

		if (int32* OldIdx = NewToOld.Find(NewIdx))
		{
			NewIndexToNode.Add(NewNode.Index, Cast<UEdGraphNode>(OldIR.Nodes[*OldIdx].SourceObject));
		}
		else
		{
			UEdGraphNode* CreatedNode = FBlueprintNodeEncoderRegistry::Get().DecodeNode(NewNode.ClassName, Graph, Blueprint, NewNode);
			if (CreatedNode)
			{
				NewIndexToNode.Add(NewNode.Index, CreatedNode);
				Result.NodesAdded.Add(FString::Printf(TEXT("N_%s %s"), *NewNode.Index, *NewNode.ClassName));
			}
			else
			{
				UE_LOG(LogUCPBlueprint, Error, TEXT("WriteGraph: Failed to create node: %s"), *NewNode.ClassName);
			}
		}
	}

	// Phase 3: Update properties on matched nodes
	for (int32 NewIdx = 0; NewIdx < NewIR.Nodes.Num(); ++NewIdx)
	{
		int32* OldIdx = NewToOld.Find(NewIdx);
		if (!OldIdx)
		{
			continue;
		}

		const FNodeCodeNodeIR& NewNode = NewIR.Nodes[NewIdx];
		const FNodeCodeNodeIR& OldNode = OldIR.Nodes[*OldIdx];
		UEdGraphNode* GraphNode = Cast<UEdGraphNode>(OldNode.SourceObject);

		if (!GraphNode)
		{
			continue;
		}

		bool bPropsChanged = (NewNode.Properties.Num() != OldNode.Properties.Num());
		if (!bPropsChanged)
		{
			for (const auto& Pair : NewNode.Properties)
			{
				const FString* OldVal = OldNode.Properties.Find(Pair.Key);
				if (!OldVal || *OldVal != Pair.Value)
				{
					bPropsChanged = true;
					break;
				}
			}
		}

		if (bPropsChanged)
		{
			TArray<FString> Changes;
			ApplyPropertyChanges(GraphNode, NewNode.Properties, Changes);
			ApplyPinDefaults(GraphNode, NewNode.Properties, Changes);

			if (Changes.Num() > 0)
			{
				Result.NodesModified.Add(FString::Printf(TEXT("N_%s: %s"),
					*NewNode.Index, *FString::Join(Changes, TEXT("; "))));
			}
		}
	}

	// Phase 4: Apply pin defaults on newly created nodes
	for (int32 NewIdx = 0; NewIdx < NewIR.Nodes.Num(); ++NewIdx)
	{
		if (NewToOld.Contains(NewIdx))
		{
			continue;
		}

		const FNodeCodeNodeIR& NewNode = NewIR.Nodes[NewIdx];
		UEdGraphNode** NodePtr = NewIndexToNode.Find(NewNode.Index);
		if (NodePtr && *NodePtr)
		{
			TArray<FString> Changes;
			ApplyPinDefaults(*NodePtr, NewNode.Properties, Changes);
		}
	}

	// Phase 5+6: Connection diff
	TSet<FBPPinPair> DesiredLinks;
	TArray<FBPPinPair> LinksToCreate;

	for (const FNodeCodeLinkIR& Link : NewIR.Links)
	{
		UEdGraphNode** FromNodePtr = NewIndexToNode.Find(Link.FromNodeIndex);
		UEdGraphNode** ToNodePtr = NewIndexToNode.Find(Link.ToNodeIndex);
		if (!FromNodePtr || !*FromNodePtr || !ToNodePtr || !*ToNodePtr)
		{
			continue;
		}

		UEdGraphPin* FromPin = FindPinByName(*FromNodePtr, Link.FromOutputName, EGPD_Output);
		UEdGraphPin* ToPin = FindPinByName(*ToNodePtr, Link.ToInputName, EGPD_Input);
		if (!FromPin || !ToPin)
		{
			if (!FromPin)
			{
				UE_LOG(LogUCPBlueprint, Warning, TEXT("WriteGraph: Output pin '%s' not found on N_%s"), *Link.FromOutputName, *Link.FromNodeIndex);
			}
			if (!ToPin)
			{
				UE_LOG(LogUCPBlueprint, Warning, TEXT("WriteGraph: Input pin '%s' not found on N_%s"), *Link.ToInputName, *Link.ToNodeIndex);
			}
			continue;
		}

		FBPPinPair Pair{FromPin, ToPin};
		DesiredLinks.Add(Pair);

		if (!FromPin->LinkedTo.Contains(ToPin))
		{
			LinksToCreate.Add(Pair);
		}
	}

	TSet<UEdGraphNode*> ScopeNodeSet;
	for (auto& Pair : NewIndexToNode)
	{
		if (Pair.Value) ScopeNodeSet.Add(Pair.Value);
	}

	for (auto& Pair : NewIndexToNode)
	{
		UEdGraphNode* GraphNode = Pair.Value;
		if (!GraphNode) continue;

		for (UEdGraphPin* Pin : GraphNode->Pins)
		{
			if (!Pin || Pin->Direction != EGPD_Output) continue;

			TArray<UEdGraphPin*> LinksToBreak;
			for (UEdGraphPin* LinkedPin : Pin->LinkedTo)
			{
				if (!LinkedPin || !ScopeNodeSet.Contains(LinkedPin->GetOwningNode())) continue;
				FBPPinPair LivePair{Pin, LinkedPin};
				if (!DesiredLinks.Contains(LivePair))
				{
					LinksToBreak.Add(LinkedPin);
				}
			}
			for (UEdGraphPin* LinkedPin : LinksToBreak)
			{
				Pin->BreakLinkTo(LinkedPin);
				Result.LinksRemoved.Add(FString::Printf(TEXT("%s.%s -> %s.%s"),
					*Pin->GetOwningNode()->GetName(), *Pin->PinName.ToString(),
					*LinkedPin->GetOwningNode()->GetName(), *LinkedPin->PinName.ToString()));
			}
		}
	}

	const UEdGraphSchema* Schema = Graph->GetSchema();

	for (const FBPPinPair& Pair : LinksToCreate)
	{
		if (Schema)
		{
			Schema->TryCreateConnection(Pair.FromPin, Pair.ToPin);
		}
		else
		{
			Pair.FromPin->MakeLinkTo(Pair.ToPin);
		}

		Result.LinksAdded.Add(FString::Printf(TEXT("%s.%s -> %s.%s"),
			*Pair.FromPin->GetOwningNode()->GetName(), *Pair.FromPin->PinName.ToString(),
			*Pair.ToPin->GetOwningNode()->GetName(), *Pair.ToPin->PinName.ToString()));
	}

	// Phase 7: Recompile
	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);

	return Result;
}

// ---- Node Matching ----

void FBlueprintGraphDiffer::MatchNodes(
	const FNodeCodeGraphIR& OldIR,
	const FNodeCodeGraphIR& NewIR,
	TMap<int32, int32>& OutNewToOld)
{
	TMap<FGuid, int32> OldGuidMap;
	for (int32 i = 0; i < OldIR.Nodes.Num(); ++i)
	{
		if (OldIR.Nodes[i].Guid.IsValid())
		{
			OldGuidMap.Add(OldIR.Nodes[i].Guid, i);
		}
	}

	TSet<int32> MatchedOld;

	// Pass 1: GUID
	for (int32 NewIdx = 0; NewIdx < NewIR.Nodes.Num(); ++NewIdx)
	{
		const FNodeCodeNodeIR& NewNode = NewIR.Nodes[NewIdx];
		if (NewNode.Guid.IsValid())
		{
			if (int32* OldIdx = OldGuidMap.Find(NewNode.Guid))
			{
				if (!MatchedOld.Contains(*OldIdx))
				{
					OutNewToOld.Add(NewIdx, *OldIdx);
					MatchedOld.Add(*OldIdx);
				}
			}
		}
	}

	// Pass 2: ClassName + Properties fingerprint
	for (int32 NewIdx = 0; NewIdx < NewIR.Nodes.Num(); ++NewIdx)
	{
		if (OutNewToOld.Contains(NewIdx))
		{
			continue;
		}

		const FNodeCodeNodeIR& NewNode = NewIR.Nodes[NewIdx];

		for (int32 OldIdx = 0; OldIdx < OldIR.Nodes.Num(); ++OldIdx)
		{
			if (MatchedOld.Contains(OldIdx))
			{
				continue;
			}

			const FNodeCodeNodeIR& OldNode = OldIR.Nodes[OldIdx];
			if (OldNode.ClassName != NewNode.ClassName)
			{
				continue;
			}

			bool bPropsMatch = true;
			for (const auto& Pair : NewNode.Properties)
			{
				const FString* OldVal = OldNode.Properties.Find(Pair.Key);
				if (OldVal && *OldVal != Pair.Value)
				{
					bPropsMatch = false;
					break;
				}
			}

			if (bPropsMatch)
			{
				OutNewToOld.Add(NewIdx, OldIdx);
				MatchedOld.Add(OldIdx);
				break;
			}
		}
	}

	// Pass 3: ClassName alone
	TMultiMap<FString, int32> UnmatchedOldByClass;
	for (int32 OldIdx = 0; OldIdx < OldIR.Nodes.Num(); ++OldIdx)
	{
		if (!MatchedOld.Contains(OldIdx))
		{
			UnmatchedOldByClass.Add(OldIR.Nodes[OldIdx].ClassName, OldIdx);
		}
	}

	for (int32 NewIdx = 0; NewIdx < NewIR.Nodes.Num(); ++NewIdx)
	{
		if (OutNewToOld.Contains(NewIdx))
		{
			continue;
		}

		const FString& ClassName = NewIR.Nodes[NewIdx].ClassName;
		for (auto It = UnmatchedOldByClass.CreateKeyIterator(ClassName); It; ++It)
		{
			int32 OldIdx = It.Value();
			OutNewToOld.Add(NewIdx, OldIdx);
			MatchedOld.Add(OldIdx);
			It.RemoveCurrent();
			break;
		}
	}
}

// ---- Property Changes ----

void FBlueprintGraphDiffer::ApplyPropertyChanges(
	UEdGraphNode* Node,
	const TMap<FString, FString>& NewProperties,
	TArray<FString>& OutChanges)
{
	UClass* NodeClass = Node->GetClass();

	for (const auto& Pair : NewProperties)
	{
		if (Pair.Key.StartsWith(TEXT("pin.")))
		{
			continue;
		}

		FProperty* Prop = NodeClass->FindPropertyByName(FName(*Pair.Key));
		if (!Prop)
		{
			OutChanges.Add(FString::Printf(TEXT("Property not found: %s"), *Pair.Key));
			continue;
		}

		void* ValuePtr = Prop->ContainerPtrToValuePtr<void>(Node);

		FString OldValue;
		Prop->ExportTextItem_Direct(OldValue, ValuePtr, nullptr, Node, PPF_None, nullptr);

		FString ImportValue = Pair.Value;
		if (ImportValue.StartsWith(TEXT("\"")) && ImportValue.EndsWith(TEXT("\"")))
		{
			ImportValue = ImportValue.Mid(1, ImportValue.Len() - 2);
			ImportValue = ImportValue.ReplaceEscapedCharWithChar();
		}

		const TCHAR* Buffer = *ImportValue;
		const TCHAR* ImportResult = Prop->ImportText_Direct(Buffer, ValuePtr, Node, PPF_None, GWarn);

		if (ImportResult)
		{
			FString NewValue;
			Prop->ExportTextItem_Direct(NewValue, ValuePtr, nullptr, Node, PPF_None, nullptr);
			if (OldValue != NewValue)
			{
				OutChanges.Add(FString::Printf(TEXT("%s: %s -> %s"), *Pair.Key, *OldValue, *NewValue));
			}
		}
		else
		{
			OutChanges.Add(FString::Printf(TEXT("Failed to import %s = %s"), *Pair.Key, *Pair.Value));
		}
	}
}

void FBlueprintGraphDiffer::ApplyPinDefaults(
	UEdGraphNode* Node,
	const TMap<FString, FString>& Properties,
	TArray<FString>& OutChanges)
{
	const UEdGraphSchema_K2* K2Schema = Cast<UEdGraphSchema_K2>(Node->GetGraph()->GetSchema());

	for (const auto& Pair : Properties)
	{
		if (!Pair.Key.StartsWith(TEXT("pin.")))
		{
			continue;
		}

		FString EncodedPinName = Pair.Key.Mid(4);
		UEdGraphPin* Pin = FindPinByName(Node, EncodedPinName, EGPD_Input);
		if (!Pin)
		{
			OutChanges.Add(FString::Printf(TEXT("Pin not found: %s"), *EncodedPinName));
			continue;
		}

		if (K2Schema)
		{
			K2Schema->TrySetDefaultValue(*Pin, Pair.Value);
		}
		else
		{
			Pin->DefaultValue = Pair.Value;
		}

		OutChanges.Add(FString::Printf(TEXT("pin.%s: %s"), *EncodedPinName, *Pair.Value));
	}
}

UEdGraphPin* FBlueprintGraphDiffer::FindPinByName(UEdGraphNode* Node, const FString& PinName, EEdGraphPinDirection Direction)
{
	for (UEdGraphPin* Pin : Node->Pins)
	{
		if (Pin && Pin->Direction == Direction && NodeCodeUtils::MatchName(PinName, Pin->PinName.ToString()))
		{
			return Pin;
		}
	}
	return nullptr;
}
