// MIT License - Copyright (c) 2025 Italink

#include "Niagara/NiagaraGraphDiffer.h"
#include "Niagara/NiagaraGraphSerializer.h"
#include "Niagara/INiagaraNodeEncoder.h"
#include "NodeCode/NodeCodeTypes.h"

#include "NiagaraGraph.h"
#include "NiagaraNode.h"
#include "NiagaraNodeOutput.h"
#include "EdGraph/EdGraph.h"
#include "EdGraph/EdGraphPin.h"
#include "ScopedTransaction.h"
#include "UObject/UnrealType.h"

DEFINE_LOG_CATEGORY_STATIC(LogNiagaraDiffer, Log, All);

struct FNiagaraPinPair
{
	UEdGraphPin* FromPin = nullptr;
	UEdGraphPin* ToPin = nullptr;

	bool operator==(const FNiagaraPinPair& Other) const { return FromPin == Other.FromPin && ToPin == Other.ToPin; }
	friend uint32 GetTypeHash(const FNiagaraPinPair& P) { return HashCombine(::GetTypeHash(P.FromPin), ::GetTypeHash(P.ToPin)); }
};

FNodeCodeDiffResult FNiagaraGraphDiffer::Apply(UNiagaraGraph* Graph, ENiagaraScriptUsage Usage, FGuid UsageId, const FNodeCodeGraphIR& NewIR)
{
	FNodeCodeDiffResult Result;

	if (!Graph)
	{
		UE_LOG(LogNiagaraDiffer, Error, TEXT("Apply: Graph is null"));
		return Result;
	}

	FNodeCodeGraphIR OldIR = FNiagaraGraphSerializer::BuildIR(Graph, Usage, UsageId);

	TMap<int32, int32> NewToOld;
	MatchNodes(OldIR, NewIR, NewToOld);

	TSet<int32> MatchedOldIndices;
	for (auto& Pair : NewToOld)
	{
		MatchedOldIndices.Add(Pair.Value);
	}

	FScopedTransaction Transaction(NSLOCTEXT("UCPNiagara", "WriteGraph", "UCP: Write Niagara Graph"));
	Graph->Modify();

	// Phase 1: Delete unmatched old nodes (skip Output nodes)
	for (int32 OldIdx = 0; OldIdx < OldIR.Nodes.Num(); ++OldIdx)
	{
		if (MatchedOldIndices.Contains(OldIdx)) continue;

		const FNodeCodeNodeIR& OldNode = OldIR.Nodes[OldIdx];
		UNiagaraNode* OldGraphNode = Cast<UNiagaraNode>(OldNode.SourceObject);
		if (!OldGraphNode) continue;

		if (OldGraphNode->IsA<UNiagaraNodeOutput>()) continue;

		Graph->RemoveNode(OldGraphNode);
		Result.NodesRemoved.Add(FString::Printf(TEXT("N_%s %s"), *OldNode.Index, *OldNode.ClassName));
	}

	// Phase 2: Create new nodes
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
			UNiagaraNode* CreatedNode = FNiagaraNodeEncoderRegistry::Get().DecodeNode(NewNode.ClassName, Graph, NewNode);
			if (CreatedNode)
			{
				NewIndexToNode.Add(NewNode.Index, CreatedNode);
				Result.NodesAdded.Add(FString::Printf(TEXT("N_%s %s"), *NewNode.Index, *NewNode.ClassName));
			}
			else
			{
				UE_LOG(LogNiagaraDiffer, Error, TEXT("WriteGraph: Failed to create node: %s"), *NewNode.ClassName);
			}
		}
	}

	// Phase 3: Update properties on matched nodes
	for (int32 NewIdx = 0; NewIdx < NewIR.Nodes.Num(); ++NewIdx)
	{
		int32* OldIdx = NewToOld.Find(NewIdx);
		if (!OldIdx) continue;

		const FNodeCodeNodeIR& NewNode = NewIR.Nodes[NewIdx];
		const FNodeCodeNodeIR& OldNode = OldIR.Nodes[*OldIdx];
		UNiagaraNode* GraphNode = Cast<UNiagaraNode>(OldNode.SourceObject);
		if (!GraphNode) continue;

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
			if (Changes.Num() > 0)
			{
				Result.NodesModified.Add(FString::Printf(TEXT("N_%s: %s"), *NewNode.Index, *FString::Join(Changes, TEXT("; "))));
			}
		}
	}

	// Phase 4: Connection diff
	TSet<FNiagaraPinPair> DesiredLinks;
	TArray<FNiagaraPinPair> LinksToCreate;

	UNiagaraNodeOutput* OutputNode = Graph->FindEquivalentOutputNode(Usage, UsageId);

	for (const FNodeCodeLinkIR& Link : NewIR.Links)
	{
		UEdGraphNode** FromNodePtr = NewIndexToNode.Find(Link.FromNodeIndex);
		if (!FromNodePtr || !*FromNodePtr)
		{
			UE_LOG(LogNiagaraDiffer, Warning, TEXT("Link skip: FromNode N_%s not found in NewIndexToNode"), *Link.FromNodeIndex);
			continue;
		}

		UEdGraphNode* ToNode = nullptr;
		if (Link.bToGraphOutput)
		{
			ToNode = OutputNode;
			if (!ToNode)
			{
				UE_LOG(LogNiagaraDiffer, Warning, TEXT("Link skip: OutputNode is null for bToGraphOutput link"));
			}
		}
		else
		{
			UEdGraphNode** ToNodePtr = NewIndexToNode.Find(Link.ToNodeIndex);
			if (ToNodePtr) ToNode = *ToNodePtr;
			if (!ToNode)
			{
				UE_LOG(LogNiagaraDiffer, Warning, TEXT("Link skip: ToNode N_%s not found in NewIndexToNode"), *Link.ToNodeIndex);
			}
		}
		if (!ToNode) continue;

		UEdGraphPin* FromPin = FindPinByName(*FromNodePtr, Link.FromOutputName, EGPD_Output);
		UEdGraphPin* ToPin = FindPinByName(ToNode, Link.ToInputName, EGPD_Input);
		if (!FromPin || !ToPin)
		{
			UE_LOG(LogNiagaraDiffer, Warning, TEXT("Link skip: Pin not found. From='%s'(%s) To='%s'(%s) FromNode=%s ToNode=%s"),
				*Link.FromOutputName, FromPin ? TEXT("OK") : TEXT("MISSING"),
				*Link.ToInputName, ToPin ? TEXT("OK") : TEXT("MISSING"),
				*(*FromNodePtr)->GetClass()->GetName(),
				*ToNode->GetClass()->GetName());
			if (!FromPin)
			{
				for (UEdGraphPin* Pin : (*FromNodePtr)->Pins)
				{
					if (Pin && Pin->Direction == EGPD_Output)
						UE_LOG(LogNiagaraDiffer, Warning, TEXT("  Available output pin: '%s'"), *Pin->PinName.ToString());
				}
			}
			if (!ToPin)
			{
				for (UEdGraphPin* Pin : ToNode->Pins)
				{
					if (Pin && Pin->Direction == EGPD_Input)
						UE_LOG(LogNiagaraDiffer, Warning, TEXT("  Available input pin: '%s'"), *Pin->PinName.ToString());
				}
			}
			continue;
		}

		FNiagaraPinPair Pair{FromPin, ToPin};
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
				FNiagaraPinPair LivePair{Pin, LinkedPin};
				if (!DesiredLinks.Contains(LivePair))
				{
					LinksToBreak.Add(LinkedPin);
				}
			}
			for (UEdGraphPin* LinkedPin : LinksToBreak)
			{
				Pin->BreakLinkTo(LinkedPin);
				Result.LinksRemoved.Add(FString::Printf(TEXT("%s -> %s"),
					*Pin->PinName.ToString(), *LinkedPin->PinName.ToString()));
			}
		}
	}

	const UEdGraphSchema* Schema = Graph->GetSchema();
	for (const FNiagaraPinPair& Pair : LinksToCreate)
	{
		if (Schema)
		{
			Schema->TryCreateConnection(Pair.FromPin, Pair.ToPin);
		}
		else
		{
			Pair.FromPin->MakeLinkTo(Pair.ToPin);
		}
		Result.LinksAdded.Add(FString::Printf(TEXT("%s -> %s"),
			*Pair.FromPin->PinName.ToString(), *Pair.ToPin->PinName.ToString()));
	}

	// Phase 5: Post-processing
	Graph->NotifyGraphChanged();
	Graph->MarkPackageDirty();

	return Result;
}

// ---- Node Matching ----

void FNiagaraGraphDiffer::MatchNodes(
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

	// Pass 1: GUID match
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

	// Pass 2: ClassName fallback for unmatched
	for (int32 NewIdx = 0; NewIdx < NewIR.Nodes.Num(); ++NewIdx)
	{
		if (OutNewToOld.Contains(NewIdx)) continue;

		const FNodeCodeNodeIR& NewNode = NewIR.Nodes[NewIdx];

		for (int32 OldIdx = 0; OldIdx < OldIR.Nodes.Num(); ++OldIdx)
		{
			if (MatchedOld.Contains(OldIdx)) continue;

			const FNodeCodeNodeIR& OldNode = OldIR.Nodes[OldIdx];
			if (OldNode.ClassName == NewNode.ClassName)
			{
				OutNewToOld.Add(NewIdx, OldIdx);
				MatchedOld.Add(OldIdx);
				break;
			}
		}
	}
}

// ---- Property Changes ----

void FNiagaraGraphDiffer::ApplyPropertyChanges(
	UNiagaraNode* Node,
	const TMap<FString, FString>& NewProperties,
	TArray<FString>& OutChanges)
{
	if (!Node) return;

	UClass* NodeClass = Node->GetClass();

	for (const auto& Pair : NewProperties)
	{
		FProperty* Prop = NodeClass->FindPropertyByName(FName(*Pair.Key));
		if (!Prop) continue;

		void* ValuePtr = Prop->ContainerPtrToValuePtr<void>(Node);
		FString CurrentValue;
		Prop->ExportTextItem_Direct(CurrentValue, ValuePtr, nullptr, Node, PPF_None, nullptr);

		if (CurrentValue != Pair.Value)
		{
			Prop->ImportText_Direct(*Pair.Value, ValuePtr, Node, PPF_None);
			OutChanges.Add(FString::Printf(TEXT("%s: %s -> %s"), *Pair.Key, *CurrentValue, *Pair.Value));
		}
	}
}

// ---- Pin Lookup ----

UEdGraphPin* FNiagaraGraphDiffer::FindPinByName(UEdGraphNode* Node, const FString& PinName, EEdGraphPinDirection Direction)
{
	if (!Node) return nullptr;

	for (UEdGraphPin* Pin : Node->Pins)
	{
		if (Pin && Pin->Direction == Direction && Pin->PinName.ToString() == PinName)
		{
			return Pin;
		}
	}

	for (UEdGraphPin* Pin : Node->Pins)
	{
		if (Pin && Pin->Direction == Direction && Pin->PinName.ToString().EndsWith(PinName))
		{
			return Pin;
		}
	}

	return nullptr;
}
