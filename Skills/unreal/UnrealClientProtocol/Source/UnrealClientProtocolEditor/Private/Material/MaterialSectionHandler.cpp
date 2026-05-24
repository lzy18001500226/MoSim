// MIT License - Copyright (c) 2025 Italink

#include "Material/MaterialSectionHandler.h"
#include "Material/MaterialGraphSerializer.h"
#include "Material/MaterialGraphDiffer.h"
#include "NodeCode/NodeCodeTextFormat.h"

#include "Materials/Material.h"
#include "Materials/MaterialFunction.h"
#include "Materials/MaterialExpression.h"

static const FString MaterialType = TEXT("Material");
static const FString CompositeType = TEXT("Composite");
static const FString PropertiesType = TEXT("Properties");

TArray<FNodeCodeSectionTypeInfo> FMaterialSectionHandler::GetSupportedSectionTypes() const
{
	return {
		{PropertiesType, ENodeCodeSectionFormat::Properties},
		{MaterialType, ENodeCodeSectionFormat::Graph},
		{CompositeType, ENodeCodeSectionFormat::Graph}
	};
}

bool FMaterialSectionHandler::CanHandle(UObject* Asset, const FString& Type) const
{
	if (!Asset)
	{
		return false;
	}

	bool bIsMaterial = Asset->IsA<UMaterial>() || Asset->IsA<UMaterialFunction>();
	if (!bIsMaterial)
	{
		return false;
	}

	if (Type.IsEmpty())
	{
		return true;
	}

	return Type == MaterialType || Type == CompositeType || Type == PropertiesType;
}

TArray<FNodeCodeSectionIR> FMaterialSectionHandler::ListSections(UObject* Asset)
{
	if (UMaterial* Material = Cast<UMaterial>(Asset))
	{
		return FMaterialGraphSerializer::ListSections(Material);
	}

	if (UMaterialFunction* MaterialFunction = Cast<UMaterialFunction>(Asset))
	{
		return FMaterialGraphSerializer::ListSections(MaterialFunction);
	}

	return {};
}

FNodeCodeSectionIR FMaterialSectionHandler::Read(UObject* Asset, const FString& Type, const FString& Name)
{
	FNodeCodeSectionIR Section;
	Section.Type = Type;
	Section.Name = Name;

	if (Type == PropertiesType)
	{
		if (UMaterial* Material = Cast<UMaterial>(Asset))
		{
			Section.Properties = FMaterialGraphSerializer::ReadMaterialProperties(Material);
		}
		return Section;
	}

	if (Type == CompositeType)
	{
		if (UMaterial* Material = Cast<UMaterial>(Asset))
		{
			Section.Graph = FMaterialGraphSerializer::BuildCompositeIR(Material, Name);
		}
		return Section;
	}

	if (UMaterial* Material = Cast<UMaterial>(Asset))
	{
		Section.Graph = FMaterialGraphSerializer::BuildIR(Material);
	}
	else if (UMaterialFunction* MaterialFunction = Cast<UMaterialFunction>(Asset))
	{
		Section.Graph = FMaterialGraphSerializer::BuildIR(MaterialFunction);
	}

	return Section;
}

FNodeCodeDiffResult FMaterialSectionHandler::Write(UObject* Asset, const FNodeCodeSectionIR& Section)
{
	if (Section.Type == PropertiesType)
	{
		if (UMaterial* Material = Cast<UMaterial>(Asset))
		{
			return FMaterialGraphDiffer::ApplyMaterialProperties(Material, Section.Properties);
		}
		return {};
	}

	if (Section.Type == CompositeType)
	{
		if (UMaterial* Material = Cast<UMaterial>(Asset))
		{
			return FMaterialGraphDiffer::ApplyComposite(Material, Section.Name, Section.Graph);
		}
		return {};
	}

	if (UMaterial* Material = Cast<UMaterial>(Asset))
	{
		return FMaterialGraphDiffer::ApplyMaterial(Material, Section.Graph);
	}

	if (UMaterialFunction* MaterialFunction = Cast<UMaterialFunction>(Asset))
	{
		return FMaterialGraphDiffer::ApplyFunction(MaterialFunction, Section.Graph);
	}

	return {};
}

bool FMaterialSectionHandler::CreateSection(UObject* Asset, const FString& Type, const FString& Name)
{
	return false;
}

bool FMaterialSectionHandler::RemoveSection(UObject* Asset, const FString& Type, const FString& Name)
{
	return false;
}

UObject* FMaterialSectionHandler::FindNodeByGuid(UObject* Asset, const FGuid& Guid)
{
	auto SearchExpressions = [&Guid](TArrayView<const TObjectPtr<UMaterialExpression>> Expressions) -> UObject*
	{
		for (const auto& Expr : Expressions)
		{
			if (Expr && Expr->MaterialExpressionGuid == Guid)
			{
				return Expr.Get();
			}
		}
		return nullptr;
	};

	if (UMaterial* Material = Cast<UMaterial>(Asset))
	{
		return SearchExpressions(Material->GetExpressions());
	}

	if (UMaterialFunction* MaterialFunction = Cast<UMaterialFunction>(Asset))
	{
		return SearchExpressions(MaterialFunction->GetExpressions());
	}

	return nullptr;
}
