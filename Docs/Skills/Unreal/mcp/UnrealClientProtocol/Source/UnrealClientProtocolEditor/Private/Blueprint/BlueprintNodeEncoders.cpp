// MIT License - Copyright (c) 2025 Italink

#include "Blueprint/IBlueprintNodeEncoder.h"
#include "NodeCode/NodeCodeTypes.h"
#include "NodeCode/NodeCodeClassCache.h"

#include "EdGraph/EdGraph.h"
#include "EdGraph/EdGraphNode.h"
#include "K2Node_CallFunction.h"
#include "K2Node_VariableGet.h"
#include "K2Node_VariableSet.h"
#include "K2Node_Event.h"
#include "K2Node_CustomEvent.h"
#include "K2Node_FunctionEntry.h"
#include "K2Node_FunctionResult.h"
#include "Engine/Blueprint.h"
#include "Kismet2/BlueprintEditorUtils.h"

static FName DecodeFName(const FString& Encoded)
{
	return FName(*Encoded.Replace(TEXT("_"), TEXT(" ")));
}

static UFunction* FindFunctionFuzzy(UClass* Class, const FString& EncodedName)
{
	if (!Class) return nullptr;
	UFunction* Func = Class->FindFunctionByName(FName(*EncodedName));
	if (Func) return Func;
	return Class->FindFunctionByName(DecodeFName(EncodedName));
}

// ---- Registry ----

FBlueprintNodeEncoderRegistry& FBlueprintNodeEncoderRegistry::Get()
{
	static FBlueprintNodeEncoderRegistry Instance;
	return Instance;
}

void FBlueprintNodeEncoderRegistry::Register(TSharedPtr<IBlueprintNodeEncoder> Encoder)
{
	if (Encoder.IsValid())
	{
		Encoders.Add(Encoder);
	}
}

FString FBlueprintNodeEncoderRegistry::EncodeNode(UEdGraphNode* Node) const
{
	for (const auto& Encoder : Encoders)
	{
		if (Encoder->CanEncode(Node))
		{
			return Encoder->Encode(Node);
		}
	}
	return FNodeCodeClassCache::Get().GetSerializableName(Node->GetClass());
}

UEdGraphNode* FBlueprintNodeEncoderRegistry::DecodeNode(const FString& ClassName, UEdGraph* Graph, UBlueprint* BP, const FNodeCodeNodeIR& IR) const
{
	for (const auto& Encoder : Encoders)
	{
		if (Encoder->CanDecode(ClassName))
		{
			return Encoder->CreateNode(Graph, BP, IR);
		}
	}

	UClass* NodeClass = FNodeCodeClassCache::Get().FindClass(ClassName);
	if (!NodeClass)
	{
		NodeClass = FNodeCodeClassCache::Get().FindClass(FString::Printf(TEXT("K2Node_%s"), *ClassName));
	}
	if (NodeClass && NodeClass->IsChildOf(UEdGraphNode::StaticClass()))
	{
		UEdGraphNode* Node = NewObject<UEdGraphNode>(Graph, NodeClass, NAME_None, RF_Transactional);
		Graph->AddNode(Node, false, false);
		Node->CreateNewGuid();
		Node->PostPlacedNewNode();
		Node->AllocateDefaultPins();
		return Node;
	}

	return nullptr;
}

// ---- CallFunction Encoder ----

class FCallFunctionEncoder : public IBlueprintNodeEncoder
{
public:
	virtual bool CanEncode(UEdGraphNode* Node) const override
	{
		return Node->GetClass() == UK2Node_CallFunction::StaticClass();
	}

	virtual FString Encode(UEdGraphNode* Node) const override
	{
		UK2Node_CallFunction* CallFunc = CastChecked<UK2Node_CallFunction>(Node);
		FName FuncName = CallFunc->FunctionReference.GetMemberName();
		UClass* FuncClass = CallFunc->FunctionReference.GetMemberParentClass();
		FString EncodedFuncName = NodeCodeUtils::EncodeSpaces(FuncName.ToString());
		if (FuncClass && !CallFunc->FunctionReference.IsSelfContext())
		{
			return FString::Printf(TEXT("CallFunction:%s.%s"), *FuncClass->GetName(), *EncodedFuncName);
		}
		return FString::Printf(TEXT("CallFunction:%s"), *EncodedFuncName);
	}

	virtual bool CanDecode(const FString& ClassName) const override
	{
		return ClassName.StartsWith(TEXT("CallFunction:"));
	}

	virtual UEdGraphNode* CreateNode(UEdGraph* Graph, UBlueprint* BP, const FNodeCodeNodeIR& IR) const override
	{
		FString FuncSpec = IR.ClassName.Mid(13);
		FString OwnerClassHint, FuncNameEncoded;
		bool bHasOwner = FuncSpec.Split(TEXT("."), &OwnerClassHint, &FuncNameEncoded);
		if (!bHasOwner) FuncNameEncoded = FuncSpec;

		UClass* OwnerClass = nullptr;
		if (const FString* TargetPath = IR.Properties.Find(TEXT("Target")))
		{
			OwnerClass = UClass::TryFindTypeSlow<UClass>(*TargetPath);
		}
		if (!OwnerClass && bHasOwner)
		{
			OwnerClass = UClass::TryFindTypeSlow<UClass>(OwnerClassHint);
		}

		FString FuncNameStr = FuncNameEncoded;
		if (const FString* FuncProp = IR.Properties.Find(TEXT("Function")))
		{
			FuncNameStr = *FuncProp;
		}

		if (OwnerClass || !bHasOwner)
		{
			UClass* SearchClass = OwnerClass ? OwnerClass : BP->GeneratedClass.Get();
			UFunction* Func = FindFunctionFuzzy(SearchClass, FuncNameStr);
			if (Func)
			{
				FGraphNodeCreator<UK2Node_CallFunction> Creator(*Graph);
				UK2Node_CallFunction* Node = Creator.CreateNode();
				Node->SetFromFunction(Func);
				Creator.Finalize();
				return Node;
			}
		}

		FGraphNodeCreator<UK2Node_CallFunction> Creator(*Graph);
		UK2Node_CallFunction* Node = Creator.CreateNode();
		FName ResolvedName = DecodeFName(FuncNameStr);
		if (OwnerClass)
		{
			Node->FunctionReference.SetExternalMember(ResolvedName, OwnerClass);
		}
		else
		{
			Node->FunctionReference.SetSelfMember(ResolvedName);
		}
		Node->AllocateDefaultPins();
		Creator.Finalize();
		return Node;
	}
};

// ---- VariableGet Encoder ----

class FVariableGetEncoder : public IBlueprintNodeEncoder
{
public:
	virtual bool CanEncode(UEdGraphNode* Node) const override
	{
		return Node->GetClass() == UK2Node_VariableGet::StaticClass();
	}

	virtual FString Encode(UEdGraphNode* Node) const override
	{
		UK2Node_VariableGet* VarGet = CastChecked<UK2Node_VariableGet>(Node);
		return FString::Printf(TEXT("VariableGet:%s"), *NodeCodeUtils::EncodeSpaces(VarGet->VariableReference.GetMemberName().ToString()));
	}

	virtual bool CanDecode(const FString& ClassName) const override
	{
		return ClassName.StartsWith(TEXT("VariableGet:"));
	}

	virtual UEdGraphNode* CreateNode(UEdGraph* Graph, UBlueprint* BP, const FNodeCodeNodeIR& IR) const override
	{
		FString VarName = IR.ClassName.Mid(12);
		if (const FString* VarProp = IR.Properties.Find(TEXT("Variable")))
		{
			VarName = *VarProp;
		}
		FName ResolvedName = DecodeFName(VarName);
		FGraphNodeCreator<UK2Node_VariableGet> Creator(*Graph);
		UK2Node_VariableGet* Node = Creator.CreateNode();
		if (const FString* TargetPath = IR.Properties.Find(TEXT("Target")))
		{
			UClass* TargetClass = UClass::TryFindTypeSlow<UClass>(*TargetPath);
			if (TargetClass)
				Node->VariableReference.SetExternalMember(ResolvedName, TargetClass);
			else
				Node->VariableReference.SetSelfMember(ResolvedName);
		}
		else
		{
			Node->VariableReference.SetSelfMember(ResolvedName);
		}
		Node->AllocateDefaultPins();
		Creator.Finalize();
		return Node;
	}
};

// ---- VariableSet Encoder ----

class FVariableSetEncoder : public IBlueprintNodeEncoder
{
public:
	virtual bool CanEncode(UEdGraphNode* Node) const override
	{
		return Node->GetClass() == UK2Node_VariableSet::StaticClass();
	}

	virtual FString Encode(UEdGraphNode* Node) const override
	{
		UK2Node_VariableSet* VarSet = CastChecked<UK2Node_VariableSet>(Node);
		return FString::Printf(TEXT("VariableSet:%s"), *NodeCodeUtils::EncodeSpaces(VarSet->VariableReference.GetMemberName().ToString()));
	}

	virtual bool CanDecode(const FString& ClassName) const override
	{
		return ClassName.StartsWith(TEXT("VariableSet:"));
	}

	virtual UEdGraphNode* CreateNode(UEdGraph* Graph, UBlueprint* BP, const FNodeCodeNodeIR& IR) const override
	{
		FString VarName = IR.ClassName.Mid(12);
		if (const FString* VarProp = IR.Properties.Find(TEXT("Variable")))
		{
			VarName = *VarProp;
		}
		FName ResolvedName = DecodeFName(VarName);
		FGraphNodeCreator<UK2Node_VariableSet> Creator(*Graph);
		UK2Node_VariableSet* Node = Creator.CreateNode();
		if (const FString* TargetPath = IR.Properties.Find(TEXT("Target")))
		{
			UClass* TargetClass = UClass::TryFindTypeSlow<UClass>(*TargetPath);
			if (TargetClass)
				Node->VariableReference.SetExternalMember(ResolvedName, TargetClass);
			else
				Node->VariableReference.SetSelfMember(ResolvedName);
		}
		else
		{
			Node->VariableReference.SetSelfMember(ResolvedName);
		}
		Node->AllocateDefaultPins();
		Creator.Finalize();
		return Node;
	}
};

// ---- CustomEvent Encoder ----

class FCustomEventEncoder : public IBlueprintNodeEncoder
{
public:
	virtual bool CanEncode(UEdGraphNode* Node) const override
	{
		return Node->GetClass() == UK2Node_CustomEvent::StaticClass();
	}

	virtual FString Encode(UEdGraphNode* Node) const override
	{
		UK2Node_CustomEvent* CustomEvent = CastChecked<UK2Node_CustomEvent>(Node);
		return FString::Printf(TEXT("CustomEvent:%s"), *NodeCodeUtils::EncodeSpaces(CustomEvent->CustomFunctionName.ToString()));
	}

	virtual bool CanDecode(const FString& ClassName) const override
	{
		return ClassName.StartsWith(TEXT("CustomEvent:"));
	}

	virtual UEdGraphNode* CreateNode(UEdGraph* Graph, UBlueprint* BP, const FNodeCodeNodeIR& IR) const override
	{
		FString EventName = IR.ClassName.Mid(12);
		if (const FString* EvProp = IR.Properties.Find(TEXT("EventName")))
		{
			EventName = *EvProp;
		}
		FGraphNodeCreator<UK2Node_CustomEvent> Creator(*Graph);
		UK2Node_CustomEvent* Node = Creator.CreateNode();
		Node->CustomFunctionName = DecodeFName(EventName);
		Node->AllocateDefaultPins();
		Creator.Finalize();
		return Node;
	}
};

// ---- Event Encoder ----

class FEventEncoder : public IBlueprintNodeEncoder
{
public:
	virtual bool CanEncode(UEdGraphNode* Node) const override
	{
		return Node->GetClass() == UK2Node_Event::StaticClass();
	}

	virtual FString Encode(UEdGraphNode* Node) const override
	{
		UK2Node_Event* Event = CastChecked<UK2Node_Event>(Node);
		FName EventName = Event->EventReference.GetMemberName();
		if (!EventName.IsNone())
		{
			return FString::Printf(TEXT("Event:%s"), *NodeCodeUtils::EncodeSpaces(EventName.ToString()));
		}
		if (!Event->CustomFunctionName.IsNone())
		{
			return FString::Printf(TEXT("Event:%s"), *NodeCodeUtils::EncodeSpaces(Event->CustomFunctionName.ToString()));
		}
		return Node->GetClass()->GetName();
	}

	virtual bool CanDecode(const FString& ClassName) const override
	{
		return ClassName.StartsWith(TEXT("Event:"));
	}

	virtual UEdGraphNode* CreateNode(UEdGraph* Graph, UBlueprint* BP, const FNodeCodeNodeIR& IR) const override
	{
		FString EventName = IR.ClassName.Mid(6);
		if (const FString* EvProp = IR.Properties.Find(TEXT("EventName")))
		{
			EventName = *EvProp;
		}

		UClass* EventClass = BP->GeneratedClass;
		if (const FString* TargetPath = IR.Properties.Find(TEXT("Target")))
		{
			UClass* TargetClass = UClass::TryFindTypeSlow<UClass>(*TargetPath);
			if (TargetClass) EventClass = TargetClass;
		}

		if (EventClass)
		{
			UFunction* EventFunc = FindFunctionFuzzy(EventClass, EventName);
			if (EventFunc)
			{
				FGraphNodeCreator<UK2Node_Event> Creator(*Graph);
				UK2Node_Event* Node = Creator.CreateNode();
				Node->EventReference.SetFromField<UFunction>(EventFunc, false);
				Node->bOverrideFunction = true;
				Node->AllocateDefaultPins();
				Creator.Finalize();
				return Node;
			}
		}

		FGraphNodeCreator<UK2Node_Event> Creator(*Graph);
		UK2Node_Event* Node = Creator.CreateNode();
		Node->EventReference.SetSelfMember(DecodeFName(EventName));
		Node->AllocateDefaultPins();
		Creator.Finalize();
		return Node;
	}
};

// ---- FunctionEntry/Result Encoder ----

class FFunctionEntryEncoder : public IBlueprintNodeEncoder
{
public:
	virtual bool CanEncode(UEdGraphNode* Node) const override
	{
		return Cast<UK2Node_FunctionEntry>(Node) != nullptr;
	}
	virtual FString Encode(UEdGraphNode* Node) const override { return TEXT("FunctionEntry"); }
	virtual bool CanDecode(const FString& ClassName) const override { return ClassName == TEXT("FunctionEntry"); }
	virtual UEdGraphNode* CreateNode(UEdGraph* Graph, UBlueprint* BP, const FNodeCodeNodeIR& IR) const override { return nullptr; }
};

class FFunctionResultEncoder : public IBlueprintNodeEncoder
{
public:
	virtual bool CanEncode(UEdGraphNode* Node) const override
	{
		return Cast<UK2Node_FunctionResult>(Node) != nullptr;
	}
	virtual FString Encode(UEdGraphNode* Node) const override { return TEXT("FunctionResult"); }
	virtual bool CanDecode(const FString& ClassName) const override { return ClassName == TEXT("FunctionResult"); }
	virtual UEdGraphNode* CreateNode(UEdGraph* Graph, UBlueprint* BP, const FNodeCodeNodeIR& IR) const override { return nullptr; }
};

// ---- Auto-registration ----

struct FBlueprintNodeEncoderAutoRegister
{
	FBlueprintNodeEncoderAutoRegister()
	{
		auto& Registry = FBlueprintNodeEncoderRegistry::Get();
		Registry.Register(MakeShared<FCallFunctionEncoder>());
		Registry.Register(MakeShared<FVariableGetEncoder>());
		Registry.Register(MakeShared<FVariableSetEncoder>());
		Registry.Register(MakeShared<FCustomEventEncoder>());
		Registry.Register(MakeShared<FEventEncoder>());
		Registry.Register(MakeShared<FFunctionEntryEncoder>());
		Registry.Register(MakeShared<FFunctionResultEncoder>());
	}
};

static FBlueprintNodeEncoderAutoRegister GAutoRegisterBlueprintNodeEncoders;
