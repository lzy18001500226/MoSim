// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "NiagaraOperationLibrary.generated.h"

class UNiagaraSystem;
class UNiagaraEmitter;
class UNiagaraScript;

UCLASS()
class UNiagaraOperationLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString AddEmitter(UNiagaraSystem* System, UNiagaraEmitter* SourceEmitter, const FString& Name);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString RemoveEmitter(UNiagaraSystem* System, const FString& EmitterName);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString ReorderEmitter(UNiagaraSystem* System, const FString& EmitterName, int32 NewIndex);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString AddUserParameter(UNiagaraSystem* System, const FString& ParamName, const FString& TypeName, const FString& DefaultValue);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString RemoveUserParameter(UNiagaraSystem* System, const FString& ParamName);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString AddModule(UObject* SystemOrEmitter, const FString& ScriptUsage, UNiagaraScript* ModuleScript, int32 Index = -1);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString RemoveModule(UObject* SystemOrEmitter, const FString& ScriptUsage, const FString& ModuleNodeGuid);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString SetModuleEnabled(UObject* SystemOrEmitter, const FString& ScriptUsage, const FString& ModuleNodeGuid, bool bEnabled);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString GetModules(UObject* SystemOrEmitter, const FString& ScriptUsage);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString SetModuleInputValue(UObject* SystemOrEmitter, const FString& ScriptUsage, const FString& ModuleNodeGuid, const FString& InputName, const FString& Value);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString SetModuleInputBinding(UObject* SystemOrEmitter, const FString& ScriptUsage, const FString& ModuleNodeGuid, const FString& InputName, const FString& LinkedParamName);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString SetModuleInputDynamicInput(UObject* SystemOrEmitter, const FString& ScriptUsage, const FString& ModuleNodeGuid, const FString& InputName, UNiagaraScript* DynamicInputScript);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString ResetModuleInput(UObject* SystemOrEmitter, const FString& ScriptUsage, const FString& ModuleNodeGuid, const FString& InputName);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString GetModuleInputs(UObject* SystemOrEmitter, const FString& ScriptUsage, const FString& ModuleNodeGuid);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString AddRenderer(UNiagaraEmitter* Emitter, const FString& RendererClassName);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString RemoveRenderer(UNiagaraEmitter* Emitter, int32 RendererIndex);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString MoveRenderer(UNiagaraEmitter* Emitter, int32 RendererIndex, int32 NewIndex);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString AddEventHandler(UNiagaraEmitter* Emitter);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString RemoveEventHandler(UNiagaraEmitter* Emitter, const FString& UsageIdString);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString AddSimulationStage(UNiagaraEmitter* Emitter);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString RemoveSimulationStage(UNiagaraEmitter* Emitter, const FString& StageIdString);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString MoveSimulationStage(UNiagaraEmitter* Emitter, const FString& StageIdString, int32 NewIndex);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString AddGraphParameter(UNiagaraScript* Script, const FString& ParamName, const FString& TypeName);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString RemoveGraphParameter(UNiagaraScript* Script, const FString& ParamName);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString RenameGraphParameter(UNiagaraScript* Script, const FString& OldName, const FString& NewName);

	UFUNCTION(BlueprintCallable, Category = "UCP|Niagara")
	static FString CreateScratchPadScript(UObject* SystemOrEmitter, const FString& ScriptName, const FString& Usage, int32 ModuleUsageBitmask = 0);
};
