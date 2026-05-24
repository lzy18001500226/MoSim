// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "NodeCode/NodeCodeTypes.h"

class UNiagaraNode;
class UNiagaraGraph;

class INiagaraNodeEncoder
{
public:
	virtual ~INiagaraNodeEncoder() = default;
	virtual bool CanEncode(UNiagaraNode* Node) const = 0;
	virtual FString Encode(UNiagaraNode* Node) const = 0;
	virtual bool CanDecode(const FString& ClassName) const = 0;
	virtual UNiagaraNode* CreateNode(UNiagaraGraph* Graph, const FNodeCodeNodeIR& IR) const = 0;
};

class FNiagaraNodeEncoderRegistry
{
public:
	static FNiagaraNodeEncoderRegistry& Get();

	void Register(TSharedPtr<INiagaraNodeEncoder> Encoder);

	FString EncodeNode(UNiagaraNode* Node) const;

	UNiagaraNode* DecodeNode(const FString& ClassName, UNiagaraGraph* Graph, const FNodeCodeNodeIR& IR) const;

private:
	TArray<TSharedPtr<INiagaraNodeEncoder>> Encoders;
};
