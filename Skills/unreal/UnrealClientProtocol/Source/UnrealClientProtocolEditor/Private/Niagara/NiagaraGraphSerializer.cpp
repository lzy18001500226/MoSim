// MIT License - Copyright (c) 2025 Italink

#include "Niagara/NiagaraGraphSerializer.h"
#include "Niagara/INiagaraNodeEncoder.h"
#include "NodeCode/NodeCodePropertyUtils.h"
#include "NodeCode/NodeCodeClassCache.h"
#include "NodeCode/NodeCodeTypes.h"

#include "NiagaraSystem.h"
#include "NiagaraEmitter.h"
#include "NiagaraScript.h"
#include "NiagaraScriptSource.h"
#include "NiagaraGraph.h"
#include "NiagaraNode.h"
#include "NiagaraNodeFunctionCall.h"
#include "NiagaraNodeInput.h"
#include "NiagaraNodeOutput.h"
#include "NiagaraNodeOp.h"
#include "NiagaraRendererProperties.h"
#include "NiagaraSimulationStageBase.h"
#include "NiagaraEmitterHandle.h"
#include "NiagaraTypes.h"
#include "NiagaraScratchPadContainer.h"

#include "Dom/JsonObject.h"
#include "Serialization/JsonWriter.h"
#include "Serialization/JsonSerializer.h"

static FString ScriptUsageToString(ENiagaraScriptUsage Usage)
{
	switch (Usage)
	{
	case ENiagaraScriptUsage::SystemSpawnScript: return TEXT("SystemSpawn");
	case ENiagaraScriptUsage::SystemUpdateScript: return TEXT("SystemUpdate");
	case ENiagaraScriptUsage::EmitterSpawnScript: return TEXT("EmitterSpawn");
	case ENiagaraScriptUsage::EmitterUpdateScript: return TEXT("EmitterUpdate");
	case ENiagaraScriptUsage::ParticleSpawnScript: return TEXT("ParticleSpawn");
	case ENiagaraScriptUsage::ParticleUpdateScript: return TEXT("ParticleUpdate");
	case ENiagaraScriptUsage::ParticleEventScript: return TEXT("ParticleEvent");
	case ENiagaraScriptUsage::ParticleSimulationStageScript: return TEXT("SimulationStage");
	case ENiagaraScriptUsage::Module: return TEXT("Module");
	case ENiagaraScriptUsage::Function: return TEXT("Function");
	case ENiagaraScriptUsage::DynamicInput: return TEXT("DynamicInput");
	default: return TEXT("Unknown");
	}
}

static ENiagaraScriptUsage StringToScriptUsage(const FString& Str)
{
	if (Str == TEXT("SystemSpawn")) return ENiagaraScriptUsage::SystemSpawnScript;
	if (Str == TEXT("SystemUpdate")) return ENiagaraScriptUsage::SystemUpdateScript;
	if (Str == TEXT("EmitterSpawn")) return ENiagaraScriptUsage::EmitterSpawnScript;
	if (Str == TEXT("EmitterUpdate")) return ENiagaraScriptUsage::EmitterUpdateScript;
	if (Str == TEXT("ParticleSpawn")) return ENiagaraScriptUsage::ParticleSpawnScript;
	if (Str == TEXT("ParticleUpdate")) return ENiagaraScriptUsage::ParticleUpdateScript;
	if (Str == TEXT("ParticleEvent")) return ENiagaraScriptUsage::ParticleEventScript;
	if (Str == TEXT("SimulationStage")) return ENiagaraScriptUsage::ParticleSimulationStageScript;
	if (Str == TEXT("Module")) return ENiagaraScriptUsage::Module;
	if (Str == TEXT("Function")) return ENiagaraScriptUsage::Function;
	if (Str == TEXT("DynamicInput")) return ENiagaraScriptUsage::DynamicInput;
	return ENiagaraScriptUsage::Module;
}

FVersionedNiagaraEmitterData* FNiagaraGraphSerializer::GetEmitterData(UNiagaraEmitter* Emitter)
{
	return Emitter ? Emitter->GetLatestEmitterData() : nullptr;
}

static UNiagaraGraph* GetGraphFromSource(UNiagaraScriptSourceBase* SourceBase)
{
	UNiagaraScriptSource* Source = Cast<UNiagaraScriptSource>(SourceBase);
	return Source ? Source->NodeGraph : nullptr;
}

// ---- List Sections ----

TArray<FNodeCodeSectionIR> FNiagaraGraphSerializer::ListSections(UNiagaraSystem* System)
{
	TArray<FNodeCodeSectionIR> Sections;
	if (!System) return Sections;

	{ FNodeCodeSectionIR S; S.Type = TEXT("SystemProperties"); Sections.Add(MoveTemp(S)); }
	{ FNodeCodeSectionIR S; S.Type = TEXT("Emitters"); Sections.Add(MoveTemp(S)); }
	{ FNodeCodeSectionIR S; S.Type = TEXT("UserParameters"); Sections.Add(MoveTemp(S)); }
	{ FNodeCodeSectionIR S; S.Type = TEXT("ScratchPadScripts"); Sections.Add(MoveTemp(S)); }
	{ FNodeCodeSectionIR S; S.Type = TEXT("SystemSpawn"); Sections.Add(MoveTemp(S)); }
	{ FNodeCodeSectionIR S; S.Type = TEXT("SystemUpdate"); Sections.Add(MoveTemp(S)); }

	return Sections;
}

TArray<FNodeCodeSectionIR> FNiagaraGraphSerializer::ListSections(UNiagaraEmitter* Emitter)
{
	TArray<FNodeCodeSectionIR> Sections;
	if (!Emitter) return Sections;

	FVersionedNiagaraEmitterData* Data = GetEmitterData(Emitter);
	if (!Data) return Sections;

	{ FNodeCodeSectionIR S; S.Type = TEXT("EmitterProperties"); Sections.Add(MoveTemp(S)); }
	{ FNodeCodeSectionIR S; S.Type = TEXT("ParticleAttributes"); Sections.Add(MoveTemp(S)); }
	{ FNodeCodeSectionIR S; S.Type = TEXT("Renderers"); Sections.Add(MoveTemp(S)); }
	{ FNodeCodeSectionIR S; S.Type = TEXT("EventHandlers"); Sections.Add(MoveTemp(S)); }
	{ FNodeCodeSectionIR S; S.Type = TEXT("SimulationStages"); Sections.Add(MoveTemp(S)); }
	{ FNodeCodeSectionIR S; S.Type = TEXT("ScratchPadScripts"); Sections.Add(MoveTemp(S)); }
	{ FNodeCodeSectionIR S; S.Type = TEXT("EmitterSpawn"); Sections.Add(MoveTemp(S)); }
	{ FNodeCodeSectionIR S; S.Type = TEXT("EmitterUpdate"); Sections.Add(MoveTemp(S)); }
	{ FNodeCodeSectionIR S; S.Type = TEXT("ParticleSpawn"); Sections.Add(MoveTemp(S)); }
	{ FNodeCodeSectionIR S; S.Type = TEXT("ParticleUpdate"); Sections.Add(MoveTemp(S)); }

	for (const FNiagaraEventScriptProperties& EventProps : Data->EventHandlerScriptProps)
	{
		FNodeCodeSectionIR S;
		S.Type = TEXT("ParticleEvent");
		S.Name = EventProps.Script ? EventProps.Script->GetUsageId().ToString() : TEXT("");
		Sections.Add(MoveTemp(S));
	}

	for (UNiagaraSimulationStageBase* Stage : Data->GetSimulationStages())
	{
		if (Stage && Stage->Script)
		{
			FNodeCodeSectionIR S;
			S.Type = TEXT("SimulationStage");
			S.Name = Stage->Script->GetUsageId().ToString();
			Sections.Add(MoveTemp(S));
		}
	}

	return Sections;
}

TArray<FNodeCodeSectionIR> FNiagaraGraphSerializer::ListSections(UNiagaraScript* Script)
{
	TArray<FNodeCodeSectionIR> Sections;
	if (!Script) return Sections;

	FNodeCodeSectionIR S;
	S.Type = ScriptUsageToString(Script->GetUsage());
	Sections.Add(MoveTemp(S));

	return Sections;
}

// ---- Build IR ----

FNodeCodeGraphIR FNiagaraGraphSerializer::BuildIR(UNiagaraGraph* Graph, ENiagaraScriptUsage Usage, FGuid UsageId)
{
	FNodeCodeGraphIR IR;
	if (!Graph) return IR;

	TArray<UNiagaraNode*> Traversal;
	Graph->BuildTraversal(Traversal, Usage, UsageId);

	if (Traversal.Num() == 0) return IR;

	TMap<UNiagaraNode*, FString> NodeToIndex;

	for (UNiagaraNode* Node : Traversal)
	{
		FString NodeId = NodeCodeUtils::GuidToBase62(Node->NodeGuid);
		NodeToIndex.Add(Node, NodeId);

		FNodeCodeNodeIR NodeIR;
		NodeIR.Index = NodeId;
		NodeIR.ClassName = FNiagaraNodeEncoderRegistry::Get().EncodeNode(Node);
		NodeIR.Guid = Node->NodeGuid;
		NodeIR.SourceObject = Node;

		SerializeNodeProperties(Node, NodeIR.Properties);

		IR.Nodes.Add(MoveTemp(NodeIR));
	}

	UNiagaraNodeOutput* OutputNode = Graph->FindEquivalentOutputNode(Usage, UsageId);

	for (UNiagaraNode* Node : Traversal)
	{
		FString FromIndex = NodeToIndex[Node];

		for (UEdGraphPin* Pin : Node->Pins)
		{
			if (Pin->Direction != EGPD_Output) continue;

			for (UEdGraphPin* LinkedPin : Pin->LinkedTo)
			{
				UNiagaraNode* LinkedNode = Cast<UNiagaraNode>(LinkedPin->GetOwningNode());
				if (!LinkedNode) continue;

				FString* ToIndexPtr = NodeToIndex.Find(LinkedNode);
				if (!ToIndexPtr) continue;

				FNodeCodeLinkIR Link;
				Link.FromNodeIndex = FromIndex;
				Link.FromOutputName = Pin->PinName.ToString();
				Link.ToNodeIndex = *ToIndexPtr;
				Link.ToInputName = LinkedPin->PinName.ToString();
				Link.bToGraphOutput = (LinkedNode == OutputNode);

				IR.Links.Add(MoveTemp(Link));
			}
		}
	}

	return IR;
}

// ---- Find Graph and Usage ----

FNiagaraGraphSerializer::FGraphAndUsage FNiagaraGraphSerializer::FindGraphAndUsage(UObject* Asset, const FString& Type, const FString& Name)
{
	FGraphAndUsage Result;

	UNiagaraSystem* System = Cast<UNiagaraSystem>(Asset);
	UNiagaraEmitter* Emitter = Cast<UNiagaraEmitter>(Asset);
	UNiagaraScript* Script = Cast<UNiagaraScript>(Asset);

	if (System)
	{
		Result.Usage = StringToScriptUsage(Type);

		if (UNiagaraScript::IsSystemScript(Result.Usage))
		{
			UNiagaraScript* SysScript = (Result.Usage == ENiagaraScriptUsage::SystemSpawnScript)
				? System->GetSystemSpawnScript() : System->GetSystemUpdateScript();
			if (SysScript)
			{
				Result.Script = SysScript;
				Result.Graph = GetGraphFromSource(SysScript->GetLatestSource());
			}
		}
	}
	else if (Emitter)
	{
		FVersionedNiagaraEmitterData* Data = GetEmitterData(Emitter);
		if (Data)
		{
			Result.Usage = StringToScriptUsage(Type);
			Result.Graph = GetGraphFromSource(Data->GraphSource);

			if (!Name.IsEmpty())
			{
				FGuid::Parse(Name, Result.UsageId);
			}

			if (Result.Usage == ENiagaraScriptUsage::ParticleSpawnScript) Result.Script = Data->SpawnScriptProps.Script;
			else if (Result.Usage == ENiagaraScriptUsage::ParticleUpdateScript) Result.Script = Data->UpdateScriptProps.Script;
			else if (Result.Usage == ENiagaraScriptUsage::EmitterSpawnScript) Result.Script = Data->EmitterSpawnScriptProps.Script;
			else if (Result.Usage == ENiagaraScriptUsage::EmitterUpdateScript) Result.Script = Data->EmitterUpdateScriptProps.Script;
		}
	}
	else if (Script)
	{
		Result.Usage = Script->GetUsage();
		Result.Script = Script;
		Result.Graph = GetGraphFromSource(Script->GetLatestSource());
	}

	return Result;
}

// ---- Read Properties ----

TMap<FString, FString> FNiagaraGraphSerializer::ReadSystemProperties(UNiagaraSystem* System)
{
	TMap<FString, FString> Props;
	if (!System) return Props;

	Props.Add(TEXT("WarmupTime"), FString::SanitizeFloat(System->GetWarmupTime()));
	Props.Add(TEXT("WarmupTickCount"), FString::FromInt(System->GetWarmupTickCount()));
	Props.Add(TEXT("WarmupTickDelta"), FString::SanitizeFloat(System->GetWarmupTickDelta()));
	Props.Add(TEXT("bFixedBounds"), System->GetFixedBounds().IsValid ? TEXT("true") : TEXT("false"));
	Props.Add(TEXT("bSupportLargeWorldCoordinates"), System->SupportsLargeWorldCoordinates() ? TEXT("true") : TEXT("false"));

	if (System->GetEffectType())
	{
		Props.Add(TEXT("EffectType"), System->GetEffectType()->GetPathName());
	}

	return Props;
}

TMap<FString, FString> FNiagaraGraphSerializer::ReadEmitters(UNiagaraSystem* System)
{
	TMap<FString, FString> Props;
	if (!System) return Props;

	for (const FNiagaraEmitterHandle& Handle : System->GetEmitterHandles())
	{
		TSharedPtr<FJsonObject> EmitterJson = MakeShared<FJsonObject>();
		EmitterJson->SetBoolField(TEXT("Enabled"), Handle.GetIsEnabled() ? true : false);

		UNiagaraEmitter* Instance = Handle.GetInstance().Emitter;
		if (Instance)
		{
			EmitterJson->SetStringField(TEXT("ObjectPath"), Instance->GetPathName());

			FVersionedNiagaraEmitterData* Data = Instance->GetLatestEmitterData();
			if (Data)
			{
				EmitterJson->SetStringField(TEXT("SimTarget"), Data->SimTarget == ENiagaraSimTarget::CPUSim ? TEXT("CPUSim") : TEXT("GPUCompute"));
			}
		}

		FString JsonStr;
		auto Writer = TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&JsonStr);
		FJsonSerializer::Serialize(EmitterJson.ToSharedRef(), Writer);
		Props.Add(Handle.GetName().ToString(), JsonStr);
	}

	return Props;
}

TMap<FString, FString> FNiagaraGraphSerializer::ReadUserParameters(UNiagaraSystem* System)
{
	TMap<FString, FString> Props;
	if (!System) return Props;

	TArray<FNiagaraVariable> Params;
	System->GetExposedParameters().GetParameters(Params);

	for (const FNiagaraVariable& Var : Params)
	{
		FString Name = Var.GetName().ToString();
		if (!Name.StartsWith(TEXT("User."))) continue;

		FString ShortName = Name.Mid(5);

		TSharedPtr<FJsonObject> ParamJson = MakeShared<FJsonObject>();
		ParamJson->SetStringField(TEXT("Type"), Var.GetType().GetName());

		if (Var.IsDataAllocated())
		{
			FString ValueStr;
			const UScriptStruct* Struct = Var.GetType().GetScriptStruct();
			if (Struct)
			{
				Struct->ExportText(ValueStr, Var.GetData(), nullptr, nullptr, PPF_None, nullptr);
			}
			ParamJson->SetStringField(TEXT("Value"), ValueStr);
		}

		FString JsonStr;
		auto Writer = TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&JsonStr);
		FJsonSerializer::Serialize(ParamJson.ToSharedRef(), Writer);
		Props.Add(ShortName, JsonStr);
	}

	return Props;
}

TMap<FString, FString> FNiagaraGraphSerializer::ReadEmitterProperties(UNiagaraEmitter* Emitter)
{
	TMap<FString, FString> Props;
	if (!Emitter) return Props;

	FVersionedNiagaraEmitterData* Data = GetEmitterData(Emitter);
	if (!Data) return Props;

	Props.Add(TEXT("SimTarget"), Data->SimTarget == ENiagaraSimTarget::CPUSim ? TEXT("CPUSim") : TEXT("GPUCompute"));
	Props.Add(TEXT("bLocalSpace"), Data->bLocalSpace ? TEXT("true") : TEXT("false"));
	Props.Add(TEXT("bDeterminism"), Data->bDeterminism ? TEXT("true") : TEXT("false"));
	Props.Add(TEXT("RandomSeed"), FString::FromInt(Data->RandomSeed));
	Props.Add(TEXT("AllocationMode"), StaticEnum<EParticleAllocationMode>()->GetNameStringByValue((int64)Data->AllocationMode));
	Props.Add(TEXT("PreAllocationCount"), FString::FromInt(Data->PreAllocationCount));
	Props.Add(TEXT("bRequiresPersistentIDs"), Data->bRequiresPersistentIDs ? TEXT("true") : TEXT("false"));
	Props.Add(TEXT("MaxGPUParticlesSpawnPerFrame"), FString::FromInt(Data->MaxGPUParticlesSpawnPerFrame));

	if (Data->CalculateBoundsMode != ENiagaraEmitterCalculateBoundMode::Dynamic)
	{
		Props.Add(TEXT("CalculateBoundsMode"), StaticEnum<ENiagaraEmitterCalculateBoundMode>()->GetNameStringByValue((int64)Data->CalculateBoundsMode));
	}

	if (Data->VersionedParent.Emitter)
	{
		Props.Add(TEXT("ParentEmitter"), Data->VersionedParent.Emitter->GetPathName());
	}

	return Props;
}

TMap<FString, FString> FNiagaraGraphSerializer::ReadParticleAttributes(UNiagaraEmitter* Emitter)
{
	TMap<FString, FString> Props;
	if (!Emitter) return Props;

	FVersionedNiagaraEmitterData* Data = GetEmitterData(Emitter);
	if (!Data) return Props;

	TArray<FNiagaraVariableBase> Attributes;
	Data->GatherCompiledParticleAttributes(Attributes);

	for (const FNiagaraVariableBase& Attr : Attributes)
	{
		Props.Add(Attr.GetName().ToString(), Attr.GetType().GetName());
	}

	return Props;
}

TMap<FString, FString> FNiagaraGraphSerializer::ReadRenderers(UNiagaraEmitter* Emitter)
{
	TMap<FString, FString> Props;
	if (!Emitter) return Props;

	FVersionedNiagaraEmitterData* Data = GetEmitterData(Emitter);
	if (!Data) return Props;

	const TArray<UNiagaraRendererProperties*>& Renderers = Data->GetRenderers();
	for (int32 i = 0; i < Renderers.Num(); ++i)
	{
		if (!Renderers[i]) continue;

		TSharedPtr<FJsonObject> RJson = MakeShared<FJsonObject>();
		RJson->SetStringField(TEXT("Class"), Renderers[i]->GetClass()->GetName());
		RJson->SetStringField(TEXT("ObjectPath"), Renderers[i]->GetPathName());
		RJson->SetBoolField(TEXT("Enabled"), Renderers[i]->GetIsEnabled() ? true : false);

		FString JsonStr;
		auto Writer = TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&JsonStr);
		FJsonSerializer::Serialize(RJson.ToSharedRef(), Writer);
		Props.Add(FString::FromInt(i), JsonStr);
	}

	return Props;
}

TMap<FString, FString> FNiagaraGraphSerializer::ReadEventHandlers(UNiagaraEmitter* Emitter)
{
	TMap<FString, FString> Props;
	if (!Emitter) return Props;

	FVersionedNiagaraEmitterData* Data = GetEmitterData(Emitter);
	if (!Data) return Props;

	for (int32 i = 0; i < Data->EventHandlerScriptProps.Num(); ++i)
	{
		const FNiagaraEventScriptProperties& EventProps = Data->EventHandlerScriptProps[i];

		TSharedPtr<FJsonObject> EJson = MakeShared<FJsonObject>();
		EJson->SetStringField(TEXT("SourceEventName"), EventProps.SourceEventName.ToString());
		EJson->SetStringField(TEXT("SourceEmitterID"), EventProps.SourceEmitterID.ToString());
		EJson->SetStringField(TEXT("ExecutionMode"), StaticEnum<EScriptExecutionMode>()->GetNameStringByValue((int64)EventProps.ExecutionMode));
		EJson->SetNumberField(TEXT("SpawnNumber"), EventProps.SpawnNumber);
		EJson->SetNumberField(TEXT("MaxEventsPerFrame"), EventProps.MaxEventsPerFrame);

		if (EventProps.Script)
		{
			EJson->SetStringField(TEXT("UsageId"), EventProps.Script->GetUsageId().ToString());
		}

		FString JsonStr;
		auto Writer = TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&JsonStr);
		FJsonSerializer::Serialize(EJson.ToSharedRef(), Writer);
		Props.Add(FString::FromInt(i), JsonStr);
	}

	return Props;
}

TMap<FString, FString> FNiagaraGraphSerializer::ReadSimulationStages(UNiagaraEmitter* Emitter)
{
	TMap<FString, FString> Props;
	if (!Emitter) return Props;

	FVersionedNiagaraEmitterData* Data = GetEmitterData(Emitter);
	if (!Data) return Props;

	const TArray<UNiagaraSimulationStageBase*>& Stages = Data->GetSimulationStages();
	for (int32 i = 0; i < Stages.Num(); ++i)
	{
		if (!Stages[i]) continue;

		TSharedPtr<FJsonObject> SJson = MakeShared<FJsonObject>();
		SJson->SetStringField(TEXT("Name"), Stages[i]->SimulationStageName.ToString());
		SJson->SetBoolField(TEXT("Enabled"), Stages[i]->bEnabled != 0);
		SJson->SetStringField(TEXT("ObjectPath"), Stages[i]->GetPathName());
		SJson->SetStringField(TEXT("Class"), Stages[i]->GetClass()->GetName());

		if (Stages[i]->Script)
		{
			SJson->SetStringField(TEXT("UsageId"), Stages[i]->Script->GetUsageId().ToString());
		}

		FString JsonStr;
		auto Writer = TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&JsonStr);
		FJsonSerializer::Serialize(SJson.ToSharedRef(), Writer);
		Props.Add(FString::FromInt(i), JsonStr);
	}

	return Props;
}

// ---- Read ScratchPad Scripts ----

static TMap<FString, FString> SerializeScratchPadScripts(const TArray<TObjectPtr<UNiagaraScript>>& Scripts)
{
	TMap<FString, FString> Props;
	for (UNiagaraScript* SP : Scripts)
	{
		if (!SP) continue;

		TSharedPtr<FJsonObject> SPJson = MakeShared<FJsonObject>();
		SPJson->SetStringField(TEXT("Usage"), ScriptUsageToString(SP->GetUsage()));
		SPJson->SetStringField(TEXT("ObjectPath"), SP->GetPathName());

		FVersionedNiagaraScriptData* ScriptData = SP->GetLatestScriptData();
		if (ScriptData)
		{
			SPJson->SetNumberField(TEXT("ModuleUsageBitmask"), ScriptData->ModuleUsageBitmask);
		}

		FString JsonStr;
		auto Writer = TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&JsonStr);
		FJsonSerializer::Serialize(SPJson.ToSharedRef(), Writer);
		Props.Add(SP->GetName(), JsonStr);
	}
	return Props;
}

TMap<FString, FString> FNiagaraGraphSerializer::ReadScratchPadScripts(UNiagaraSystem* System)
{
	if (!System) return {};
	return SerializeScratchPadScripts(System->ScratchPadScripts);
}

TMap<FString, FString> FNiagaraGraphSerializer::ReadScratchPadScripts(UNiagaraEmitter* Emitter)
{
	if (!Emitter) return {};
	FVersionedNiagaraEmitterData* Data = GetEmitterData(Emitter);
	if (!Data || !Data->ScratchPads) return {};
	return SerializeScratchPadScripts(Data->ScratchPads->Scripts);
}

// ---- Serialize Node Properties ----

void FNiagaraGraphSerializer::SerializeNodeProperties(UNiagaraNode* Node, TMap<FString, FString>& OutProperties)
{
	if (!Node) return;

	const TSet<FName>& EdGraphSkip = FNodeCodePropertyUtils::GetEdGraphNodeSkipSet();
	const TSet<FName>& NiagaraSkip = FNodeCodePropertyUtils::GetNiagaraNodeSkipSet();

	if (UNiagaraNodeOp* OpNode = Cast<UNiagaraNodeOp>(Node))
	{
		OutProperties.Add(TEXT("OpName"), OpNode->OpName.ToString());
	}

	if (UNiagaraNodeInput* InputNode = Cast<UNiagaraNodeInput>(Node))
	{
		OutProperties.Add(TEXT("Usage"), StaticEnum<ENiagaraInputNodeUsage>()->GetNameStringByValue((int64)InputNode->Usage));

		FString InputStr = InputNode->Input.GetName().ToString();
		if (!InputStr.IsEmpty())
		{
			OutProperties.Add(TEXT("Input"), InputStr);
		}
	}

	if (UNiagaraNodeFunctionCall* FCNode = Cast<UNiagaraNodeFunctionCall>(Node))
	{
		if (!FCNode->FunctionSpecifiers.IsEmpty())
		{
			TArray<FString> SpecParts;
			for (const auto& Pair : FCNode->FunctionSpecifiers)
			{
				SpecParts.Add(FString::Printf(TEXT("%s=%s"), *Pair.Key.ToString(), *Pair.Value.ToString()));
			}
			OutProperties.Add(TEXT("FunctionSpecifiers"), FString::Join(SpecParts, TEXT(",")));
		}
	}

	UClass* NodeClass = Node->GetClass();
	for (TFieldIterator<FProperty> PropIt(NodeClass); PropIt; ++PropIt)
	{
		FProperty* Prop = *PropIt;
		FName PropName = Prop->GetFName();

		if (FNodeCodePropertyUtils::ShouldSkipProperty(Prop)) continue;
		if (EdGraphSkip.Contains(PropName)) continue;
		if (NiagaraSkip.Contains(PropName)) continue;
		if (OutProperties.Contains(PropName.ToString())) continue;

		if (Prop->IsA<FObjectPropertyBase>()) continue;
		if (Prop->IsA<FArrayProperty>()) continue;
		if (Prop->IsA<FMapProperty>()) continue;
		if (Prop->IsA<FSetProperty>()) continue;

		const void* ValuePtr = Prop->ContainerPtrToValuePtr<void>(Node);
		const void* DefaultPtr = Prop->ContainerPtrToValuePtr<void>(NodeClass->GetDefaultObject());

		if (Prop->Identical(ValuePtr, DefaultPtr)) continue;

		FString Value = FNodeCodePropertyUtils::FormatPropertyValue(Prop, ValuePtr, Node);
		if (!Value.IsEmpty())
		{
			OutProperties.Add(PropName.ToString(), Value);
		}
	}
}
