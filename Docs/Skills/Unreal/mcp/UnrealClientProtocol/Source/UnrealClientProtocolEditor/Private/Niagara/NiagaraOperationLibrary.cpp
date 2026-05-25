// MIT License - Copyright (c) 2025 Italink

#include "NiagaraOperationLibrary.h"
#include "UCPJsonUtils.h"

#include "NiagaraSystem.h"
#include "NiagaraEmitter.h"
#include "NiagaraScript.h"
#include "NiagaraScriptSource.h"
#include "NiagaraGraph.h"
#include "NiagaraScriptVariable.h"
#include "NiagaraNode.h"
#include "NiagaraNodeFunctionCall.h"
#include "NiagaraNodeOutput.h"
#include "NiagaraSimulationStageBase.h"
#include "NiagaraRendererProperties.h"
#include "NiagaraEmitterHandle.h"
#include "NiagaraTypes.h"
#include "NiagaraConstants.h"
#include "NiagaraCommon.h"
#include "NiagaraEditorDataBase.h"
#include "NiagaraDataInterface.h"
#include "NiagaraEditorUtilities.h"
#include "NiagaraSystemEditorData.h"
#include "NiagaraScratchPadContainer.h"
#include "NiagaraSystemFactoryNew.h"
#include "ViewModels/Stack/NiagaraStackGraphUtilities.h"
#include "ViewModels/Stack/NiagaraParameterHandle.h"

#include "ScopedTransaction.h"

DEFINE_LOG_CATEGORY_STATIC(LogNiagaraOp, Log, All);

using namespace UCPUtils;

// ---- Helpers ----

static FString ErrorResult(const FString& Func, const FString& Msg)
{
	UE_LOG(LogNiagaraOp, Error, TEXT("%s: %s"), *Func, *Msg);
	TSharedPtr<FJsonObject> R = MakeShared<FJsonObject>();
	R->SetBoolField(TEXT("success"), false);
	R->SetStringField(TEXT("error"), Msg);
	return JsonToString(R);
}

static FString SuccessResult(const FString& Message = TEXT(""))
{
	TSharedPtr<FJsonObject> R = MakeShared<FJsonObject>();
	R->SetBoolField(TEXT("success"), true);
	if (!Message.IsEmpty()) R->SetStringField(TEXT("message"), Message);
	return JsonToString(R);
}

static FVersionedNiagaraEmitterData* GetEmitterData(UNiagaraEmitter* Emitter)
{
	return Emitter ? Emitter->GetLatestEmitterData() : nullptr;
}

static FGuid GetEmitterVersion(UNiagaraEmitter* Emitter)
{
	return (Emitter && Emitter->IsVersioningEnabled()) ? Emitter->GetExposedVersion().VersionGuid : FGuid();
}

static void SyncSystemEditorData(UNiagaraSystem* System)
{
	if (!System) return;
	if (UNiagaraEditorDataBase* EditorDataBase = System->GetEditorData())
	{
		if (UNiagaraSystemEditorData* EditorData = Cast<UNiagaraSystemEditorData>(EditorDataBase))
		{
			EditorData->SynchronizeOverviewGraphWithSystem(*System);
		}
	}
}

static void EnsureSystemInitialized(UNiagaraSystem* System)
{
	if (!System) return;
	UNiagaraScript* SpawnScript = System->GetSystemSpawnScript();
	if (SpawnScript && !SpawnScript->GetLatestSource())
	{
		UNiagaraSystemFactoryNew::InitializeSystem(System, true);
	}
}

static ENiagaraScriptUsage ParseScriptUsage(const FString& Str)
{
	if (Str == TEXT("SystemSpawn")) return ENiagaraScriptUsage::SystemSpawnScript;
	if (Str == TEXT("SystemUpdate")) return ENiagaraScriptUsage::SystemUpdateScript;
	if (Str == TEXT("EmitterSpawn")) return ENiagaraScriptUsage::EmitterSpawnScript;
	if (Str == TEXT("EmitterUpdate")) return ENiagaraScriptUsage::EmitterUpdateScript;
	if (Str == TEXT("ParticleSpawn")) return ENiagaraScriptUsage::ParticleSpawnScript;
	if (Str == TEXT("ParticleUpdate")) return ENiagaraScriptUsage::ParticleUpdateScript;
	if (Str == TEXT("ParticleEvent")) return ENiagaraScriptUsage::ParticleEventScript;
	if (Str == TEXT("SimulationStage")) return ENiagaraScriptUsage::ParticleSimulationStageScript;
	return ENiagaraScriptUsage::Module;
}

static FGuid ParseGuid(const FString& S) { FGuid G; FGuid::Parse(S, G); return G; }

static FNiagaraTypeDefinition ParseTypeDef(const FString& T)
{
	if (T == TEXT("float") || T == TEXT("NiagaraFloat")) return FNiagaraTypeDefinition::GetFloatDef();
	if (T == TEXT("int32") || T == TEXT("NiagaraInt32")) return FNiagaraTypeDefinition::GetIntDef();
	if (T == TEXT("bool") || T == TEXT("NiagaraBool")) return FNiagaraTypeDefinition::GetBoolDef();
	if (T == TEXT("NiagaraPosition")) return FNiagaraTypeDefinition::GetPositionDef();
	if (T == TEXT("Vector") || T == TEXT("FVector")) return FNiagaraTypeDefinition::GetVec3Def();
	if (T == TEXT("Vector2D") || T == TEXT("FVector2D") || T == TEXT("NiagaraVec2")) return FNiagaraTypeDefinition::GetVec2Def();
	if (T == TEXT("Vector4") || T == TEXT("FVector4") || T == TEXT("NiagaraVec4")) return FNiagaraTypeDefinition::GetVec4Def();
	if (T == TEXT("LinearColor") || T == TEXT("FLinearColor") || T == TEXT("NiagaraLinearColor")) return FNiagaraTypeDefinition::GetColorDef();
	if (T == TEXT("Quat") || T == TEXT("FQuat") || T == TEXT("NiagaraQuat")) return FNiagaraTypeDefinition::GetQuatDef();
	if (T == TEXT("Matrix") || T == TEXT("FMatrix") || T == TEXT("NiagaraMatrix")) return FNiagaraTypeDefinition::GetMatrix4Def();
	if (T == TEXT("NiagaraID")) return FNiagaraTypeDefinition::GetIDDef();

	// Data Interface types: look up UClass by name
	FString DIClassName = T;
	if (!DIClassName.StartsWith(TEXT("U")))
	{
		DIClassName = TEXT("U") + DIClassName;
	}
	UClass* DIClass = FindFirstObject<UClass>(*DIClassName, EFindFirstObjectOptions::NativeFirst);
	if (DIClass && DIClass->IsChildOf(UNiagaraDataInterface::StaticClass()))
	{
		return FNiagaraTypeDefinition(DIClass);
	}

	// Try with the original name (no U prefix)
	DIClass = FindFirstObject<UClass>(*T, EFindFirstObjectOptions::NativeFirst);
	if (DIClass && DIClass->IsChildOf(UNiagaraDataInterface::StaticClass()))
	{
		return FNiagaraTypeDefinition(DIClass);
	}

	// Enum/Struct lookup by name
	UScriptStruct* Struct = FindFirstObject<UScriptStruct>(*T, EFindFirstObjectOptions::NativeFirst);
	if (Struct)
	{
		return FNiagaraTypeDefinition(Struct);
	}

	return FNiagaraTypeDefinition();
}

struct FResolvedContext
{
	UNiagaraSystem* System = nullptr;
	UNiagaraEmitter* Emitter = nullptr;
	UNiagaraGraph* Graph = nullptr;
	UNiagaraScript* Script = nullptr;
	ENiagaraScriptUsage Usage = ENiagaraScriptUsage::Module;
};

static bool ResolveContext(UObject* Obj, const FString& UsageStr, FResolvedContext& Out)
{
	Out.System = Cast<UNiagaraSystem>(Obj);
	Out.Emitter = Cast<UNiagaraEmitter>(Obj);
	Out.Usage = ParseScriptUsage(UsageStr);

	auto GetGraph = [](UNiagaraScriptSourceBase* Src) -> UNiagaraGraph* {
		UNiagaraScriptSource* S = Cast<UNiagaraScriptSource>(Src);
		return S ? S->NodeGraph : nullptr;
	};

	if (Out.System && UNiagaraScript::IsSystemScript(Out.Usage))
	{
		Out.Script = (Out.Usage == ENiagaraScriptUsage::SystemSpawnScript) ? Out.System->GetSystemSpawnScript() : Out.System->GetSystemUpdateScript();
		if (Out.Script) Out.Graph = GetGraph(Out.Script->GetLatestSource());
	}
	else if (Out.Emitter)
	{
		FVersionedNiagaraEmitterData* Data = GetEmitterData(Out.Emitter);
		if (Data)
		{
			Out.Graph = GetGraph(Data->GraphSource);
			if (Out.Usage == ENiagaraScriptUsage::ParticleSpawnScript) Out.Script = Data->SpawnScriptProps.Script;
			else if (Out.Usage == ENiagaraScriptUsage::ParticleUpdateScript) Out.Script = Data->UpdateScriptProps.Script;
			else if (Out.Usage == ENiagaraScriptUsage::EmitterSpawnScript) Out.Script = Data->EmitterSpawnScriptProps.Script;
			else if (Out.Usage == ENiagaraScriptUsage::EmitterUpdateScript) Out.Script = Data->EmitterUpdateScriptProps.Script;
			else if (Out.Usage == ENiagaraScriptUsage::ParticleEventScript)
			{
				for (const FNiagaraEventScriptProperties& EP : Data->EventHandlerScriptProps)
				{
					if (EP.Script) { Out.Script = EP.Script; break; }
				}
			}
			else if (Out.Usage == ENiagaraScriptUsage::ParticleSimulationStageScript)
			{
				for (UNiagaraSimulationStageBase* Stage : Data->GetSimulationStages())
				{
					if (Stage && Stage->Script) { Out.Script = Stage->Script; break; }
				}
			}
		}
	}
	else if (Out.System && !UNiagaraScript::IsSystemScript(Out.Usage))
	{
		UE_LOG(LogNiagaraOp, Error, TEXT("ResolveContext: System passed with emitter-level usage '%s'. Pass the Emitter path instead."), *UsageStr);
		return false;
	}
	return Out.Graph != nullptr;
}

// Uses exported BuildTraversal to find FunctionCall modules in a usage chain
static TArray<UNiagaraNodeFunctionCall*> GetModulesInUsage(UNiagaraGraph* Graph, ENiagaraScriptUsage Usage)
{
	TArray<UNiagaraNodeFunctionCall*> Result;
	if (!Graph) return Result;

	TArray<UNiagaraNode*> Traversal;
	Graph->BuildTraversal(Traversal, Usage, FGuid());

	for (UNiagaraNode* Node : Traversal)
	{
		UNiagaraNodeFunctionCall* FC = Cast<UNiagaraNodeFunctionCall>(Node);
		if (FC && !FC->IsA<UNiagaraNodeOutput>())
		{
			Result.Add(FC);
		}
	}
	return Result;
}

static UNiagaraNodeFunctionCall* FindModuleByGuid(UNiagaraGraph* Graph, ENiagaraScriptUsage Usage, const FGuid& Guid)
{
	for (UNiagaraNodeFunctionCall* FC : GetModulesInUsage(Graph, Usage))
	{
		if (FC->NodeGuid == Guid) return FC;
	}
	return nullptr;
}

// ---- Emitter Management ----

FString UNiagaraOperationLibrary::AddEmitter(UNiagaraSystem* System, UNiagaraEmitter* SourceEmitter, const FString& Name)
{
	if (!System) return ErrorResult(TEXT("AddEmitter"), TEXT("System is null"));
	if (!SourceEmitter) return ErrorResult(TEXT("AddEmitter"), TEXT("SourceEmitter is null"));

	EnsureSystemInitialized(System);

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "AddEmitter", "UCP: Add Emitter"));
	const FGuid NewHandleId = FNiagaraEditorUtilities::AddEmitterToSystem(*System, *SourceEmitter, GetEmitterVersion(SourceEmitter), true);

	if (!NewHandleId.IsValid())
		return ErrorResult(TEXT("AddEmitter"), TEXT("Failed to add emitter"));

	FString HandleName;
	for (const FNiagaraEmitterHandle& H : System->GetEmitterHandles())
	{
		if (H.GetId() == NewHandleId)
		{
			HandleName = H.GetName().ToString();
			break;
		}
	}

	TSharedPtr<FJsonObject> R = MakeShared<FJsonObject>();
	R->SetBoolField(TEXT("success"), true);
	R->SetStringField(TEXT("name"), HandleName);
	R->SetStringField(TEXT("id"), NewHandleId.ToString());
	return JsonToString(R);
}

FString UNiagaraOperationLibrary::RemoveEmitter(UNiagaraSystem* System, const FString& EmitterName)
{
	if (!System) return ErrorResult(TEXT("RemoveEmitter"), TEXT("System is null"));
	for (const FNiagaraEmitterHandle& H : System->GetEmitterHandles())
	{
		if (H.GetName().ToString() == EmitterName)
		{
			FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "RemoveEmitter", "UCP: Remove Emitter"));
			System->Modify();
			TSet<FGuid> Ids;
			Ids.Add(H.GetId());
			System->RemoveEmitterHandlesById(Ids);
			SyncSystemEditorData(System);
			return SuccessResult(FString::Printf(TEXT("Removed: %s"), *EmitterName));
		}
	}
	return ErrorResult(TEXT("RemoveEmitter"), FString::Printf(TEXT("Not found: %s"), *EmitterName));
}

FString UNiagaraOperationLibrary::ReorderEmitter(UNiagaraSystem* System, const FString& EmitterName, int32 NewIndex)
{
	if (!System) return ErrorResult(TEXT("ReorderEmitter"), TEXT("System is null"));
	TArray<FNiagaraEmitterHandle>& Handles = System->GetEmitterHandles();
	int32 Cur = INDEX_NONE;
	for (int32 i = 0; i < Handles.Num(); ++i)
		if (Handles[i].GetName().ToString() == EmitterName) { Cur = i; break; }
	if (Cur == INDEX_NONE) return ErrorResult(TEXT("ReorderEmitter"), TEXT("Not found"));

	NewIndex = FMath::Clamp(NewIndex, 0, Handles.Num() - 1);
	if (Cur == NewIndex) return SuccessResult(TEXT("No change"));

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "ReorderEmitter", "UCP: Reorder Emitter"));
	System->Modify();
	FNiagaraEmitterHandle H = Handles[Cur];
	Handles.RemoveAt(Cur);
	Handles.Insert(H, NewIndex);

	SyncSystemEditorData(System);
	return SuccessResult(FString::Printf(TEXT("Moved %s to %d"), *EmitterName, NewIndex));
}

// ---- User Parameter Management ----

FString UNiagaraOperationLibrary::AddUserParameter(UNiagaraSystem* System, const FString& ParamName, const FString& TypeName, const FString& DefaultValue)
{
	if (!System) return ErrorResult(TEXT("AddUserParameter"), TEXT("System is null"));
	FNiagaraTypeDefinition TypeDef = ParseTypeDef(TypeName);
	if (!TypeDef.IsValid()) return ErrorResult(TEXT("AddUserParameter"), FString::Printf(TEXT("Unsupported type: %s"), *TypeName));

	FString FullName = ParamName.StartsWith(TEXT("User.")) ? ParamName : (TEXT("User.") + ParamName);
	FNiagaraVariable Var(TypeDef, FName(*FullName));

	if (!DefaultValue.IsEmpty() && !TypeDef.IsDataInterface())
	{
		Var.AllocateData();
		const UScriptStruct* Struct = TypeDef.GetScriptStruct();
		if (Struct)
		{
			Struct->ImportText(*DefaultValue, Var.GetData(), nullptr, PPF_None, nullptr, Struct->GetName());
		}
	}

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "AddUserParam", "UCP: Add User Parameter"));
	if (!System->GetExposedParameters().AddParameter(Var, true, false))
		return ErrorResult(TEXT("AddUserParameter"), TEXT("Failed to add"));
	return SuccessResult(FString::Printf(TEXT("Added %s (%s)"), *ParamName, *TypeName));
}

FString UNiagaraOperationLibrary::RemoveUserParameter(UNiagaraSystem* System, const FString& ParamName)
{
	if (!System) return ErrorResult(TEXT("RemoveUserParameter"), TEXT("System is null"));
	FString FullName = ParamName.StartsWith(TEXT("User.")) ? ParamName : (TEXT("User.") + ParamName);

	TArray<FNiagaraVariable> Params;
	System->GetExposedParameters().GetParameters(Params);
	for (const FNiagaraVariable& V : Params)
	{
		if (V.GetName().ToString() == FullName)
		{
			FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "RemoveUserParam", "UCP: Remove User Parameter"));
			System->GetExposedParameters().RemoveParameter(V);
			return SuccessResult(FString::Printf(TEXT("Removed %s"), *ParamName));
		}
	}
	return ErrorResult(TEXT("RemoveUserParameter"), TEXT("Not found"));
}

// ---- Module Stack Management ----
// Uses exported: AddScriptModuleToStack(UNiagaraScript*,...), SetModuleIsEnabled, BuildTraversal, FindEquivalentOutputNode

FString UNiagaraOperationLibrary::AddModule(UObject* SystemOrEmitter, const FString& ScriptUsage, UNiagaraScript* ModuleScript, int32 Index)
{
	FResolvedContext Ctx;
	if (!ResolveContext(SystemOrEmitter, ScriptUsage, Ctx))
		return ErrorResult(TEXT("AddModule"), TEXT("Could not resolve graph"));
	if (!ModuleScript) return ErrorResult(TEXT("AddModule"), TEXT("ModuleScript is null"));

	UNiagaraNodeOutput* OutputNode = Ctx.Graph->FindEquivalentOutputNode(Ctx.Usage);
	if (!OutputNode) return ErrorResult(TEXT("AddModule"), TEXT("Output node not found"));

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "AddModule", "UCP: Add Module"));
	UNiagaraNodeFunctionCall* NewNode = FNiagaraStackGraphUtilities::AddScriptModuleToStack(ModuleScript, *OutputNode, Index);
	if (!NewNode) return ErrorResult(TEXT("AddModule"), TEXT("Failed"));
	Ctx.Graph->NotifyGraphChanged();

	TSharedPtr<FJsonObject> R = MakeShared<FJsonObject>();
	R->SetBoolField(TEXT("success"), true);
	R->SetStringField(TEXT("name"), NewNode->GetFunctionName());
	R->SetStringField(TEXT("guid"), NewNode->NodeGuid.ToString());
	return JsonToString(R);
}

FString UNiagaraOperationLibrary::RemoveModule(UObject* SystemOrEmitter, const FString& ScriptUsage, const FString& ModuleNodeGuid)
{
	FResolvedContext Ctx;
	if (!ResolveContext(SystemOrEmitter, ScriptUsage, Ctx))
		return ErrorResult(TEXT("RemoveModule"), TEXT("Could not resolve graph"));

	UNiagaraNodeFunctionCall* FC = FindModuleByGuid(Ctx.Graph, Ctx.Usage, ParseGuid(ModuleNodeGuid));
	if (!FC) return ErrorResult(TEXT("RemoveModule"), TEXT("Module not found"));

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "RemoveModule", "UCP: Remove Module"));
	FString Name = FC->GetFunctionName();
	FC->GetGraph()->RemoveNode(FC);
	Ctx.Graph->NotifyGraphChanged();
	return SuccessResult(FString::Printf(TEXT("Removed %s"), *Name));
}

FString UNiagaraOperationLibrary::SetModuleEnabled(UObject* SystemOrEmitter, const FString& ScriptUsage, const FString& ModuleNodeGuid, bool bEnabled)
{
	FResolvedContext Ctx;
	if (!ResolveContext(SystemOrEmitter, ScriptUsage, Ctx))
		return ErrorResult(TEXT("SetModuleEnabled"), TEXT("Could not resolve graph"));

	UNiagaraNodeFunctionCall* FC = FindModuleByGuid(Ctx.Graph, Ctx.Usage, ParseGuid(ModuleNodeGuid));
	if (!FC) return ErrorResult(TEXT("SetModuleEnabled"), TEXT("Module not found"));

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "SetModuleEnabled", "UCP: Set Module Enabled"));
	FNiagaraStackGraphUtilities::SetModuleIsEnabled(*FC, bEnabled);
	return SuccessResult(FString::Printf(TEXT("%s: %s"), *FC->GetFunctionName(), bEnabled ? TEXT("enabled") : TEXT("disabled")));
}

FString UNiagaraOperationLibrary::GetModules(UObject* SystemOrEmitter, const FString& ScriptUsage)
{
	FResolvedContext Ctx;
	if (!ResolveContext(SystemOrEmitter, ScriptUsage, Ctx))
		return ErrorResult(TEXT("GetModules"), TEXT("Could not resolve graph"));

	TArray<TSharedPtr<FJsonValue>> Arr;
	for (UNiagaraNodeFunctionCall* FC : GetModulesInUsage(Ctx.Graph, Ctx.Usage))
	{
		TSharedPtr<FJsonObject> M = MakeShared<FJsonObject>();
		M->SetStringField(TEXT("name"), FC->GetFunctionName());
		M->SetStringField(TEXT("guid"), FC->NodeGuid.ToString());
		M->SetBoolField(TEXT("enabled"), FC->GetDesiredEnabledState() == ENodeEnabledState::Enabled);
		if (FC->FunctionScript) M->SetStringField(TEXT("scriptPath"), FC->FunctionScript->GetPathName());
		Arr.Add(MakeShared<FJsonValueObject>(M));
	}
	return JsonArrayToString(Arr);
}

// ---- Module Input Operations ----
// Uses exported: GetOrCreateStackFunctionInputOverridePin, SetLinkedParameterValueForFunctionInput, SetDynamicInputForFunctionInput

FString UNiagaraOperationLibrary::SetModuleInputValue(UObject* SystemOrEmitter, const FString& ScriptUsage, const FString& ModuleNodeGuid, const FString& InputName, const FString& Value)
{
	FResolvedContext Ctx;
	if (!ResolveContext(SystemOrEmitter, ScriptUsage, Ctx) || !Ctx.Script)
		return ErrorResult(TEXT("SetModuleInputValue"), TEXT("Could not resolve context"));

	UNiagaraNodeFunctionCall* FC = FindModuleByGuid(Ctx.Graph, Ctx.Usage, ParseGuid(ModuleNodeGuid));
	if (!FC) return ErrorResult(TEXT("SetModuleInputValue"), TEXT("Module not found"));

	FNiagaraParameterHandle ModuleHandle(TEXT("Module"), FName(*InputName));
	FNiagaraParameterHandle AliasedHandle = FNiagaraParameterHandle::CreateAliasedModuleParameterHandle(ModuleHandle, FC);

	FString EmitterName;
	if (Ctx.Emitter) EmitterName = Ctx.Emitter->GetUniqueEmitterName();

	FString RapidIterName = FNiagaraUtilities::CreateRapidIterationConstantName(
		AliasedHandle.GetParameterHandleString(), EmitterName.IsEmpty() ? nullptr : *EmitterName, Ctx.Usage);

	FNiagaraTypeDefinition InputType;
	for (const FNiagaraVariable& V : FC->Signature.Inputs)
	{
		FString VName = V.GetName().ToString();
		if (VName == InputName || VName.EndsWith(TEXT(".") + InputName) || VName == TEXT("Module.") + InputName)
		{
			InputType = V.GetType();
			break;
		}
	}
	if (!InputType.IsValid())
		return ErrorResult(TEXT("SetModuleInputValue"), FString::Printf(TEXT("Input not found: %s"), *InputName));

	FNiagaraVariable RapidVar(InputType, FName(*RapidIterName));
	RapidVar.AllocateData();

	const UScriptStruct* Struct = InputType.GetScriptStruct();
	if (!Struct)
		return ErrorResult(TEXT("SetModuleInputValue"), FString::Printf(TEXT("Type %s has no struct — cannot set literal value"), *InputType.GetName()));

	const TCHAR* ParseResult = Struct->ImportText(*Value, RapidVar.GetData(), nullptr, PPF_None, nullptr, Struct->GetName());
	if (!ParseResult)
		return ErrorResult(TEXT("SetModuleInputValue"), FString::Printf(TEXT("Failed to parse value '%s' for type %s"), *Value, *InputType.GetName()));

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "SetInputValue", "UCP: Set Module Input Value"));
	Ctx.Script->RapidIterationParameters.SetParameterData(RapidVar.GetData(), RapidVar, true);

	return SuccessResult(FString::Printf(TEXT("Set %s = %s"), *InputName, *Value));
}

FString UNiagaraOperationLibrary::SetModuleInputBinding(UObject* SystemOrEmitter, const FString& ScriptUsage, const FString& ModuleNodeGuid, const FString& InputName, const FString& LinkedParamName)
{
	FResolvedContext Ctx;
	if (!ResolveContext(SystemOrEmitter, ScriptUsage, Ctx))
		return ErrorResult(TEXT("SetModuleInputBinding"), TEXT("Could not resolve context"));

	UNiagaraNodeFunctionCall* FC = FindModuleByGuid(Ctx.Graph, Ctx.Usage, ParseGuid(ModuleNodeGuid));
	if (!FC) return ErrorResult(TEXT("SetModuleInputBinding"), TEXT("Module not found"));

	FNiagaraTypeDefinition InputType;
	for (const FNiagaraVariable& V : FC->Signature.Inputs)
	{
		FString VName = V.GetName().ToString();
		if (VName == InputName || VName.EndsWith(TEXT(".") + InputName) || VName == TEXT("Module.") + InputName)
		{
			InputType = V.GetType();
			break;
		}
	}
	if (!InputType.IsValid())
		return ErrorResult(TEXT("SetModuleInputBinding"), FString::Printf(TEXT("Input not found: %s"), *InputName));

	FNiagaraParameterHandle ModuleHandle(TEXT("Module"), FName(*InputName));
	FNiagaraParameterHandle AliasedHandle = FNiagaraParameterHandle::CreateAliasedModuleParameterHandle(ModuleHandle, FC);

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "SetInputBinding", "UCP: Set Module Input Binding"));

	UEdGraphPin& Pin = FNiagaraStackGraphUtilities::GetOrCreateStackFunctionInputOverridePin(*FC, AliasedHandle, InputType, FGuid(), FGuid());

	FNiagaraVariable LinkedVar(InputType, FName(*LinkedParamName));
	TSet<FNiagaraVariableBase> Known;
	FNiagaraStackGraphUtilities::SetLinkedParameterValueForFunctionInput(Pin, LinkedVar, Known);

	Ctx.Graph->NotifyGraphChanged();
	return SuccessResult(FString::Printf(TEXT("Bound %s -> %s"), *InputName, *LinkedParamName));
}

FString UNiagaraOperationLibrary::SetModuleInputDynamicInput(UObject* SystemOrEmitter, const FString& ScriptUsage, const FString& ModuleNodeGuid, const FString& InputName, UNiagaraScript* DynamicInputScript)
{
	FResolvedContext Ctx;
	if (!ResolveContext(SystemOrEmitter, ScriptUsage, Ctx))
		return ErrorResult(TEXT("SetModuleInputDynamicInput"), TEXT("Could not resolve context"));
	if (!DynamicInputScript) return ErrorResult(TEXT("SetModuleInputDynamicInput"), TEXT("Script is null"));

	UNiagaraNodeFunctionCall* FC = FindModuleByGuid(Ctx.Graph, Ctx.Usage, ParseGuid(ModuleNodeGuid));
	if (!FC) return ErrorResult(TEXT("SetModuleInputDynamicInput"), TEXT("Module not found"));

	FNiagaraTypeDefinition InputType;
	for (const FNiagaraVariable& V : FC->Signature.Inputs)
	{
		FString VName = V.GetName().ToString();
		if (VName == InputName || VName.EndsWith(TEXT(".") + InputName) || VName == TEXT("Module.") + InputName)
		{
			InputType = V.GetType();
			break;
		}
	}
	if (!InputType.IsValid())
		return ErrorResult(TEXT("SetModuleInputDynamicInput"), FString::Printf(TEXT("Input not found: %s"), *InputName));

	FNiagaraParameterHandle ModuleHandle(TEXT("Module"), FName(*InputName));
	FNiagaraParameterHandle AliasedHandle = FNiagaraParameterHandle::CreateAliasedModuleParameterHandle(ModuleHandle, FC);

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "SetInputDI", "UCP: Set Dynamic Input"));

	UEdGraphPin& Pin = FNiagaraStackGraphUtilities::GetOrCreateStackFunctionInputOverridePin(*FC, AliasedHandle, InputType, FGuid(), FGuid());

	UNiagaraNodeFunctionCall* DINode = nullptr;
	FNiagaraStackGraphUtilities::SetDynamicInputForFunctionInput(Pin, DynamicInputScript, DINode);

	Ctx.Graph->NotifyGraphChanged();
	return SuccessResult(FString::Printf(TEXT("Set dynamic input for %s"), *InputName));
}

FString UNiagaraOperationLibrary::ResetModuleInput(UObject* SystemOrEmitter, const FString& ScriptUsage, const FString& ModuleNodeGuid, const FString& InputName)
{
	FResolvedContext Ctx;
	if (!ResolveContext(SystemOrEmitter, ScriptUsage, Ctx))
		return ErrorResult(TEXT("ResetModuleInput"), TEXT("Could not resolve context"));

	UNiagaraNodeFunctionCall* FC = FindModuleByGuid(Ctx.Graph, Ctx.Usage, ParseGuid(ModuleNodeGuid));
	if (!FC) return ErrorResult(TEXT("ResetModuleInput"), TEXT("Module not found"));

	FNiagaraParameterHandle ModuleHandle(TEXT("Module"), FName(*InputName));
	FNiagaraParameterHandle AliasedHandle = FNiagaraParameterHandle::CreateAliasedModuleParameterHandle(ModuleHandle, FC);

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "ResetInput", "UCP: Reset Module Input"));

	// Remove rapid iteration parameter if any
	if (Ctx.Script)
	{
		FString EmitterName;
		if (Ctx.Emitter) EmitterName = Ctx.Emitter->GetUniqueEmitterName();
		FString RIName = FNiagaraUtilities::CreateRapidIterationConstantName(
			AliasedHandle.GetParameterHandleString(), EmitterName.IsEmpty() ? nullptr : *EmitterName, Ctx.Usage);

		TArray<FNiagaraVariable> RIParams;
		Ctx.Script->RapidIterationParameters.GetParameters(RIParams);
		for (const FNiagaraVariable& P : RIParams)
		{
			if (P.GetName().ToString() == RIName)
			{
				Ctx.Script->RapidIterationParameters.RemoveParameter(P);
				break;
			}
		}
	}

	// Find the actual input type for the override pin
	FNiagaraTypeDefinition InputType;
	for (const FNiagaraVariable& V : FC->Signature.Inputs)
	{
		FString VName = V.GetName().ToString();
		if (VName == InputName || VName.EndsWith(TEXT(".") + InputName) || VName == TEXT("Module.") + InputName)
		{
			InputType = V.GetType();
			break;
		}
	}
	if (!InputType.IsValid())
		InputType = FNiagaraTypeDefinition::GetFloatDef();

	UEdGraphPin& Pin = FNiagaraStackGraphUtilities::GetOrCreateStackFunctionInputOverridePin(
		*FC, AliasedHandle, InputType, FGuid(), FGuid());
	if (Pin.LinkedTo.Num() > 0)
	{
		TArray<UEdGraphPin*> LinkedCopy = Pin.LinkedTo;
		for (UEdGraphPin* Linked : LinkedCopy)
		{
			if (Linked)
			{
				UEdGraphNode* LinkedNode = Linked->GetOwningNode();
				Pin.BreakLinkTo(Linked);
				if (LinkedNode && LinkedNode != FC)
				{
					LinkedNode->GetGraph()->RemoveNode(LinkedNode);
				}
			}
		}
	}

	Ctx.Graph->NotifyGraphChanged();
	return SuccessResult(FString::Printf(TEXT("Reset %s"), *InputName));
}

FString UNiagaraOperationLibrary::GetModuleInputs(UObject* SystemOrEmitter, const FString& ScriptUsage, const FString& ModuleNodeGuid)
{
	FResolvedContext Ctx;
	if (!ResolveContext(SystemOrEmitter, ScriptUsage, Ctx))
		return ErrorResult(TEXT("GetModuleInputs"), TEXT("Could not resolve context"));

	UNiagaraNodeFunctionCall* FC = FindModuleByGuid(Ctx.Graph, Ctx.Usage, ParseGuid(ModuleNodeGuid));
	if (!FC) return ErrorResult(TEXT("GetModuleInputs"), TEXT("Module not found"));

	FString EmitterName;
	if (Ctx.Emitter) EmitterName = Ctx.Emitter->GetUniqueEmitterName();

	TArray<TSharedPtr<FJsonValue>> Arr;

	for (const FNiagaraVariable& Var : FC->Signature.Inputs)
	{
		FString VarName = Var.GetName().ToString();
		if (Var.GetType() == FNiagaraTypeDefinition::GetParameterMapDef()) continue;

		FString ShortName = VarName;
		if (ShortName.StartsWith(TEXT("Module."))) ShortName = ShortName.Mid(7);

		TSharedPtr<FJsonObject> InputObj = MakeShared<FJsonObject>();
		InputObj->SetStringField(TEXT("name"), ShortName);
		InputObj->SetStringField(TEXT("type"), Var.GetType().GetName());

		FNiagaraParameterHandle ModuleHandle(TEXT("Module"), FName(*ShortName));
		FNiagaraParameterHandle AliasedHandle = FNiagaraParameterHandle::CreateAliasedModuleParameterHandle(ModuleHandle, FC);

		FString RIName = FNiagaraUtilities::CreateRapidIterationConstantName(
			AliasedHandle.GetParameterHandleString(), EmitterName.IsEmpty() ? nullptr : *EmitterName, Ctx.Usage);

		bool bFound = false;

		// Check rapid iteration parameters first
		if (Ctx.Script)
		{
			TArray<FNiagaraVariable> RIParams;
			Ctx.Script->RapidIterationParameters.GetParameters(RIParams);
			for (const FNiagaraVariable& RP : RIParams)
			{
				if (RP.GetName().ToString() == RIName && RP.IsDataAllocated())
				{
					InputObj->SetStringField(TEXT("mode"), TEXT("Value"));
					FString ValStr;
					const UScriptStruct* S = RP.GetType().GetScriptStruct();
					if (S) S->ExportText(ValStr, RP.GetData(), nullptr, nullptr, PPF_None, nullptr);
					InputObj->SetStringField(TEXT("value"), ValStr);
					bFound = true;
					break;
				}
			}
		}

		// Check for linked parameter or dynamic input via function call pins
		if (!bFound)
		{
			FString OverridePinName = AliasedHandle.GetParameterHandleString().ToString();
			for (UEdGraphPin* Pin : FC->Pins)
			{
				if (Pin && Pin->Direction == EGPD_Input && Pin->PinName.ToString() == OverridePinName && Pin->LinkedTo.Num() > 0)
				{
					UEdGraphPin* LinkedPin = Pin->LinkedTo[0];
					UEdGraphNode* LinkedNode = LinkedPin ? LinkedPin->GetOwningNode() : nullptr;
					if (UNiagaraNodeFunctionCall* DINode = Cast<UNiagaraNodeFunctionCall>(LinkedNode))
					{
						InputObj->SetStringField(TEXT("mode"), TEXT("DynamicInput"));
						InputObj->SetStringField(TEXT("value"), DINode->FunctionScript ? DINode->FunctionScript->GetPathName() : DINode->GetFunctionName());
					}
					else
					{
						InputObj->SetStringField(TEXT("mode"), TEXT("Binding"));
						InputObj->SetStringField(TEXT("value"), LinkedPin ? LinkedPin->PinName.ToString() : TEXT(""));
					}
					bFound = true;
					break;
				}
			}
		}

		if (!bFound)
		{
			InputObj->SetStringField(TEXT("mode"), TEXT("Default"));
		}

		Arr.Add(MakeShared<FJsonValueObject>(InputObj));
	}
	return JsonArrayToString(Arr);
}

// ---- Renderer Management ----
// Uses exported: AddRenderer, RemoveRenderer, MoveRenderer on UNiagaraEmitter

FString UNiagaraOperationLibrary::AddRenderer(UNiagaraEmitter* Emitter, const FString& RendererClassName)
{
	if (!Emitter) return ErrorResult(TEXT("AddRenderer"), TEXT("Emitter is null"));

	UClass* RC = FindObject<UClass>(nullptr, *FString::Printf(TEXT("/Script/Niagara.%s"), *RendererClassName));
	if (!RC) RC = FindFirstObject<UClass>(*RendererClassName);
	if (!RC || !RC->IsChildOf(UNiagaraRendererProperties::StaticClass()))
		return ErrorResult(TEXT("AddRenderer"), FString::Printf(TEXT("Class not found: %s"), *RendererClassName));

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "AddRenderer", "UCP: Add Renderer"));
	UNiagaraRendererProperties* R = NewObject<UNiagaraRendererProperties>(Emitter, RC, NAME_None, RF_Transactional);
	Emitter->AddRenderer(R, GetEmitterVersion(Emitter));

	TSharedPtr<FJsonObject> Res = MakeShared<FJsonObject>();
	Res->SetBoolField(TEXT("success"), true);
	Res->SetStringField(TEXT("path"), R->GetPathName());
	Res->SetStringField(TEXT("class"), RendererClassName);
	return JsonToString(Res);
}

FString UNiagaraOperationLibrary::RemoveRenderer(UNiagaraEmitter* Emitter, int32 RendererIndex)
{
	if (!Emitter) return ErrorResult(TEXT("RemoveRenderer"), TEXT("Emitter is null"));
	FVersionedNiagaraEmitterData* Data = GetEmitterData(Emitter);
	if (!Data) return ErrorResult(TEXT("RemoveRenderer"), TEXT("No data"));

	const TArray<UNiagaraRendererProperties*>& Renderers = Data->GetRenderers();
	if (!Renderers.IsValidIndex(RendererIndex))
		return ErrorResult(TEXT("RemoveRenderer"), TEXT("Invalid index"));

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "RemoveRenderer", "UCP: Remove Renderer"));
	Emitter->RemoveRenderer(Renderers[RendererIndex], GetEmitterVersion(Emitter));
	return SuccessResult(FString::Printf(TEXT("Removed renderer %d"), RendererIndex));
}

FString UNiagaraOperationLibrary::MoveRenderer(UNiagaraEmitter* Emitter, int32 RendererIndex, int32 NewIndex)
{
	if (!Emitter) return ErrorResult(TEXT("MoveRenderer"), TEXT("Emitter is null"));
	FVersionedNiagaraEmitterData* Data = GetEmitterData(Emitter);
	if (!Data) return ErrorResult(TEXT("MoveRenderer"), TEXT("No data"));

	const TArray<UNiagaraRendererProperties*>& Renderers = Data->GetRenderers();
	if (!Renderers.IsValidIndex(RendererIndex))
		return ErrorResult(TEXT("MoveRenderer"), TEXT("Invalid index"));

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "MoveRenderer", "UCP: Move Renderer"));
	Emitter->MoveRenderer(Renderers[RendererIndex], NewIndex, GetEmitterVersion(Emitter));
	return SuccessResult(FString::Printf(TEXT("Moved %d -> %d"), RendererIndex, NewIndex));
}

// ---- Event Handler Management ----

FString UNiagaraOperationLibrary::AddEventHandler(UNiagaraEmitter* Emitter)
{
	if (!Emitter) return ErrorResult(TEXT("AddEventHandler"), TEXT("Emitter is null"));

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "AddEventHandler", "UCP: Add Event Handler"));
	Emitter->Modify();

	FVersionedNiagaraEmitterData* Data = GetEmitterData(Emitter);
	if (!Data) return ErrorResult(TEXT("AddEventHandler"), TEXT("No data"));

	FNiagaraEventScriptProperties Props;
	Props.Script = NewObject<UNiagaraScript>(Emitter, NAME_None, RF_Transactional);
	Props.Script->SetUsage(ENiagaraScriptUsage::ParticleEventScript);
	Props.Script->SetUsageId(FGuid::NewGuid());
	Props.ExecutionMode = EScriptExecutionMode::EveryParticle;
	Props.SpawnNumber = 0;
	Props.MaxEventsPerFrame = 0;

	if (Data && Data->GraphSource)
	{
		Props.Script->SetLatestSource(Data->GraphSource);
	}

	Emitter->AddEventHandler(Props, GetEmitterVersion(Emitter));

	TSharedPtr<FJsonObject> R = MakeShared<FJsonObject>();
	R->SetBoolField(TEXT("success"), true);
	R->SetStringField(TEXT("usageId"), Props.Script->GetUsageId().ToString());
	return JsonToString(R);
}

FString UNiagaraOperationLibrary::RemoveEventHandler(UNiagaraEmitter* Emitter, const FString& UsageIdString)
{
	if (!Emitter) return ErrorResult(TEXT("RemoveEventHandler"), TEXT("Emitter is null"));

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "RemoveEventHandler", "UCP: Remove Event Handler"));
	Emitter->Modify();

	FVersionedNiagaraEmitterData* Data = GetEmitterData(Emitter);
	if (!Data) return ErrorResult(TEXT("RemoveEventHandler"), TEXT("No data"));

	FGuid UsageId = ParseGuid(UsageIdString);
	for (const FNiagaraEventScriptProperties& EP : Data->EventHandlerScriptProps)
	{
		if (EP.Script && EP.Script->GetUsageId() == UsageId)
		{
			Emitter->RemoveEventHandlerByUsageId(UsageId, GetEmitterVersion(Emitter));
			return SuccessResult(TEXT("Removed event handler"));
		}
	}
	return ErrorResult(TEXT("RemoveEventHandler"), TEXT("Not found"));
}

// ---- Simulation Stage Management ----
// Uses exported: AddSimulationStage, RemoveSimulationStage, MoveSimulationStageToIndex on UNiagaraEmitter

FString UNiagaraOperationLibrary::AddSimulationStage(UNiagaraEmitter* Emitter)
{
	if (!Emitter) return ErrorResult(TEXT("AddSimulationStage"), TEXT("Emitter is null"));

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "AddSimStage", "UCP: Add Simulation Stage"));

	UNiagaraSimulationStageGeneric* Stage = NewObject<UNiagaraSimulationStageGeneric>(Emitter, NAME_None, RF_Transactional);
	Stage->Script = NewObject<UNiagaraScript>(Stage, NAME_None, RF_Transactional);
	Stage->Script->SetUsage(ENiagaraScriptUsage::ParticleSimulationStageScript);
	Stage->Script->SetUsageId(FGuid::NewGuid());

	FVersionedNiagaraEmitterData* Data = GetEmitterData(Emitter);
	if (Data && Data->GraphSource)
	{
		Stage->Script->SetLatestSource(Data->GraphSource);
	}

	Emitter->AddSimulationStage(Stage, GetEmitterVersion(Emitter));

	TSharedPtr<FJsonObject> R = MakeShared<FJsonObject>();
	R->SetBoolField(TEXT("success"), true);
	R->SetStringField(TEXT("path"), Stage->GetPathName());
	R->SetStringField(TEXT("usageId"), Stage->Script->GetUsageId().ToString());
	return JsonToString(R);
}

FString UNiagaraOperationLibrary::RemoveSimulationStage(UNiagaraEmitter* Emitter, const FString& StageIdString)
{
	if (!Emitter) return ErrorResult(TEXT("RemoveSimulationStage"), TEXT("Emitter is null"));
	FVersionedNiagaraEmitterData* Data = GetEmitterData(Emitter);
	if (!Data) return ErrorResult(TEXT("RemoveSimulationStage"), TEXT("No data"));

	FGuid StageId = ParseGuid(StageIdString);
	for (UNiagaraSimulationStageBase* Stage : Data->GetSimulationStages())
	{
		if (Stage && Stage->Script && Stage->Script->GetUsageId() == StageId)
		{
			FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "RemoveSimStage", "UCP: Remove Simulation Stage"));
			Emitter->RemoveSimulationStage(Stage, GetEmitterVersion(Emitter));
			return SuccessResult(TEXT("Removed"));
		}
	}
	return ErrorResult(TEXT("RemoveSimulationStage"), TEXT("Not found"));
}

FString UNiagaraOperationLibrary::MoveSimulationStage(UNiagaraEmitter* Emitter, const FString& StageIdString, int32 NewIndex)
{
	if (!Emitter) return ErrorResult(TEXT("MoveSimulationStage"), TEXT("Emitter is null"));
	FVersionedNiagaraEmitterData* Data = GetEmitterData(Emitter);
	if (!Data) return ErrorResult(TEXT("MoveSimulationStage"), TEXT("No data"));

	FGuid StageId = ParseGuid(StageIdString);
	for (UNiagaraSimulationStageBase* Stage : Data->GetSimulationStages())
	{
		if (Stage && Stage->Script && Stage->Script->GetUsageId() == StageId)
		{
			FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "MoveSimStage", "UCP: Move Simulation Stage"));
			Emitter->MoveSimulationStageToIndex(Stage, NewIndex, GetEmitterVersion(Emitter));
			return SuccessResult(FString::Printf(TEXT("Moved to %d"), NewIndex));
		}
	}
	return ErrorResult(TEXT("MoveSimulationStage"), TEXT("Not found"));
}

// ---- Graph Parameter Operations ----
// Uses exported: GetAllMetaData, GetScriptVariable, RenameParameter

FString UNiagaraOperationLibrary::AddGraphParameter(UNiagaraScript* Script, const FString& ParamName, const FString& TypeName)
{
	if (!Script) return ErrorResult(TEXT("AddGraphParameter"), TEXT("Script is null"));
	UNiagaraScriptSource* Src = Cast<UNiagaraScriptSource>(Script->GetLatestSource());
	if (!Src || !Src->NodeGraph) return ErrorResult(TEXT("AddGraphParameter"), TEXT("No graph"));

	FNiagaraTypeDefinition TypeDef = ParseTypeDef(TypeName);
	if (!TypeDef.IsValid()) return ErrorResult(TEXT("AddGraphParameter"), FString::Printf(TEXT("Unsupported type: %s"), *TypeName));

	if (Src->NodeGraph->GetScriptVariable(FName(*ParamName)))
		return ErrorResult(TEXT("AddGraphParameter"), TEXT("Already exists"));

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "AddGraphParam", "UCP: Add Graph Parameter"));
	Src->NodeGraph->Modify();

	FNiagaraVariable NewVar(TypeDef, FName(*ParamName));
	UNiagaraScriptVariable* SV = NewObject<UNiagaraScriptVariable>(Src->NodeGraph);
	SV->Variable = NewVar;
	UNiagaraGraph::FScriptVariableMap& Map = Src->NodeGraph->GetAllMetaData();
	Map.Add(NewVar, SV);
	Src->NodeGraph->NotifyGraphChanged();

	return SuccessResult(FString::Printf(TEXT("Added %s (%s)"), *ParamName, *TypeName));
}

FString UNiagaraOperationLibrary::RemoveGraphParameter(UNiagaraScript* Script, const FString& ParamName)
{
	if (!Script) return ErrorResult(TEXT("RemoveGraphParameter"), TEXT("Script is null"));
	UNiagaraScriptSource* Src = Cast<UNiagaraScriptSource>(Script->GetLatestSource());
	if (!Src || !Src->NodeGraph) return ErrorResult(TEXT("RemoveGraphParameter"), TEXT("No graph"));

	UNiagaraScriptVariable* SV = Src->NodeGraph->GetScriptVariable(FName(*ParamName));
	if (!SV) return ErrorResult(TEXT("RemoveGraphParameter"), TEXT("Not found"));

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "RemoveGraphParam", "UCP: Remove Graph Parameter"));
	Src->NodeGraph->Modify();
	UNiagaraGraph::FScriptVariableMap& Map = Src->NodeGraph->GetAllMetaData();
	Map.Remove(SV->Variable);
	Src->NodeGraph->NotifyGraphChanged();

	return SuccessResult(FString::Printf(TEXT("Removed %s"), *ParamName));
}

FString UNiagaraOperationLibrary::RenameGraphParameter(UNiagaraScript* Script, const FString& OldName, const FString& NewName)
{
	if (!Script) return ErrorResult(TEXT("RenameGraphParameter"), TEXT("Script is null"));
	UNiagaraScriptSource* Src = Cast<UNiagaraScriptSource>(Script->GetLatestSource());
	if (!Src || !Src->NodeGraph) return ErrorResult(TEXT("RenameGraphParameter"), TEXT("No graph"));

	UNiagaraScriptVariable* SV = Src->NodeGraph->GetScriptVariable(FName(*OldName));
	if (!SV) return ErrorResult(TEXT("RenameGraphParameter"), TEXT("Not found"));

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "RenameGraphParam", "UCP: Rename Graph Parameter"));
	Src->NodeGraph->RenameParameter(SV->Variable, FName(*NewName));

	return SuccessResult(FString::Printf(TEXT("%s -> %s"), *OldName, *NewName));
}

// ---- ScratchPad Script Management ----

FString UNiagaraOperationLibrary::CreateScratchPadScript(UObject* SystemOrEmitter, const FString& ScriptName, const FString& Usage, int32 ModuleUsageBitmask)
{
	ENiagaraScriptUsage ScriptUsage = ParseScriptUsage(Usage);
	if (ScriptUsage != ENiagaraScriptUsage::Module && ScriptUsage != ENiagaraScriptUsage::DynamicInput && ScriptUsage != ENiagaraScriptUsage::Function)
	{
		if (Usage == TEXT("Module")) ScriptUsage = ENiagaraScriptUsage::Module;
		else if (Usage == TEXT("DynamicInput")) ScriptUsage = ENiagaraScriptUsage::DynamicInput;
		else if (Usage == TEXT("Function")) ScriptUsage = ENiagaraScriptUsage::Function;
		else return ErrorResult(TEXT("CreateScratchPadScript"), FString::Printf(TEXT("Invalid usage: %s (expected Module/DynamicInput/Function)"), *Usage));
	}

	UObject* ScriptOuter = nullptr;
	TArray<TObjectPtr<UNiagaraScript>>* TargetScripts = nullptr;

	if (UNiagaraSystem* System = Cast<UNiagaraSystem>(SystemOrEmitter))
	{
		ScriptOuter = System;
		TargetScripts = &System->ScratchPadScripts;
	}
	else if (UNiagaraEmitter* Emitter = Cast<UNiagaraEmitter>(SystemOrEmitter))
	{
		FVersionedNiagaraEmitterData* Data = GetEmitterData(Emitter);
		if (Data)
		{
			if (!Data->ScratchPads)
			{
				Data->ScratchPads = NewObject<UNiagaraScratchPadContainer>(Emitter, NAME_None, RF_Transactional);
			}
			ScriptOuter = Data->ScratchPads;
			TargetScripts = &Data->ScratchPads->Scripts;
		}
	}

	if (!ScriptOuter || !TargetScripts)
		return ErrorResult(TEXT("CreateScratchPadScript"), TEXT("Invalid target (pass System or Emitter)"));

	FScopedTransaction Tx(NSLOCTEXT("UCPNiagara", "CreateScratchPad", "UCP: Create ScratchPad Script"));
	ScriptOuter->Modify();

	UNiagaraScript* NewScript = NewObject<UNiagaraScript>(ScriptOuter, FName(*ScriptName), RF_Transactional);
	NewScript->SetUsage(ScriptUsage);

	UNiagaraScriptSource* Source = NewObject<UNiagaraScriptSource>(NewScript, NAME_None, RF_Transactional);
	Source->NodeGraph = NewObject<UNiagaraGraph>(Source, NAME_None, RF_Transactional);
	NewScript->SetLatestSource(Source);

	NewScript->ClearFlags(RF_Public | RF_Standalone);

	if (ModuleUsageBitmask != 0)
	{
		FVersionedNiagaraScriptData* ScriptData = NewScript->GetLatestScriptData();
		if (ScriptData)
		{
			ScriptData->ModuleUsageBitmask = ModuleUsageBitmask;
		}
	}

	TargetScripts->Add(NewScript);

	TSharedPtr<FJsonObject> R = MakeShared<FJsonObject>();
	R->SetBoolField(TEXT("success"), true);
	R->SetStringField(TEXT("name"), NewScript->GetName());
	R->SetStringField(TEXT("objectPath"), NewScript->GetPathName());
	return JsonToString(R);
}
