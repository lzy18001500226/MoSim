// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"

class FNodeCodePropertyUtils
{
public:
	static FString FormatPropertyValue(FProperty* Prop, const void* ValuePtr, UObject* Owner);

	static bool ShouldSkipProperty(const FProperty* Prop);

	static const TSet<FName>& GetEdGraphNodeSkipSet();

	static const TSet<FName>& GetMaterialExpressionSkipSet();

	static const TSet<FName>& GetWidgetSkipSet();

	static const TSet<FName>& GetNiagaraNodeSkipSet();
};
