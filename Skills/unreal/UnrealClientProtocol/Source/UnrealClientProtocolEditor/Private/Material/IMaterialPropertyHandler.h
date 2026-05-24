// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"

class UMaterialExpression;

class IMaterialPropertyHandler
{
public:
	virtual ~IMaterialPropertyHandler() = default;
	virtual bool CanHandle(UMaterialExpression* Expr) const = 0;
	virtual void Serialize(UMaterialExpression* Expr, TMap<FString, FString>& OutProps) const = 0;
	virtual void Apply(UMaterialExpression* Expr, const TMap<FString, FString>& Props, TArray<FString>& OutChanges) const = 0;
};

class FMaterialPropertyHandlerRegistry
{
public:
	static FMaterialPropertyHandlerRegistry& Get();

	void Register(TSharedPtr<IMaterialPropertyHandler> Handler);

	void SerializeSpecial(UMaterialExpression* Expr, TMap<FString, FString>& OutProps) const;
	void ApplySpecial(UMaterialExpression* Expr, const TMap<FString, FString>& Props, TArray<FString>& OutChanges) const;

	bool IsHandledKey(UMaterialExpression* Expr, const FString& Key) const;

private:
	TArray<TSharedPtr<IMaterialPropertyHandler>> Handlers;
};
