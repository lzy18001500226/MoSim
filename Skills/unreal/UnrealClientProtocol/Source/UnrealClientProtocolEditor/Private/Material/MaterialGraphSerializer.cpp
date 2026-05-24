// MIT License - Copyright (c) 2025 Italink

#include "Material/MaterialGraphSerializer.h"
#include "NodeCode/NodeCodeClassCache.h"
#include "Material/IMaterialPropertyHandler.h"
#include "NodeCode/NodeCodeTextFormat.h"
#include "NodeCode/NodeCodePropertyUtils.h"

#include "Materials/Material.h"
#include "Materials/MaterialFunction.h"
#include "Materials/MaterialExpression.h"
#include "Materials/MaterialExpressionComment.h"
#include "Materials/MaterialExpressionComposite.h"
#include "Materials/MaterialExpressionReroute.h"
#include "Materials/MaterialExpressionRerouteBase.h"
#include "Materials/MaterialExpressionCustomOutput.h"
#include "Materials/MaterialExpressionMaterialFunctionCall.h"
#include "Materials/MaterialExpressionCustom.h"
#include "Materials/MaterialExpressionSwitch.h"
#include "Materials/MaterialExpressionSetMaterialAttributes.h"
#include "Materials/MaterialAttributeDefinitionMap.h"
#include "UObject/UnrealType.h"

static UMaterialExpression* TraceReroute(FExpressionInput* Input, int32& OutOutputIndex)
{
	if (!Input || !Input->Expression)
	{
		return nullptr;
	}

	if (UMaterialExpressionRerouteBase* Reroute = Cast<UMaterialExpressionRerouteBase>(Input->Expression))
	{
		return Reroute->TraceInputsToRealExpression(OutOutputIndex);
	}

	OutOutputIndex = Input->OutputIndex;
	return Input->Expression;
}

// ---- List Sections ----

TArray<FNodeCodeSectionIR> FMaterialGraphSerializer::ListSections(UMaterial* Material)
{
	TArray<FNodeCodeSectionIR> Sections;
	if (!Material)
	{
		return Sections;
	}

	{
		FNodeCodeSectionIR PropSection;
		PropSection.Type = TEXT("Properties");
		Sections.Add(MoveTemp(PropSection));
	}

	{
		FNodeCodeSectionIR MatSection;
		MatSection.Type = TEXT("Material");
		Sections.Add(MoveTemp(MatSection));
	}

	TConstArrayView<TObjectPtr<UMaterialExpression>> Expressions = Material->GetExpressions();
	for (const TObjectPtr<UMaterialExpression>& Expr : Expressions)
	{
		if (UMaterialExpressionComposite* Composite = Cast<UMaterialExpressionComposite>(Expr.Get()))
		{
			if (!Composite->SubgraphName.IsEmpty())
			{
				FNodeCodeSectionIR CompSection;
				CompSection.Type = TEXT("Composite");
				CompSection.Name = Composite->SubgraphName;
				Sections.Add(MoveTemp(CompSection));
			}
		}
	}

	return Sections;
}

TArray<FNodeCodeSectionIR> FMaterialGraphSerializer::ListSections(UMaterialFunction* MaterialFunction)
{
	TArray<FNodeCodeSectionIR> Sections;
	if (!MaterialFunction)
	{
		return Sections;
	}

	FNodeCodeSectionIR MatSection;
	MatSection.Type = TEXT("Material");
	Sections.Add(MoveTemp(MatSection));

	return Sections;
}

// ---- Read Properties ----

TMap<FString, FString> FMaterialGraphSerializer::ReadMaterialProperties(UMaterial* Material)
{
	TMap<FString, FString> Props;
	if (!Material)
	{
		return Props;
	}

	UClass* MatClass = Material->GetClass();
	UObject* CDO = MatClass->GetDefaultObject();

	static const TArray<FName> PropertyNames = {
		TEXT("ShadingModel"),
		TEXT("BlendMode"),
		TEXT("MaterialDomain"),
		TEXT("TwoSided"),
		TEXT("OpacityMaskClipValue"),
		TEXT("bUseMaterialAttributes"),
		TEXT("DecalBlendMode"),
		TEXT("TranslucencyLightingMode"),
	};

	for (const FName& PropName : PropertyNames)
	{
		FProperty* Prop = MatClass->FindPropertyByName(PropName);
		if (!Prop)
		{
			continue;
		}

		const void* InstanceValue = Prop->ContainerPtrToValuePtr<void>(Material);
		const void* CDOValue = Prop->ContainerPtrToValuePtr<void>(CDO);

		if (!Prop->Identical(InstanceValue, CDOValue, PPF_None))
		{
			FString ValueStr = FNodeCodePropertyUtils::FormatPropertyValue(Prop, InstanceValue, Material);
			Props.Add(PropName.ToString(), MoveTemp(ValueStr));
		}
	}

	return Props;
}

// ---- Build IR ----

FNodeCodeGraphIR FMaterialGraphSerializer::BuildIR(UMaterial* Material)
{
	if (!Material)
	{
		return {};
	}

	TConstArrayView<TObjectPtr<UMaterialExpression>> Expressions = Material->GetExpressions();
	return BuildIRFromExpressions(Expressions, Material, nullptr, nullptr);
}

FNodeCodeGraphIR FMaterialGraphSerializer::BuildCompositeIR(UMaterial* Material, const FString& CompositeName)
{
	if (!Material)
	{
		return {};
	}

	TConstArrayView<TObjectPtr<UMaterialExpression>> Expressions = Material->GetExpressions();

	UMaterialExpressionComposite* TargetComposite = nullptr;
	for (const TObjectPtr<UMaterialExpression>& Expr : Expressions)
	{
		UMaterialExpressionComposite* Composite = Cast<UMaterialExpressionComposite>(Expr.Get());
		if (Composite && Composite->SubgraphName == CompositeName)
		{
			TargetComposite = Composite;
			break;
		}
	}

	if (!TargetComposite)
	{
		return {};
	}

	return BuildIRFromExpressions(Expressions, Material, nullptr, TargetComposite);
}

FNodeCodeGraphIR FMaterialGraphSerializer::BuildIR(UMaterialFunction* MaterialFunction)
{
	if (!MaterialFunction)
	{
		return {};
	}

	TConstArrayView<TObjectPtr<UMaterialExpression>> Expressions = MaterialFunction->GetExpressions();
	return BuildIRFromExpressions(Expressions, nullptr, MaterialFunction, nullptr);
}

void FMaterialGraphSerializer::CollectAllConnectedNodes(
	UMaterial* Material,
	TSet<UMaterialExpression*>& OutReachable)
{
	TSet<UMaterialExpression*> Visited;

	for (int32 i = 0; i < MP_MAX; ++i)
	{
		FExpressionInput* Input = Material->GetExpressionInputForProperty(static_cast<EMaterialProperty>(i));
		if (Input && Input->Expression)
		{
			int32 OutIdx;
			UMaterialExpression* RealExpr = TraceReroute(Input, OutIdx);
			if (RealExpr)
			{
				CollectReachableNodes(RealExpr, OutReachable, Visited);
			}
		}
	}

#if WITH_EDITORONLY_DATA
	TArray<UMaterialExpressionCustomOutput*> CustomOutputs;
	Material->GetAllCustomOutputExpressions(CustomOutputs);
	for (UMaterialExpressionCustomOutput* CustomOut : CustomOutputs)
	{
		CollectReachableNodes(CustomOut, OutReachable, Visited);
	}
#endif
}

FNodeCodeGraphIR FMaterialGraphSerializer::BuildIRFromExpressions(
	TConstArrayView<TObjectPtr<UMaterialExpression>> AllExpressions,
	UMaterial* Material,
	UMaterialFunction* MaterialFunction,
	UMaterialExpressionComposite* TargetComposite)
{
	FNodeCodeGraphIR IR;

	TSet<UMaterialExpression*> ReachableSet;
	bool bScopeIsComposite = (TargetComposite != nullptr);

	if (Material)
	{
		if (bScopeIsComposite)
		{
			for (const TObjectPtr<UMaterialExpression>& Expr : AllExpressions)
			{
				if (Expr && Expr->SubgraphExpression == TargetComposite)
				{
					ReachableSet.Add(Expr.Get());
				}
			}
		}
		else
		{
			CollectAllConnectedNodes(Material, ReachableSet);
		}
	}
	else if (MaterialFunction)
	{
		for (const TObjectPtr<UMaterialExpression>& Expr : AllExpressions)
		{
			if (Expr && !Cast<UMaterialExpressionComment>(Expr.Get()))
			{
				ReachableSet.Add(Expr.Get());
			}
		}
	}

	TMap<UMaterialExpression*, FString> ExprToNodeIndex;

	for (const TObjectPtr<UMaterialExpression>& Expr : AllExpressions)
	{
		if (!Expr || !ReachableSet.Contains(Expr.Get()))
		{
			continue;
		}
		if (Cast<UMaterialExpressionComment>(Expr.Get()))
		{
			continue;
		}
		if (!bScopeIsComposite && Expr->SubgraphExpression != nullptr)
		{
			continue;
		}
		if (Cast<UMaterialExpressionRerouteBase>(Expr.Get()))
		{
			continue;
		}

		FString NodeId = NodeCodeUtils::GuidToBase62(Expr->MaterialExpressionGuid);

		FNodeCodeNodeIR Node;
		Node.Index = NodeId;
		Node.SourceObject = Expr.Get();
		Node.Guid = Expr->MaterialExpressionGuid;
		Node.ClassName = FNodeCodeClassCache::Get().GetSerializableName(Expr->GetClass());

		SerializeNodeProperties(Expr.Get(), Node.Properties);

		ExprToNodeIndex.Add(Expr.Get(), NodeId);
		IR.Nodes.Add(MoveTemp(Node));
	}

	if (Material && !bScopeIsComposite)
	{
		auto AddMaterialOutputLinks = [&](EMaterialProperty Prop, const FString& PinName)
		{
			FExpressionInput* Input = Material->GetExpressionInputForProperty(Prop);
			if (!Input || !Input->Expression)
			{
				return;
			}

			int32 OutIdx;
			UMaterialExpression* RealExpr = TraceReroute(Input, OutIdx);
			if (!RealExpr)
			{
				return;
			}

			FString* FromId = ExprToNodeIndex.Find(RealExpr);
			if (!FromId)
			{
				return;
			}

			FNodeCodeLinkIR Link;
			Link.FromNodeIndex = *FromId;
			Link.FromOutputName = GetOutputPinName(RealExpr, OutIdx);
			Link.ToInputName = PinName;
			Link.bToGraphOutput = true;
			IR.Links.Add(MoveTemp(Link));
		};

		for (int32 i = 0; i < MP_MAX; ++i)
		{
			EMaterialProperty Prop = static_cast<EMaterialProperty>(i);
			FExpressionInput* Input = Material->GetExpressionInputForProperty(Prop);
			if (Input && Input->Expression)
			{
				const FString& AttrName = FMaterialAttributeDefinitionMap::GetAttributeName(Prop);
				AddMaterialOutputLinks(Prop, AttrName);
			}
		}

#if WITH_EDITORONLY_DATA
		TArray<UMaterialExpressionCustomOutput*> CustomOutputs;
		Material->GetAllCustomOutputExpressions(CustomOutputs);
		for (UMaterialExpressionCustomOutput* CustomOut : CustomOutputs)
		{
			FString* ToId = ExprToNodeIndex.Find(CustomOut);
			if (!ToId)
			{
				continue;
			}

			for (FExpressionInputIterator It(CustomOut); It; ++It)
			{
				if (!It->Expression)
				{
					continue;
				}

				int32 OutIdx;
				UMaterialExpression* RealExpr = TraceReroute(It.Input, OutIdx);
				if (!RealExpr)
				{
					continue;
				}

				FString* FromId = ExprToNodeIndex.Find(RealExpr);
				if (!FromId)
				{
					continue;
				}

				FNodeCodeLinkIR Link;
				Link.FromNodeIndex = *FromId;
				Link.FromOutputName = GetOutputPinName(RealExpr, OutIdx);
				Link.ToNodeIndex = *ToId;
				Link.ToInputName = ShortenInputPinName(CustomOut->GetInputName(It.Index).ToString());
				Link.bToGraphOutput = false;
				IR.Links.Add(MoveTemp(Link));
			}
		}
#endif
	}

	for (const FNodeCodeNodeIR& Node : IR.Nodes)
	{
		UMaterialExpression* Expr = Cast<UMaterialExpression>(Node.SourceObject);
		if (!Expr || Cast<UMaterialExpressionCustomOutput>(Expr))
		{
			continue;
		}

		for (FExpressionInputIterator It(Expr); It; ++It)
		{
			if (!It->Expression)
			{
				continue;
			}

			int32 OutIdx;
			UMaterialExpression* RealExpr = TraceReroute(It.Input, OutIdx);
			if (!RealExpr)
			{
				continue;
			}

			FString* FromId = ExprToNodeIndex.Find(RealExpr);
			if (!FromId)
			{
				continue;
			}

			FNodeCodeLinkIR Link;
			Link.FromNodeIndex = *FromId;
			Link.FromOutputName = GetOutputPinName(RealExpr, OutIdx);
			Link.ToNodeIndex = Node.Index;
			Link.ToInputName = ShortenInputPinName(Expr->GetInputName(It.Index).ToString());
			Link.bToGraphOutput = false;
			IR.Links.Add(MoveTemp(Link));
		}
	}

	return IR;
}

void FMaterialGraphSerializer::CollectReachableNodes(
	UMaterialExpression* StartExpr,
	TSet<UMaterialExpression*>& OutReachable,
	TSet<UMaterialExpression*>& Visited)
{
	if (!StartExpr || Visited.Contains(StartExpr))
	{
		return;
	}

	Visited.Add(StartExpr);
	OutReachable.Add(StartExpr);

	for (FExpressionInputIterator It(StartExpr); It; ++It)
	{
		if (It->Expression)
		{
			if (UMaterialExpressionRerouteBase* Reroute = Cast<UMaterialExpressionRerouteBase>(It->Expression))
			{
				int32 OutIdx;
				UMaterialExpression* RealExpr = Reroute->TraceInputsToRealExpression(OutIdx);
				if (RealExpr)
				{
					CollectReachableNodes(RealExpr, OutReachable, Visited);
				}
			}
			else
			{
				CollectReachableNodes(It->Expression, OutReachable, Visited);
			}
		}
	}
}

void FMaterialGraphSerializer::SerializeNodeProperties(
	UMaterialExpression* Expression,
	TMap<FString, FString>& OutProperties)
{
	FMaterialPropertyHandlerRegistry::Get().SerializeSpecial(Expression, OutProperties);

	UClass* ExprClass = Expression->GetClass();
	UObject* CDO = ExprClass->GetDefaultObject();
	const TSet<FName>& SkipSet = FNodeCodePropertyUtils::GetMaterialExpressionSkipSet();

	for (TFieldIterator<FProperty> PropIt(ExprClass); PropIt; ++PropIt)
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

		if (IsConnectionProperty(Prop))
		{
			continue;
		}

		if (IsEmbeddedConnectionArrayProperty(Prop))
		{
			continue;
		}

		const void* InstanceValue = Prop->ContainerPtrToValuePtr<void>(Expression);
		const void* CDOValue = Prop->ContainerPtrToValuePtr<void>(CDO);

		if (Prop->Identical(InstanceValue, CDOValue, PPF_None))
		{
			continue;
		}

		FString ValueStr = FNodeCodePropertyUtils::FormatPropertyValue(Prop, InstanceValue, Expression);
		OutProperties.Add(Prop->GetName(), MoveTemp(ValueStr));
	}
}

FString FMaterialGraphSerializer::GetOutputPinName(UMaterialExpression* Expression, int32 OutputIndex)
{
	TArray<FExpressionOutput>& Outputs = Expression->GetOutputs();

	if (Outputs.Num() <= 1)
	{
		return FString();
	}

	if (OutputIndex >= 0 && OutputIndex < Outputs.Num())
	{
		const FExpressionOutput& Output = Outputs[OutputIndex];
		if (!Output.OutputName.IsNone())
		{
			return Output.OutputName.ToString();
		}

		if (Output.MaskR && !Output.MaskG && !Output.MaskB && !Output.MaskA) return TEXT("R");
		if (!Output.MaskR && Output.MaskG && !Output.MaskB && !Output.MaskA) return TEXT("G");
		if (!Output.MaskR && !Output.MaskG && Output.MaskB && !Output.MaskA) return TEXT("B");
		if (!Output.MaskR && !Output.MaskG && !Output.MaskB && Output.MaskA) return TEXT("A");
		if (Output.MaskR && Output.MaskG && Output.MaskB && !Output.MaskA) return TEXT("RGB");
		if (Output.MaskR && Output.MaskG && Output.MaskB && Output.MaskA) return TEXT("RGBA");
	}

	return FString::FromInt(OutputIndex);
}

FString FMaterialGraphSerializer::ShortenInputPinName(const FString& InputName)
{
	return InputName;
}

bool FMaterialGraphSerializer::IsConnectionProperty(const FProperty* Prop)
{
	const FStructProperty* StructProp = CastField<FStructProperty>(Prop);
	if (!StructProp || !StructProp->Struct)
	{
		return false;
	}

	const UStruct* Current = StructProp->Struct;
	while (Current)
	{
		if (Current->GetFName() == NAME_ExpressionInput)
		{
			return true;
		}
		Current = Current->GetSuperStruct();
	}

	return false;
}

bool FMaterialGraphSerializer::IsEmbeddedConnectionArrayProperty(const FProperty* Prop)
{
	const FArrayProperty* ArrayProp = CastField<FArrayProperty>(Prop);
	if (!ArrayProp)
	{
		return false;
	}

	const FStructProperty* InnerStruct = CastField<FStructProperty>(ArrayProp->Inner);
	if (!InnerStruct || !InnerStruct->Struct)
	{
		return false;
	}

	for (TFieldIterator<FStructProperty> It(InnerStruct->Struct); It; ++It)
	{
		const UStruct* Current = It->Struct;
		while (Current)
		{
			if (Current->GetFName() == NAME_ExpressionInput)
			{
				return true;
			}
			Current = Current->GetSuperStruct();
		}
	}

	return false;
}
