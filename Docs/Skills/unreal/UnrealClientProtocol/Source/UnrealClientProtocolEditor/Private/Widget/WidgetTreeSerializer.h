// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "NodeCode/NodeCodeTypes.h"

class UWidgetBlueprint;
class UWidget;
class UPanelWidget;

class FWidgetTreeSerializer
{
public:
	static FString Serialize(UWidgetBlueprint* WidgetBP);

	static FNodeCodeDiffResult Apply(UWidgetBlueprint* WidgetBP, const FString& TreeText);

private:
	struct FWidgetEntry
	{
		int32 Depth = 0;
		FString Name;
		FString Type;
		bool bIsVariable = false;
		TMap<FString, FString> Properties;
		TMap<FString, FString> SlotProperties;
	};

	static void SerializeWidget(UWidget* Widget, int32 Depth, FString& OutText);
	static void SerializeWidgetProperties(UWidget* Widget, TMap<FString, FString>& OutProperties);
	static void SerializeSlotProperties(UWidget* Widget, TMap<FString, FString>& OutProperties);

	static TArray<FWidgetEntry> ParseTreeText(const FString& TreeText);
	static FWidgetEntry ParseEntryLine(const FString& Line, int32 Depth);

	static void ApplyWidgetProperties(UWidget* Widget, const TMap<FString, FString>& Properties);
	static void ApplySlotProperties(UWidget* Widget, const TMap<FString, FString>& SlotProperties);
};
