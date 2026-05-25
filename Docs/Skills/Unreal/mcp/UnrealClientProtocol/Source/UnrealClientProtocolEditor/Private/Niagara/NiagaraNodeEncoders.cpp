// MIT License - Copyright (c) 2025 Italink

#include "Niagara/INiagaraNodeEncoder.h"
#include "NodeCode/NodeCodeTypes.h"
#include "NodeCode/NodeCodeClassCache.h"

#include "NiagaraGraph.h"
#include "NiagaraNode.h"
#include "NiagaraNodeFunctionCall.h"
#include "NiagaraNodeInput.h"
#include "NiagaraNodeOutput.h"
#include "NiagaraNodeOp.h"
#include "NiagaraNodeCustomHlsl.h"
#include "NiagaraNodeAssignment.h"
#include "NiagaraScript.h"
#include "NiagaraSystem.h"
#include "NiagaraEmitter.h"
#include "NiagaraScratchPadContainer.h"
#include "NiagaraDataInterface.h"
#include "NiagaraTypes.h"

// UNiagaraNodeParameterMapGet/Set are in NiagaraEditor Private headers,
// so we use runtime class name checks instead of direct IsA<>.

static bool IsParameterMapGetNode(const UNiagaraNode* Node)
{
	return Node && Node->GetClass()->GetName() == TEXT("NiagaraNodeParameterMapGet");
}

static bool IsParameterMapSetNode(const UNiagaraNode* Node)
{
	return Node && Node->GetClass()->GetName() == TEXT("NiagaraNodeParameterMapSet");
}

static bool IsParameterMapBaseNode(const UNiagaraNode* Node)
{
	return IsParameterMapGetNode(Node) || IsParameterMapSetNode(Node);
}

static UNiagaraNode* CreateNodeByClassName(UNiagaraGraph* Graph, const FString& ClassName)
{
	UClass* NodeClass = FNodeCodeClassCache::Get().FindClass(ClassName);
	if (!NodeClass) NodeClass = FNodeCodeClassCache::Get().FindClass(TEXT("NiagaraNode") + ClassName);
	if (!NodeClass || !NodeClass->IsChildOf(UEdGraphNode::StaticClass())) return nullptr;

	UEdGraphNode* EdNode = NewObject<UEdGraphNode>(Graph, NodeClass, NAME_None, RF_Transactional);
	Graph->AddNode(EdNode, false, false);
	EdNode->CreateNewGuid();
	EdNode->PostPlacedNewNode();
	EdNode->AllocateDefaultPins();
	return Cast<UNiagaraNode>(EdNode);
}

// ---- Registry ----

FNiagaraNodeEncoderRegistry& FNiagaraNodeEncoderRegistry::Get()
{
	static FNiagaraNodeEncoderRegistry Instance;
	return Instance;
}

void FNiagaraNodeEncoderRegistry::Register(TSharedPtr<INiagaraNodeEncoder> Encoder)
{
	if (Encoder.IsValid()) Encoders.Add(Encoder);
}

FString FNiagaraNodeEncoderRegistry::EncodeNode(UNiagaraNode* Node) const
{
	for (const auto& Encoder : Encoders)
	{
		if (Encoder->CanEncode(Node)) return Encoder->Encode(Node);
	}
	return FNodeCodeClassCache::Get().GetSerializableName(Node->GetClass());
}

UNiagaraNode* FNiagaraNodeEncoderRegistry::DecodeNode(const FString& ClassName, UNiagaraGraph* Graph, const FNodeCodeNodeIR& IR) const
{
	for (const auto& Encoder : Encoders)
	{
		if (Encoder->CanDecode(ClassName)) return Encoder->CreateNode(Graph, IR);
	}
	return CreateNodeByClassName(Graph, ClassName);
}

// ---- FunctionCall Encoder ----

class FFunctionCallEncoder : public INiagaraNodeEncoder
{
public:
	virtual bool CanEncode(UNiagaraNode* Node) const override
	{
		return Node->IsA<UNiagaraNodeFunctionCall>()
			&& !Node->IsA<UNiagaraNodeAssignment>()
			&& !Node->IsA<UNiagaraNodeCustomHlsl>();
	}

	virtual FString Encode(UNiagaraNode* Node) const override
	{
		UNiagaraNodeFunctionCall* FC = CastChecked<UNiagaraNodeFunctionCall>(Node);

		if (FC->FunctionScript && !FC->FunctionScript->IsAsset())
		{
			return FString::Printf(TEXT("FunctionCall:ScratchPad:%s"), *FC->FunctionScript->GetName());
		}

		FString ScriptName;
		if (FC->FunctionScript)
		{
			ScriptName = FC->FunctionScript->GetPathName();
		}
		else
		{
			ScriptName = FC->FunctionScriptAssetObjectPath.ToString();
		}

		if (ScriptName.IsEmpty() || ScriptName == TEXT("None"))
		{
			UClass* DIClass = nullptr;
			if (FC->Signature.bMemberFunction && FC->Signature.Inputs.Num() > 0)
			{
				DIClass = FC->Signature.Inputs[0].GetType().GetClass();
			}
			FString DIClassName = DIClass ? DIClass->GetPathName() : TEXT("Unknown");
			FString SigName = FC->Signature.Name.ToString();
			return FString::Printf(TEXT("FunctionCall:DI:%s:%s"), *DIClassName, *SigName);
		}

		return FString::Printf(TEXT("FunctionCall:%s"), *ScriptName);
	}

	virtual bool CanDecode(const FString& ClassName) const override
	{
		return ClassName.StartsWith(TEXT("FunctionCall:"));
	}

	virtual UNiagaraNode* CreateNode(UNiagaraGraph* Graph, const FNodeCodeNodeIR& IR) const override
	{
		FString ScriptPath = IR.ClassName.Mid(13); // strip "FunctionCall:"

		if (ScriptPath.StartsWith(TEXT("DI:")))
		{
			FString DIInfo = ScriptPath.Mid(3); // strip "DI:"
			FString DIClassPath, SigName;
			DIInfo.Split(TEXT(":"), &DIClassPath, &SigName);

			UClass* DIClass = FindObject<UClass>(nullptr, *DIClassPath);
			if (!DIClass) DIClass = LoadObject<UClass>(nullptr, *DIClassPath);

			if (DIClass)
			{
				UNiagaraDataInterface* DIDefaultObj = Cast<UNiagaraDataInterface>(DIClass->GetDefaultObject());
				if (DIDefaultObj)
				{
					TArray<FNiagaraFunctionSignature> Sigs;
					DIDefaultObj->GetFunctionSignatures(Sigs);
					for (const FNiagaraFunctionSignature& Sig : Sigs)
					{
						if (Sig.Name == FName(*SigName))
						{
							UNiagaraNodeFunctionCall* Node = NewObject<UNiagaraNodeFunctionCall>(Graph, NAME_None, RF_Transactional);
							Node->Signature = Sig;
							Graph->AddNode(Node, false, false);
							Node->CreateNewGuid();
							Node->PostPlacedNewNode();
							Node->AllocateDefaultPins();
							return Node;
						}
					}
				}
			}
			return nullptr;
		}

		UNiagaraScript* Script = nullptr;

		if (ScriptPath.StartsWith(TEXT("ScratchPad:")))
		{
			FString ScriptName = ScriptPath.Mid(11); // strip "ScratchPad:"
			Script = FindScratchPadScript(Graph, ScriptName);
		}
		else
		{
			Script = LoadObject<UNiagaraScript>(nullptr, *ScriptPath);
		}

		if (!Script) return nullptr;

		UNiagaraNodeFunctionCall* Node = NewObject<UNiagaraNodeFunctionCall>(Graph, NAME_None, RF_Transactional);
		Node->FunctionScript = Script;
		Graph->AddNode(Node, false, false);
		Node->CreateNewGuid();
		Node->PostPlacedNewNode();
		Node->AllocateDefaultPins();
		return Node;
	}

private:
	static UNiagaraScript* FindScratchPadScript(UNiagaraGraph* Graph, const FString& ScriptName)
	{
		if (!Graph) return nullptr;

		if (UNiagaraSystem* System = Graph->GetTypedOuter<UNiagaraSystem>())
		{
			for (UNiagaraScript* SP : System->ScratchPadScripts)
			{
				if (SP && SP->GetName() == ScriptName) return SP;
			}
		}

		if (UNiagaraEmitter* Emitter = Graph->GetTypedOuter<UNiagaraEmitter>())
		{
			FVersionedNiagaraEmitterData* Data = Emitter->GetLatestEmitterData();
			if (Data && Data->ScratchPads)
			{
				for (UNiagaraScript* SP : Data->ScratchPads->Scripts)
				{
					if (SP && SP->GetName() == ScriptName) return SP;
				}
			}
		}

		return nullptr;
	}
};

// ---- Assignment Encoder ----

class FAssignmentEncoder : public INiagaraNodeEncoder
{
public:
	virtual bool CanEncode(UNiagaraNode* Node) const override { return Node->IsA<UNiagaraNodeAssignment>(); }
	virtual FString Encode(UNiagaraNode* Node) const override { return TEXT("Assignment"); }
	virtual bool CanDecode(const FString& ClassName) const override { return ClassName == TEXT("Assignment"); }

	virtual UNiagaraNode* CreateNode(UNiagaraGraph* Graph, const FNodeCodeNodeIR& IR) const override
	{
		UNiagaraNodeAssignment* Node = NewObject<UNiagaraNodeAssignment>(Graph, NAME_None, RF_Transactional);
		Graph->AddNode(Node, false, false);
		Node->CreateNewGuid();
		Node->PostPlacedNewNode();
		Node->AllocateDefaultPins();
		return Node;
	}
};

// ---- CustomHlsl Encoder ----

class FCustomHlslEncoder : public INiagaraNodeEncoder
{
public:
	virtual bool CanEncode(UNiagaraNode* Node) const override { return Node->IsA<UNiagaraNodeCustomHlsl>(); }
	virtual FString Encode(UNiagaraNode* Node) const override { return TEXT("CustomHlsl"); }
	virtual bool CanDecode(const FString& ClassName) const override { return ClassName == TEXT("CustomHlsl"); }

	virtual UNiagaraNode* CreateNode(UNiagaraGraph* Graph, const FNodeCodeNodeIR& IR) const override
	{
		UNiagaraNodeCustomHlsl* Node = NewObject<UNiagaraNodeCustomHlsl>(Graph, NAME_None, RF_Transactional);
		Graph->AddNode(Node, false, false);
		Node->CreateNewGuid();
		Node->PostPlacedNewNode();
		Node->AllocateDefaultPins();
		return Node;
	}
};

// ---- ParameterMapGet Encoder (private class, use runtime check) ----

class FParameterMapGetEncoder : public INiagaraNodeEncoder
{
public:
	virtual bool CanEncode(UNiagaraNode* Node) const override { return IsParameterMapGetNode(Node); }
	virtual FString Encode(UNiagaraNode* Node) const override { return TEXT("ParameterMapGet"); }
	virtual bool CanDecode(const FString& ClassName) const override { return ClassName == TEXT("ParameterMapGet"); }

	virtual UNiagaraNode* CreateNode(UNiagaraGraph* Graph, const FNodeCodeNodeIR& IR) const override
	{
		return CreateNodeByClassName(Graph, TEXT("/Script/NiagaraEditor.NiagaraNodeParameterMapGet"));
	}
};

// ---- ParameterMapSet Encoder (private class, use runtime check) ----

class FParameterMapSetEncoder : public INiagaraNodeEncoder
{
public:
	virtual bool CanEncode(UNiagaraNode* Node) const override { return IsParameterMapSetNode(Node); }
	virtual FString Encode(UNiagaraNode* Node) const override { return TEXT("ParameterMapSet"); }
	virtual bool CanDecode(const FString& ClassName) const override { return ClassName == TEXT("ParameterMapSet"); }

	virtual UNiagaraNode* CreateNode(UNiagaraGraph* Graph, const FNodeCodeNodeIR& IR) const override
	{
		return CreateNodeByClassName(Graph, TEXT("/Script/NiagaraEditor.NiagaraNodeParameterMapSet"));
	}
};

// ---- Op Encoder ----

class FOpEncoder : public INiagaraNodeEncoder
{
public:
	virtual bool CanEncode(UNiagaraNode* Node) const override { return Node->IsA<UNiagaraNodeOp>(); }
	virtual FString Encode(UNiagaraNode* Node) const override { return TEXT("NiagaraOp"); }
	virtual bool CanDecode(const FString& ClassName) const override { return ClassName == TEXT("NiagaraOp"); }

	virtual UNiagaraNode* CreateNode(UNiagaraGraph* Graph, const FNodeCodeNodeIR& IR) const override
	{
		UNiagaraNodeOp* Node = NewObject<UNiagaraNodeOp>(Graph, NAME_None, RF_Transactional);
		const FString* OpNamePtr = IR.Properties.Find(TEXT("OpName"));
		if (OpNamePtr) Node->OpName = FName(**OpNamePtr);
		Graph->AddNode(Node, false, false);
		Node->CreateNewGuid();
		Node->PostPlacedNewNode();
		Node->AllocateDefaultPins();
		return Node;
	}
};

// ---- NiagaraNodeInput Encoder ----

class FNodeInputEncoder : public INiagaraNodeEncoder
{
public:
	virtual bool CanEncode(UNiagaraNode* Node) const override { return Node->IsA<UNiagaraNodeInput>(); }
	virtual FString Encode(UNiagaraNode* Node) const override { return TEXT("NiagaraNodeInput"); }
	virtual bool CanDecode(const FString& ClassName) const override { return ClassName == TEXT("NiagaraNodeInput"); }

	virtual UNiagaraNode* CreateNode(UNiagaraGraph* Graph, const FNodeCodeNodeIR& IR) const override
	{
		UNiagaraNodeInput* Node = NewObject<UNiagaraNodeInput>(Graph, NAME_None, RF_Transactional);
		Graph->AddNode(Node, false, false);
		Node->CreateNewGuid();
		Node->PostPlacedNewNode();
		Node->AllocateDefaultPins();
		return Node;
	}
};

// ---- NiagaraNodeOutput Encoder ----

class FNodeOutputEncoder : public INiagaraNodeEncoder
{
public:
	virtual bool CanEncode(UNiagaraNode* Node) const override { return Node->IsA<UNiagaraNodeOutput>(); }
	virtual FString Encode(UNiagaraNode* Node) const override { return TEXT("NiagaraNodeOutput"); }
	virtual bool CanDecode(const FString& ClassName) const override { return ClassName == TEXT("NiagaraNodeOutput"); }
	virtual UNiagaraNode* CreateNode(UNiagaraGraph* Graph, const FNodeCodeNodeIR& IR) const override
	{
		return nullptr;
	}
};

// ---- Auto Registration ----

struct FNiagaraNodeEncoderAutoRegister
{
	FNiagaraNodeEncoderAutoRegister()
	{
		auto& Registry = FNiagaraNodeEncoderRegistry::Get();
		Registry.Register(MakeShared<FFunctionCallEncoder>());
		Registry.Register(MakeShared<FAssignmentEncoder>());
		Registry.Register(MakeShared<FCustomHlslEncoder>());
		Registry.Register(MakeShared<FParameterMapGetEncoder>());
		Registry.Register(MakeShared<FParameterMapSetEncoder>());
		Registry.Register(MakeShared<FOpEncoder>());
		Registry.Register(MakeShared<FNodeInputEncoder>());
		Registry.Register(MakeShared<FNodeOutputEncoder>());
	}
};

static FNiagaraNodeEncoderAutoRegister GAutoRegisterNiagaraNodeEncoders;
