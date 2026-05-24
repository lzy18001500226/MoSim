// MIT License - Copyright (c) 2025 Italink

#include "NodeCode/NodeCodePropertyUtils.h"
#include "UObject/UnrealType.h"

FString FNodeCodePropertyUtils::FormatPropertyValue(FProperty* Prop, const void* ValuePtr, UObject* Owner)
{
	if (FObjectPropertyBase* ObjProp = CastField<FObjectPropertyBase>(Prop))
	{
		UObject* Obj = ObjProp->GetObjectPropertyValue(ValuePtr);
		if (!Obj)
		{
			return TEXT("None");
		}
		if (Obj->IsAsset())
		{
			return FString::Printf(TEXT("\"%s\""), *Obj->GetPathName().ReplaceCharWithEscapedChar());
		}
		FString ExportStr;
		Prop->ExportTextItem_Direct(ExportStr, ValuePtr, nullptr, Owner, PPF_None, nullptr);
		return ExportStr;
	}

	if (CastField<FStructProperty>(Prop))
	{
		FString ExportStr;
		Prop->ExportTextItem_Direct(ExportStr, ValuePtr, nullptr, Owner, PPF_None, nullptr);
		return ExportStr;
	}

	if (CastField<FStrProperty>(Prop))
	{
		const FString& Str = *static_cast<const FString*>(ValuePtr);
		return FString::Printf(TEXT("\"%s\""), *Str.ReplaceCharWithEscapedChar());
	}

	if (CastField<FNameProperty>(Prop))
	{
		const FName& Name = *static_cast<const FName*>(ValuePtr);
		return FString::Printf(TEXT("\"%s\""), *Name.ToString().ReplaceCharWithEscapedChar());
	}

	if (CastField<FTextProperty>(Prop))
	{
		const FText& Text = *static_cast<const FText*>(ValuePtr);
		return FString::Printf(TEXT("\"%s\""), *Text.ToString().ReplaceCharWithEscapedChar());
	}

	FString ExportStr;
	Prop->ExportTextItem_Direct(ExportStr, ValuePtr, nullptr, Owner, PPF_None, nullptr);
	return ExportStr;
}

bool FNodeCodePropertyUtils::ShouldSkipProperty(const FProperty* Prop)
{
	if (Prop->HasAnyPropertyFlags(
		CPF_Transient | CPF_DuplicateTransient | CPF_SkipSerialization | CPF_Deprecated))
	{
		return true;
	}

	const FString Name = Prop->GetName();
	if (Name.EndsWith(TEXT("_DEPRECATED")))
	{
		return true;
	}

	return false;
}

const TSet<FName>& FNodeCodePropertyUtils::GetEdGraphNodeSkipSet()
{
	static TSet<FName> SkipSet;
	if (SkipSet.Num() == 0)
	{
		SkipSet.Add(TEXT("NodePosX"));
		SkipSet.Add(TEXT("NodePosY"));
		SkipSet.Add(TEXT("NodeWidth"));
		SkipSet.Add(TEXT("NodeHeight"));
		SkipSet.Add(TEXT("NodeGuid"));
		SkipSet.Add(TEXT("NodeComment"));
		SkipSet.Add(TEXT("ErrorType"));
		SkipSet.Add(TEXT("ErrorMsg"));
		SkipSet.Add(TEXT("bHasCompilerMessage"));
		SkipSet.Add(TEXT("bCommentBubblePinned"));
		SkipSet.Add(TEXT("bCommentBubbleVisible"));
		SkipSet.Add(TEXT("bCommentBubbleMakeVisible"));
		SkipSet.Add(TEXT("bCanRenameNode"));
		SkipSet.Add(TEXT("bCanResizeNode"));
		SkipSet.Add(TEXT("bDisplayAsDisabled"));
		SkipSet.Add(TEXT("bUserSetEnabledState"));
		SkipSet.Add(TEXT("bIsIntermediateNode"));
		SkipSet.Add(TEXT("AdvancedPinDisplay"));
		SkipSet.Add(TEXT("EnabledState"));
		SkipSet.Add(TEXT("DeprecatedPins"));
		SkipSet.Add(TEXT("NodeUpgradeMessage"));
		SkipSet.Add(TEXT("bDefaultsToPureFunc"));
		SkipSet.Add(TEXT("bWantsEnumToExecExpansion"));
		SkipSet.Add(TEXT("bIsPureFunc"));
		SkipSet.Add(TEXT("bIsConstFunc"));
		SkipSet.Add(TEXT("bIsInterfaceCall"));
		SkipSet.Add(TEXT("bIsFinalFunction"));
		SkipSet.Add(TEXT("bIsBeadFunction"));
		SkipSet.Add(TEXT("NodePurityOverride"));
	}
	return SkipSet;
}

const TSet<FName>& FNodeCodePropertyUtils::GetMaterialExpressionSkipSet()
{
	static TSet<FName> SkipSet;
	if (SkipSet.Num() == 0)
	{
		SkipSet.Add(TEXT("MaterialExpressionEditorX"));
		SkipSet.Add(TEXT("MaterialExpressionEditorY"));
		SkipSet.Add(TEXT("MaterialExpressionGuid"));
		SkipSet.Add(TEXT("Material"));
		SkipSet.Add(TEXT("Function"));
		SkipSet.Add(TEXT("GraphNode"));
		SkipSet.Add(TEXT("bRealtimePreview"));
		SkipSet.Add(TEXT("bNeedToUpdatePreview"));
		SkipSet.Add(TEXT("bIsParameterExpression"));
		SkipSet.Add(TEXT("bShowOutputNameOnPin"));
		SkipSet.Add(TEXT("bShowMaskColorsOnPin"));
		SkipSet.Add(TEXT("bHidePreviewWindow"));
		SkipSet.Add(TEXT("bCollapsed"));
		SkipSet.Add(TEXT("bShaderInputData"));
		SkipSet.Add(TEXT("Outputs"));
		SkipSet.Add(TEXT("Desc"));
		SkipSet.Add(TEXT("SubgraphExpression"));
		SkipSet.Add(TEXT("AttributeSetTypes"));
		SkipSet.Add(TEXT("PreEditAttributeSetTypes"));
	}
	return SkipSet;
}

const TSet<FName>& FNodeCodePropertyUtils::GetWidgetSkipSet()
{
	static TSet<FName> SkipSet;
	if (SkipSet.Num() == 0)
	{
		SkipSet.Add(TEXT("Slot"));
		SkipSet.Add(TEXT("bIsVariable"));
		SkipSet.Add(TEXT("bIsDesignTime"));
		SkipSet.Add(TEXT("DesignerFlags"));
		SkipSet.Add(TEXT("DisplayLabel"));
		SkipSet.Add(TEXT("bLockedInDesigner"));
		SkipSet.Add(TEXT("DesignSizeMode"));
		SkipSet.Add(TEXT("NativeBindings"));
		SkipSet.Add(TEXT("ToolTipWidget"));
		SkipSet.Add(TEXT("Navigation"));
		SkipSet.Add(TEXT("FlowDirectionPreference"));
		SkipSet.Add(TEXT("bCreatedByConstructionScript"));
		SkipSet.Add(TEXT("bExpandedInDesigner"));
		SkipSet.Add(TEXT("bHiddenInDesigner"));
		SkipSet.Add(TEXT("CategoryName"));
	}
	return SkipSet;
}

const TSet<FName>& FNodeCodePropertyUtils::GetNiagaraNodeSkipSet()
{
	static TSet<FName> SkipSet;
	if (SkipSet.Num() == 0)
	{
		SkipSet.Add(TEXT("ChangeId"));
		SkipSet.Add(TEXT("FullTitle"));
		SkipSet.Add(TEXT("Usage"));
		SkipSet.Add(TEXT("RefreshFromExternalChanges"));
		SkipSet.Add(TEXT("Signature"));
		SkipSet.Add(TEXT("FunctionScriptAssetObjectPath"));
		SkipSet.Add(TEXT("SelectedScriptVersion"));
		SkipSet.Add(TEXT("PreviousScriptVersion"));
		SkipSet.Add(TEXT("DebugState"));
		SkipSet.Add(TEXT("BoundPinNames"));
		SkipSet.Add(TEXT("PropagatedStaticSwitchParameters"));
		SkipSet.Add(TEXT("PinOutputToPinDefaultPersistentId"));
		SkipSet.Add(TEXT("ScriptType"));
		SkipSet.Add(TEXT("ScriptTypeId"));
		SkipSet.Add(TEXT("AddedPins"));
	}
	return SkipSet;
}
