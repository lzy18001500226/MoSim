// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "NodeCode/NodeCodeTypes.h"

class UMaterial;
class UMaterialFunction;
class UMaterialExpression;
class UMaterialExpressionComposite;
struct FExpressionOutput;

class FMaterialGraphSerializer
{
public:
	static FNodeCodeGraphIR BuildIR(UMaterial* Material);
	static FNodeCodeGraphIR BuildCompositeIR(UMaterial* Material, const FString& CompositeName);
	static FNodeCodeGraphIR BuildIR(UMaterialFunction* MaterialFunction);

	static TArray<FNodeCodeSectionIR> ListSections(UMaterial* Material);
	static TArray<FNodeCodeSectionIR> ListSections(UMaterialFunction* MaterialFunction);

	static TMap<FString, FString> ReadMaterialProperties(UMaterial* Material);

	static void CollectAllConnectedNodes(
		UMaterial* Material,
		TSet<UMaterialExpression*>& OutReachable);

private:
	static FNodeCodeGraphIR BuildIRFromExpressions(
		TConstArrayView<TObjectPtr<UMaterialExpression>> AllExpressions,
		UMaterial* Material,
		UMaterialFunction* MaterialFunction,
		UMaterialExpressionComposite* TargetComposite);

	static void CollectReachableNodes(
		UMaterialExpression* StartExpr,
		TSet<UMaterialExpression*>& OutReachable,
		TSet<UMaterialExpression*>& Visited);

	static void SerializeNodeProperties(
		UMaterialExpression* Expression,
		TMap<FString, FString>& OutProperties);

	static FString GetOutputPinName(
		UMaterialExpression* Expression,
		int32 OutputIndex);

	static FString ShortenInputPinName(const FString& InputName);

	static bool IsConnectionProperty(const FProperty* Prop);
	static bool IsEmbeddedConnectionArrayProperty(const FProperty* Prop);
};
