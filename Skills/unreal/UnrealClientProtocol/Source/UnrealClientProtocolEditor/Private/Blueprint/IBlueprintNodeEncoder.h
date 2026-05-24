// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "NodeCode/NodeCodeTypes.h"

class UEdGraphNode;
class UEdGraph;
class UBlueprint;

class IBlueprintNodeEncoder
{
public:
	virtual ~IBlueprintNodeEncoder() = default;
	virtual bool CanEncode(UEdGraphNode* Node) const = 0;
	virtual FString Encode(UEdGraphNode* Node) const = 0;
	virtual bool CanDecode(const FString& ClassName) const = 0;
	virtual UEdGraphNode* CreateNode(UEdGraph* Graph, UBlueprint* BP, const FNodeCodeNodeIR& IR) const = 0;
};

class FBlueprintNodeEncoderRegistry
{
public:
	static FBlueprintNodeEncoderRegistry& Get();

	void Register(TSharedPtr<IBlueprintNodeEncoder> Encoder);

	FString EncodeNode(UEdGraphNode* Node) const;

	UEdGraphNode* DecodeNode(const FString& ClassName, UEdGraph* Graph, UBlueprint* BP, const FNodeCodeNodeIR& IR) const;

private:
	TArray<TSharedPtr<IBlueprintNodeEncoder>> Encoders;
};
