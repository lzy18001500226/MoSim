// MIT License - Copyright (c) 2025 Italink

#include "Niagara/NiagaraSectionHandler.h"
#include "Niagara/NiagaraGraphSerializer.h"
#include "Niagara/NiagaraGraphDiffer.h"
#include "NodeCode/NodeCodeTextFormat.h"

#include "NiagaraSystem.h"
#include "NiagaraEmitter.h"
#include "NiagaraScript.h"
#include "NiagaraScriptSource.h"
#include "NiagaraGraph.h"
#include "ScopedTransaction.h"

DEFINE_LOG_CATEGORY_STATIC(LogUCPNiagaraHandler, Log, All);

static const TSet<FString>& GetSystemSectionTypes()
{
	static TSet<FString> Types = {
		TEXT("SystemProperties"), TEXT("Emitters"), TEXT("UserParameters"),
		TEXT("ScratchPadScripts"),
		TEXT("SystemSpawn"), TEXT("SystemUpdate")
	};
	return Types;
}

static const TSet<FString>& GetEmitterSectionTypes()
{
	static TSet<FString> Types = {
		TEXT("EmitterProperties"), TEXT("ParticleAttributes"), TEXT("Renderers"),
		TEXT("EventHandlers"), TEXT("SimulationStages"),
		TEXT("ScratchPadScripts"),
		TEXT("EmitterSpawn"), TEXT("EmitterUpdate"),
		TEXT("ParticleSpawn"), TEXT("ParticleUpdate"),
		TEXT("ParticleEvent"), TEXT("SimulationStage")
	};
	return Types;
}

static const TSet<FString>& GetScriptSectionTypes()
{
	static TSet<FString> Types = {
		TEXT("Module"), TEXT("Function"), TEXT("DynamicInput")
	};
	return Types;
}

TArray<FNodeCodeSectionTypeInfo> FNiagaraSectionHandler::GetSupportedSectionTypes() const
{
	return {
		{TEXT("SystemProperties"), ENodeCodeSectionFormat::Properties},
		{TEXT("Emitters"), ENodeCodeSectionFormat::Properties},
		{TEXT("UserParameters"), ENodeCodeSectionFormat::Properties},
		{TEXT("ScratchPadScripts"), ENodeCodeSectionFormat::Properties},
		{TEXT("SystemSpawn"), ENodeCodeSectionFormat::Graph},
		{TEXT("SystemUpdate"), ENodeCodeSectionFormat::Graph},

		{TEXT("EmitterProperties"), ENodeCodeSectionFormat::Properties},
		{TEXT("ParticleAttributes"), ENodeCodeSectionFormat::Properties},
		{TEXT("Renderers"), ENodeCodeSectionFormat::Properties},
		{TEXT("EventHandlers"), ENodeCodeSectionFormat::Properties},
		{TEXT("SimulationStages"), ENodeCodeSectionFormat::Properties},
		{TEXT("EmitterSpawn"), ENodeCodeSectionFormat::Graph},
		{TEXT("EmitterUpdate"), ENodeCodeSectionFormat::Graph},
		{TEXT("ParticleSpawn"), ENodeCodeSectionFormat::Graph},
		{TEXT("ParticleUpdate"), ENodeCodeSectionFormat::Graph},
		{TEXT("ParticleEvent"), ENodeCodeSectionFormat::Graph},
		{TEXT("SimulationStage"), ENodeCodeSectionFormat::Graph},

		{TEXT("Module"), ENodeCodeSectionFormat::Graph},
		{TEXT("Function"), ENodeCodeSectionFormat::Graph},
		{TEXT("DynamicInput"), ENodeCodeSectionFormat::Graph}
	};
}

bool FNiagaraSectionHandler::CanHandle(UObject* Asset, const FString& Type) const
{
	if (!Asset) return false;

	bool bIsNiagara = Asset->IsA<UNiagaraSystem>()
		|| Asset->IsA<UNiagaraEmitter>()
		|| Asset->IsA<UNiagaraScript>();

	if (!bIsNiagara) return false;
	if (Type.IsEmpty()) return true;

	if (Asset->IsA<UNiagaraSystem>()) return GetSystemSectionTypes().Contains(Type);
	if (Asset->IsA<UNiagaraEmitter>()) return GetEmitterSectionTypes().Contains(Type);
	if (Asset->IsA<UNiagaraScript>()) return GetScriptSectionTypes().Contains(Type);

	return false;
}

TArray<FNodeCodeSectionIR> FNiagaraSectionHandler::ListSections(UObject* Asset)
{
	if (UNiagaraSystem* System = Cast<UNiagaraSystem>(Asset))
	{
		return FNiagaraGraphSerializer::ListSections(System);
	}
	if (UNiagaraEmitter* Emitter = Cast<UNiagaraEmitter>(Asset))
	{
		return FNiagaraGraphSerializer::ListSections(Emitter);
	}
	if (UNiagaraScript* Script = Cast<UNiagaraScript>(Asset))
	{
		return FNiagaraGraphSerializer::ListSections(Script);
	}
	return {};
}

FNodeCodeSectionIR FNiagaraSectionHandler::Read(UObject* Asset, const FString& Type, const FString& Name)
{
	FNodeCodeSectionIR Section;
	Section.Type = Type;
	Section.Name = Name;

	UNiagaraSystem* System = Cast<UNiagaraSystem>(Asset);
	UNiagaraEmitter* Emitter = Cast<UNiagaraEmitter>(Asset);

	if (Type == TEXT("SystemProperties") && System)
	{
		Section.Properties = FNiagaraGraphSerializer::ReadSystemProperties(System);
		return Section;
	}
	if (Type == TEXT("Emitters") && System)
	{
		Section.Properties = FNiagaraGraphSerializer::ReadEmitters(System);
		return Section;
	}
	if (Type == TEXT("UserParameters") && System)
	{
		Section.Properties = FNiagaraGraphSerializer::ReadUserParameters(System);
		return Section;
	}
	if (Type == TEXT("ScratchPadScripts") && System)
	{
		Section.Properties = FNiagaraGraphSerializer::ReadScratchPadScripts(System);
		return Section;
	}
	if (Type == TEXT("ScratchPadScripts") && Emitter)
	{
		Section.Properties = FNiagaraGraphSerializer::ReadScratchPadScripts(Emitter);
		return Section;
	}
	if (Type == TEXT("EmitterProperties") && Emitter)
	{
		Section.Properties = FNiagaraGraphSerializer::ReadEmitterProperties(Emitter);
		return Section;
	}
	if (Type == TEXT("ParticleAttributes") && Emitter)
	{
		Section.Properties = FNiagaraGraphSerializer::ReadParticleAttributes(Emitter);
		return Section;
	}
	if (Type == TEXT("Renderers") && Emitter)
	{
		Section.Properties = FNiagaraGraphSerializer::ReadRenderers(Emitter);
		return Section;
	}
	if (Type == TEXT("EventHandlers") && Emitter)
	{
		Section.Properties = FNiagaraGraphSerializer::ReadEventHandlers(Emitter);
		return Section;
	}
	if (Type == TEXT("SimulationStages") && Emitter)
	{
		Section.Properties = FNiagaraGraphSerializer::ReadSimulationStages(Emitter);
		return Section;
	}

	auto GraphAndUsage = FNiagaraGraphSerializer::FindGraphAndUsage(Asset, Type, Name);
	if (GraphAndUsage.Graph)
	{
		Section.Graph = FNiagaraGraphSerializer::BuildIR(GraphAndUsage.Graph, GraphAndUsage.Usage, GraphAndUsage.UsageId);
	}
	else
	{
		UE_LOG(LogUCPNiagaraHandler, Warning, TEXT("Read: Graph not found for [%s:%s]"), *Type, *Name);
	}

	return Section;
}

FNodeCodeDiffResult FNiagaraSectionHandler::Write(UObject* Asset, const FNodeCodeSectionIR& Section)
{
	FNodeCodeDiffResult Result;

	if (Section.Format == ENodeCodeSectionFormat::Properties)
	{
		UNiagaraSystem* System = Cast<UNiagaraSystem>(Asset);
		UNiagaraEmitter* Emitter = Cast<UNiagaraEmitter>(Asset);

		if (Section.Type == TEXT("ParticleAttributes"))
		{
			UE_LOG(LogUCPNiagaraHandler, Warning, TEXT("Write: ParticleAttributes is read-only (compiled data)"));
			return Result;
		}

		if (Section.Type == TEXT("ScratchPadScripts"))
		{
			UE_LOG(LogUCPNiagaraHandler, Warning, TEXT("Write: ScratchPadScripts is read-only (use CreateScratchPadScript API)"));
			return Result;
		}

		FScopedTransaction Transaction(NSLOCTEXT("UCPNiagara", "WriteProperties", "UCP: Write Niagara Properties"));

		if (Section.Type == TEXT("SystemProperties") && System)
		{
			System->Modify();
			for (const auto& Pair : Section.Properties)
			{
				FProperty* Prop = System->GetClass()->FindPropertyByName(FName(*Pair.Key));
				if (Prop)
				{
					void* ValuePtr = Prop->ContainerPtrToValuePtr<void>(System);
					Prop->ImportText_Direct(*Pair.Value, ValuePtr, System, PPF_None);
				}
			}
		}
		else if (Section.Type == TEXT("Emitters") && System)
		{
			for (const auto& Pair : Section.Properties)
			{
				for (FNiagaraEmitterHandle& Handle : System->GetEmitterHandles())
				{
					if (Handle.GetName().ToString() == Pair.Key)
					{
						TSharedPtr<FJsonObject> JsonObj;
						TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Pair.Value);
						if (FJsonSerializer::Deserialize(Reader, JsonObj) && JsonObj.IsValid())
						{
							if (JsonObj->HasField(TEXT("Enabled")))
							{
								bool bEnabled = JsonObj->GetBoolField(TEXT("Enabled"));
								Handle.SetIsEnabled(bEnabled, *System, false);
							}
						}
						break;
					}
				}
			}
		}
		else if (Section.Type == TEXT("EmitterProperties") && Emitter)
		{
			FVersionedNiagaraEmitterData* Data = Emitter->GetLatestEmitterData();
			if (Data)
			{
				Emitter->Modify();
				UScriptStruct* StructType = FVersionedNiagaraEmitterData::StaticStruct();
				for (const auto& Pair : Section.Properties)
				{
					FProperty* Prop = StructType->FindPropertyByName(FName(*Pair.Key));
					if (Prop)
					{
						void* ValuePtr = Prop->ContainerPtrToValuePtr<void>(Data);
						Prop->ImportText_Direct(*Pair.Value, ValuePtr, nullptr, PPF_None);
					}
				}
			}
		}

		return Result;
	}

	auto GraphAndUsage = FNiagaraGraphSerializer::FindGraphAndUsage(Asset, Section.Type, Section.Name);
	if (!GraphAndUsage.Graph)
	{
		UE_LOG(LogUCPNiagaraHandler, Error, TEXT("Write: Graph not found for [%s:%s]"), *Section.Type, *Section.Name);
		return Result;
	}

	Result = FNiagaraGraphDiffer::Apply(GraphAndUsage.Graph, GraphAndUsage.Usage, GraphAndUsage.UsageId, Section.Graph);

	if (Asset)
	{
		Asset->Modify(true);
	}

	return Result;
}

bool FNiagaraSectionHandler::CreateSection(UObject* Asset, const FString& Type, const FString& Name)
{
	return false;
}

bool FNiagaraSectionHandler::RemoveSection(UObject* Asset, const FString& Type, const FString& Name)
{
	return false;
}

UObject* FNiagaraSectionHandler::FindNodeByGuid(UObject* Asset, const FGuid& Guid)
{
	auto SearchGraph = [&Guid](UNiagaraScriptSourceBase* SourceBase) -> UObject*
	{
		UNiagaraScriptSource* Source = Cast<UNiagaraScriptSource>(SourceBase);
		if (!Source || !Source->NodeGraph) return nullptr;
		for (UEdGraphNode* Node : Source->NodeGraph->Nodes)
		{
			if (Node && Node->NodeGuid == Guid)
			{
				return Node;
			}
		}
		return nullptr;
	};

	if (UNiagaraSystem* System = Cast<UNiagaraSystem>(Asset))
	{
		if (UNiagaraScript* SpawnScript = System->GetSystemSpawnScript())
		{
			if (UObject* Found = SearchGraph(SpawnScript->GetLatestSource())) return Found;
		}
		if (UNiagaraScript* UpdateScript = System->GetSystemUpdateScript())
		{
			if (UObject* Found = SearchGraph(UpdateScript->GetLatestSource())) return Found;
		}
	}
	else if (UNiagaraEmitter* Emitter = Cast<UNiagaraEmitter>(Asset))
	{
		FVersionedNiagaraEmitterData* Data = Emitter->GetLatestEmitterData();
		if (Data)
		{
			if (UObject* Found = SearchGraph(Data->GraphSource)) return Found;
		}
	}
	else if (UNiagaraScript* Script = Cast<UNiagaraScript>(Asset))
	{
		if (UObject* Found = SearchGraph(Script->GetLatestSource())) return Found;
	}

	return nullptr;
}
