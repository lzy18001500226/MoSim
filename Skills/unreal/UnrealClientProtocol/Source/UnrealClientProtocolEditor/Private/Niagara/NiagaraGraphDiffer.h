// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "NodeCode/NodeCodeTypes.h"
#include "NiagaraCommon.h"

class UNiagaraGraph;
class UNiagaraNode;

class FNiagaraGraphDiffer
{
public:
	static FNodeCodeDiffResult Apply(UNiagaraGraph* Graph, ENiagaraScriptUsage Usage, FGuid UsageId, const FNodeCodeGraphIR& NewIR);

private:
	static void MatchNodes(
		const FNodeCodeGraphIR& OldIR,
		const FNodeCodeGraphIR& NewIR,
		TMap<int32, int32>& OutNewToOld);

	static void ApplyPropertyChanges(
		UNiagaraNode* Node,
		const TMap<FString, FString>& NewProperties,
		TArray<FString>& OutChanges);

	static UEdGraphPin* FindPinByName(UEdGraphNode* Node, const FString& PinName, EEdGraphPinDirection Direction);
};
