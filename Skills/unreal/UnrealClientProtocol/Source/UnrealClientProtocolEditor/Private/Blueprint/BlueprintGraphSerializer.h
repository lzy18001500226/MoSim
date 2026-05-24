// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "NodeCode/NodeCodeTypes.h"

class UBlueprint;
class UEdGraph;
class UEdGraphNode;

class FBlueprintGraphSerializer
{
public:
	static FNodeCodeGraphIR BuildIR(UEdGraph* Graph);

	static TArray<FNodeCodeSectionIR> ListSections(UBlueprint* Blueprint);

	static UEdGraph* FindGraphBySection(UBlueprint* Blueprint, const FString& Type, const FString& Name);

private:
	static void SerializeNodeProperties(UEdGraphNode* Node, TMap<FString, FString>& OutProperties);
	static void SerializePinDefaults(UEdGraphNode* Node, TMap<FString, FString>& OutProperties);
	static bool ShouldSkipNode(UEdGraphNode* Node);
};
