// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "NodeCode/NodeCodeTypes.h"
#include "NiagaraCommon.h"

class UNiagaraSystem;
class UNiagaraEmitter;
class UNiagaraScript;
class UNiagaraGraph;
class UNiagaraNode;
struct FVersionedNiagaraEmitterData;

class FNiagaraGraphSerializer
{
public:
	static TArray<FNodeCodeSectionIR> ListSections(UNiagaraSystem* System);
	static TArray<FNodeCodeSectionIR> ListSections(UNiagaraEmitter* Emitter);
	static TArray<FNodeCodeSectionIR> ListSections(UNiagaraScript* Script);

	static FNodeCodeGraphIR BuildIR(UNiagaraGraph* Graph, ENiagaraScriptUsage Usage, FGuid UsageId);

	struct FGraphAndUsage
	{
		UNiagaraGraph* Graph = nullptr;
		ENiagaraScriptUsage Usage = ENiagaraScriptUsage::Module;
		FGuid UsageId;
		UNiagaraScript* Script = nullptr;
	};

	static FGraphAndUsage FindGraphAndUsage(UObject* Asset, const FString& Type, const FString& Name);

	static TMap<FString, FString> ReadSystemProperties(UNiagaraSystem* System);
	static TMap<FString, FString> ReadEmitters(UNiagaraSystem* System);
	static TMap<FString, FString> ReadUserParameters(UNiagaraSystem* System);
	static TMap<FString, FString> ReadEmitterProperties(UNiagaraEmitter* Emitter);
	static TMap<FString, FString> ReadParticleAttributes(UNiagaraEmitter* Emitter);
	static TMap<FString, FString> ReadRenderers(UNiagaraEmitter* Emitter);
	static TMap<FString, FString> ReadEventHandlers(UNiagaraEmitter* Emitter);
	static TMap<FString, FString> ReadSimulationStages(UNiagaraEmitter* Emitter);
	static TMap<FString, FString> ReadScratchPadScripts(UNiagaraSystem* System);
	static TMap<FString, FString> ReadScratchPadScripts(UNiagaraEmitter* Emitter);

private:
	static void SerializeNodeProperties(UNiagaraNode* Node, TMap<FString, FString>& OutProperties);
	static FVersionedNiagaraEmitterData* GetEmitterData(UNiagaraEmitter* Emitter);
};
