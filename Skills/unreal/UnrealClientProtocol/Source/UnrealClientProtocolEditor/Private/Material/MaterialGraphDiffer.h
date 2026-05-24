// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "NodeCode/NodeCodeTypes.h"

class UMaterial;
class UMaterialFunction;
class UMaterialExpression;

class FMaterialGraphDiffer
{
public:
	static FNodeCodeDiffResult ApplyMaterial(UMaterial* Material, const FNodeCodeGraphIR& NewIR);
	static FNodeCodeDiffResult ApplyComposite(UMaterial* Material, const FString& CompositeName, const FNodeCodeGraphIR& NewIR);
	static FNodeCodeDiffResult ApplyFunction(UMaterialFunction* MaterialFunction, const FNodeCodeGraphIR& NewIR);

	static FNodeCodeDiffResult ApplyMaterialProperties(UMaterial* Material, const TMap<FString, FString>& Properties);

private:
	static FNodeCodeDiffResult DiffAndApply(
		UMaterial* Material,
		UMaterialFunction* MaterialFunction,
		const FString& CompositeName,
		FNodeCodeGraphIR NewIR);

	static void MatchNodes(
		const FNodeCodeGraphIR& OldIR,
		const FNodeCodeGraphIR& NewIR,
		TMap<int32, int32>& OutNewToOld);

	static void ApplyPropertyChanges(
		UMaterialExpression* Expression,
		const TMap<FString, FString>& NewProperties,
		TArray<FString>& OutChanges);

	static EMaterialProperty FindMaterialPropertyByName(UMaterial* Material, const FString& Name);
};
