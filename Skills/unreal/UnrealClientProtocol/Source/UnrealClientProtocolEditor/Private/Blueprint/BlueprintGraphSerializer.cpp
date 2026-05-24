// MIT License - Copyright (c) 2025 Italink

#include "Blueprint/BlueprintGraphSerializer.h"
#include "Blueprint/IBlueprintNodeEncoder.h"
#include "NodeCode/NodeCodePropertyUtils.h"
#include "NodeCode/NodeCodeTypes.h"

#include "Engine/Blueprint.h"
#include "EdGraph/EdGraph.h"
#include "EdGraph/EdGraphNode.h"
#include "EdGraph/EdGraphPin.h"
#include "EdGraphNode_Comment.h"
#include "K2Node.h"
#include "K2Node_Knot.h"
#include "K2Node_FunctionEntry.h"
#include "K2Node_FunctionResult.h"
#include "EdGraphSchema_K2.h"
#include "UObject/UnrealType.h"

TArray<FNodeCodeSectionIR> FBlueprintGraphSerializer::ListSections(UBlueprint* Blueprint)
{
	TArray<FNodeCodeSectionIR> Sections;
	if (!Blueprint)
	{
		return Sections;
	}

	{
		FNodeCodeSectionIR VarSection;
		VarSection.Type = TEXT("Variables");
		Sections.Add(MoveTemp(VarSection));
	}

	for (UEdGraph* Graph : Blueprint->UbergraphPages)
	{
		if (Graph)
		{
			FNodeCodeSectionIR Section;
			Section.Type = TEXT("EventGraph");
			Section.Name = (Blueprint->UbergraphPages.Num() > 1) ? NodeCodeUtils::EncodeSpaces(Graph->GetName()) : FString();
			Sections.Add(MoveTemp(Section));
		}
	}

	for (UEdGraph* Graph : Blueprint->FunctionGraphs)
	{
		if (Graph)
		{
			FNodeCodeSectionIR Section;
			Section.Type = TEXT("Function");
			Section.Name = NodeCodeUtils::EncodeSpaces(Graph->GetName());
			Sections.Add(MoveTemp(Section));
		}
	}

	for (UEdGraph* Graph : Blueprint->MacroGraphs)
	{
		if (Graph)
		{
			FNodeCodeSectionIR Section;
			Section.Type = TEXT("Macro");
			Section.Name = NodeCodeUtils::EncodeSpaces(Graph->GetName());
			Sections.Add(MoveTemp(Section));
		}
	}

	return Sections;
}

UEdGraph* FBlueprintGraphSerializer::FindGraphBySection(UBlueprint* Blueprint, const FString& Type, const FString& Name)
{
	if (!Blueprint)
	{
		return nullptr;
	}

	auto SearchGraphArray = [&Name](const TArray<TObjectPtr<UEdGraph>>& Graphs) -> UEdGraph*
	{
		for (const TObjectPtr<UEdGraph>& Graph : Graphs)
		{
			if (Graph && NodeCodeUtils::MatchName(Name, Graph->GetName()))
			{
				return Graph.Get();
			}
		}
		return nullptr;
	};

	if (Type == TEXT("Function"))
	{
		return SearchGraphArray(Blueprint->FunctionGraphs);
	}
	if (Type == TEXT("Macro"))
	{
		return SearchGraphArray(Blueprint->MacroGraphs);
	}
	if (Type == TEXT("EventGraph"))
	{
		if (Name.IsEmpty() && Blueprint->UbergraphPages.Num() > 0)
		{
			return Blueprint->UbergraphPages[0];
		}
		return SearchGraphArray(Blueprint->UbergraphPages);
	}

	return nullptr;
}

FNodeCodeGraphIR FBlueprintGraphSerializer::BuildIR(UEdGraph* Graph)
{
	FNodeCodeGraphIR IR;
	if (!Graph)
	{
		return IR;
	}

	TMap<UEdGraphNode*, FString> NodeToIndex;

	for (UEdGraphNode* Node : Graph->Nodes)
	{
		if (!Node || ShouldSkipNode(Node))
		{
			continue;
		}

		FNodeCodeNodeIR NodeIR;
		FString NodeId = NodeCodeUtils::GuidToBase62(Node->NodeGuid);
		NodeIR.Index = NodeId;
		NodeIR.SourceObject = Node;
		NodeIR.Guid = Node->NodeGuid;
		NodeIR.ClassName = FBlueprintNodeEncoderRegistry::Get().EncodeNode(Node);

		SerializeNodeProperties(Node, NodeIR.Properties);
		SerializePinDefaults(Node, NodeIR.Properties);

		NodeToIndex.Add(Node, NodeId);
		IR.Nodes.Add(MoveTemp(NodeIR));
	}

	for (UEdGraphNode* Node : Graph->Nodes)
	{
		if (!Node || ShouldSkipNode(Node))
		{
			continue;
		}

		FString* ToId = NodeToIndex.Find(Node);
		if (!ToId)
		{
			continue;
		}

		for (UEdGraphPin* Pin : Node->Pins)
		{
			if (!Pin || Pin->Direction != EGPD_Input)
			{
				continue;
			}

			for (UEdGraphPin* LinkedPin : Pin->LinkedTo)
			{
				if (!LinkedPin || !LinkedPin->GetOwningNode())
				{
					continue;
				}

				UEdGraphNode* FromNode = LinkedPin->GetOwningNode();

				while (UK2Node_Knot* Knot = Cast<UK2Node_Knot>(FromNode))
				{
					UEdGraphPin* KnotInput = Knot->GetInputPin();
					if (KnotInput && KnotInput->LinkedTo.Num() > 0)
					{
						LinkedPin = KnotInput->LinkedTo[0];
						FromNode = LinkedPin->GetOwningNode();
					}
					else
					{
						FromNode = nullptr;
						break;
					}
				}

				if (!FromNode)
				{
					continue;
				}

				FString* FromId = NodeToIndex.Find(FromNode);
				if (!FromId)
				{
					continue;
				}

				FNodeCodeLinkIR Link;
				Link.FromNodeIndex = *FromId;
				Link.FromOutputName = NodeCodeUtils::EncodeSpaces(LinkedPin->PinName.ToString());
				Link.ToNodeIndex = *ToId;
				Link.ToInputName = NodeCodeUtils::EncodeSpaces(Pin->PinName.ToString());
				Link.bToGraphOutput = false;
				IR.Links.Add(MoveTemp(Link));
			}
		}
	}

	return IR;
}

bool FBlueprintGraphSerializer::ShouldSkipNode(UEdGraphNode* Node)
{
	if (Cast<UEdGraphNode_Comment>(Node))
	{
		return true;
	}
	if (Cast<UK2Node_Knot>(Node))
	{
		return true;
	}
	return false;
}

void FBlueprintGraphSerializer::SerializeNodeProperties(
	UEdGraphNode* Node,
	TMap<FString, FString>& OutProperties)
{
	UClass* NodeClass = Node->GetClass();
	UObject* CDO = NodeClass->GetDefaultObject();
	const TSet<FName>& SkipSet = FNodeCodePropertyUtils::GetEdGraphNodeSkipSet();

	for (TFieldIterator<FProperty> PropIt(NodeClass); PropIt; ++PropIt)
	{
		FProperty* Prop = *PropIt;

		if (FNodeCodePropertyUtils::ShouldSkipProperty(Prop))
		{
			continue;
		}

		if (SkipSet.Contains(Prop->GetFName()))
		{
			continue;
		}

		const void* InstanceValue = Prop->ContainerPtrToValuePtr<void>(Node);
		const void* CDOValue = Prop->ContainerPtrToValuePtr<void>(CDO);

		if (Prop->Identical(InstanceValue, CDOValue, PPF_None))
		{
			continue;
		}

		FString ValueStr = FNodeCodePropertyUtils::FormatPropertyValue(Prop, InstanceValue, Node);
		OutProperties.Add(Prop->GetName(), MoveTemp(ValueStr));
	}
}

void FBlueprintGraphSerializer::SerializePinDefaults(
	UEdGraphNode* Node,
	TMap<FString, FString>& OutProperties)
{
	for (UEdGraphPin* Pin : Node->Pins)
	{
		if (!Pin || Pin->Direction != EGPD_Input)
		{
			continue;
		}

		if (Pin->bHidden || Pin->LinkedTo.Num() > 0)
		{
			continue;
		}

		if (Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Exec)
		{
			continue;
		}

		FString DefaultValue;
		if (Pin->DefaultObject)
		{
			DefaultValue = Pin->DefaultObject->GetPathName();
		}
		else if (!Pin->DefaultValue.IsEmpty())
		{
			DefaultValue = Pin->DefaultValue;
		}
		else if (!Pin->DefaultTextValue.IsEmpty())
		{
			DefaultValue = Pin->DefaultTextValue.ToString();
		}
		else if (!Pin->AutogeneratedDefaultValue.IsEmpty())
		{
			continue;
		}
		else
		{
			continue;
		}

		FString EncodedPinName = NodeCodeUtils::EncodeSpaces(Pin->PinName.ToString());
		FString PinKey = FString::Printf(TEXT("pin.%s"), *EncodedPinName);
		OutProperties.Add(PinKey, DefaultValue);
	}
}
