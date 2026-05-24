// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "NodeCode/NodeCodeTypes.h"
#include "EdGraph/EdGraphPin.h"

class UBlueprint;
class UEdGraph;
class UEdGraphNode;

class FBlueprintGraphDiffer
{
public:
	static FNodeCodeDiffResult Apply(UBlueprint* Blueprint, UEdGraph* Graph, const FNodeCodeGraphIR& NewIR);

private:
	static void MatchNodes(
		const FNodeCodeGraphIR& OldIR,
		const FNodeCodeGraphIR& NewIR,
		TMap<int32, int32>& OutNewToOld);

	static void ApplyPropertyChanges(
		UEdGraphNode* Node,
		const TMap<FString, FString>& NewProperties,
		TArray<FString>& OutChanges);

	static void ApplyPinDefaults(
		UEdGraphNode* Node,
		const TMap<FString, FString>& Properties,
		TArray<FString>& OutChanges);

	static UEdGraphPin* FindPinByName(UEdGraphNode* Node, const FString& PinName, EEdGraphPinDirection Direction);
};
