// MIT License - Copyright (c) 2025 Italink

#include "Widget/WidgetTreeSerializer.h"
#include "NodeCode/NodeCodeClassCache.h"
#include "NodeCode/NodeCodePropertyUtils.h"
#include "NodeCode/NodeCodeTypes.h"

#include "WidgetBlueprint.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Widget.h"
#include "Components/PanelWidget.h"
#include "Components/PanelSlot.h"
#include "UObject/UnrealType.h"
#include "UObject/LazyObjectPtr.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonWriter.h"
#include "Serialization/JsonSerializer.h"
#include "ScopedTransaction.h"
#include "Kismet2/BlueprintEditorUtils.h"

DEFINE_LOG_CATEGORY_STATIC(LogUCPWidget, Log, All);

// ---- Serialize ----

FString FWidgetTreeSerializer::Serialize(UWidgetBlueprint* WidgetBP)
{
	if (!WidgetBP || !WidgetBP->WidgetTree)
	{
		return FString();
	}

	UWidget* RootWidget = WidgetBP->WidgetTree->RootWidget;
	if (!RootWidget)
	{
		return FString();
	}

	FString OutText;
	SerializeWidget(RootWidget, 0, OutText);
	return OutText;
}

void FWidgetTreeSerializer::SerializeWidget(UWidget* Widget, int32 Depth, FString& OutText)
{
	if (!Widget)
	{
		return;
	}

	FString Indent;
	for (int32 i = 0; i < Depth; ++i)
	{
		Indent += TEXT("  ");
	}

	FString ClassName = FNodeCodeClassCache::Get().GetSerializableName(Widget->GetClass());

	FUniqueObjectGuid UniqueGuid = FUniqueObjectGuid::GetOrCreateIDForObject(Widget);

	TSharedPtr<FJsonObject> JsonObj = MakeShared<FJsonObject>();
	JsonObj->SetStringField(TEXT("Type"), ClassName);

	if (UniqueGuid.IsValid())
	{
		JsonObj->SetStringField(TEXT("Id"), NodeCodeUtils::GuidToBase62(UniqueGuid.GetGuid()));
	}

	if (Widget->bIsVariable)
	{
		JsonObj->SetBoolField(TEXT("bIsVariable"), true);
	}

	TMap<FString, FString> SlotProps;
	SerializeSlotProperties(Widget, SlotProps);
	if (SlotProps.Num() > 0)
	{
		TSharedPtr<FJsonObject> SlotObj = MakeShared<FJsonObject>();
		for (const auto& Pair : SlotProps)
		{
			SlotObj->SetStringField(Pair.Key, Pair.Value);
		}
		JsonObj->SetObjectField(TEXT("Slot"), SlotObj);
	}

	TMap<FString, FString> WidgetProps;
	SerializeWidgetProperties(Widget, WidgetProps);
	for (const auto& Pair : WidgetProps)
	{
		JsonObj->SetStringField(Pair.Key, Pair.Value);
	}

	FString JsonStr;
	TSharedRef<TJsonWriter<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>> Writer =
		TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&JsonStr);
	FJsonSerializer::Serialize(JsonObj.ToSharedRef(), Writer);

	OutText += FString::Printf(TEXT("%s%s: %s\n"), *Indent, *Widget->GetName(), *JsonStr);

	UPanelWidget* PanelWidget = Cast<UPanelWidget>(Widget);
	if (PanelWidget)
	{
		for (int32 i = 0; i < PanelWidget->GetChildrenCount(); ++i)
		{
			UWidget* Child = PanelWidget->GetChildAt(i);
			if (Child)
			{
				SerializeWidget(Child, Depth + 1, OutText);
			}
		}
	}
}

void FWidgetTreeSerializer::SerializeWidgetProperties(UWidget* Widget, TMap<FString, FString>& OutProperties)
{
	UClass* WidgetClass = Widget->GetClass();
	UObject* CDO = WidgetClass->GetDefaultObject();
	const TSet<FName>& SkipSet = FNodeCodePropertyUtils::GetWidgetSkipSet();

	for (TFieldIterator<FProperty> PropIt(WidgetClass); PropIt; ++PropIt)
	{
		FProperty* Prop = *PropIt;

		if (FNodeCodePropertyUtils::ShouldSkipProperty(Prop))
		{
			continue;
		}

		if (SkipSet.Contains(Prop->GetFName()))
		{
			continue;
		}

		const void* InstanceValue = Prop->ContainerPtrToValuePtr<void>(Widget);
		const void* CDOValue = Prop->ContainerPtrToValuePtr<void>(CDO);

		if (Prop->Identical(InstanceValue, CDOValue, PPF_None))
		{
			continue;
		}

		FString ValueStr = FNodeCodePropertyUtils::FormatPropertyValue(Prop, InstanceValue, Widget);
		OutProperties.Add(Prop->GetName(), MoveTemp(ValueStr));
	}
}

void FWidgetTreeSerializer::SerializeSlotProperties(UWidget* Widget, TMap<FString, FString>& OutProperties)
{
	UPanelSlot* Slot = Widget->Slot;
	if (!Slot)
	{
		return;
	}

	UClass* SlotClass = Slot->GetClass();
	UObject* CDO = SlotClass->GetDefaultObject();

	static const TSet<FName> SlotSkipSet = {
		TEXT("Parent"),
		TEXT("Content"),
	};

	for (TFieldIterator<FProperty> PropIt(SlotClass); PropIt; ++PropIt)
	{
		FProperty* Prop = *PropIt;

		if (FNodeCodePropertyUtils::ShouldSkipProperty(Prop))
		{
			continue;
		}

		if (SlotSkipSet.Contains(Prop->GetFName()))
		{
			continue;
		}

		const void* InstanceValue = Prop->ContainerPtrToValuePtr<void>(Slot);
		const void* CDOValue = Prop->ContainerPtrToValuePtr<void>(CDO);

		if (Prop->Identical(InstanceValue, CDOValue, PPF_None))
		{
			continue;
		}

		FString ValueStr = FNodeCodePropertyUtils::FormatPropertyValue(Prop, InstanceValue, Slot);
		OutProperties.Add(Prop->GetName(), MoveTemp(ValueStr));
	}
}

// ---- Parse ----

TArray<FWidgetTreeSerializer::FWidgetEntry> FWidgetTreeSerializer::ParseTreeText(const FString& TreeText)
{
	TArray<FWidgetEntry> Entries;

	TArray<FString> Lines;
	TreeText.ParseIntoArrayLines(Lines);

	for (const FString& Line : Lines)
	{
		if (Line.TrimStartAndEnd().IsEmpty())
		{
			continue;
		}

		int32 Depth = 0;
		int32 Idx = 0;
		while (Idx + 1 < Line.Len() && Line[Idx] == ' ' && Line[Idx + 1] == ' ')
		{
			Depth++;
			Idx += 2;
		}

		FString TrimmedLine = Line.Mid(Idx);
		Entries.Add(ParseEntryLine(TrimmedLine, Depth));
	}

	return Entries;
}

FWidgetTreeSerializer::FWidgetEntry FWidgetTreeSerializer::ParseEntryLine(const FString& Line, int32 Depth)
{
	FWidgetEntry Entry;
	Entry.Depth = Depth;

	int32 ColonPos;
	if (!Line.FindChar(':', ColonPos))
	{
		Entry.Name = Line.TrimStartAndEnd();
		return Entry;
	}

	Entry.Name = Line.Left(ColonPos).TrimStartAndEnd();
	FString JsonStr = Line.Mid(ColonPos + 1).TrimStartAndEnd();

	TSharedPtr<FJsonObject> JsonObj;
	TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonStr);
	if (!FJsonSerializer::Deserialize(Reader, JsonObj) || !JsonObj.IsValid())
	{
		UE_LOG(LogUCPWidget, Warning, TEXT("ParseEntryLine: Failed to parse JSON for widget: %s"), *Entry.Name);
		return Entry;
	}

	if (JsonObj->HasField(TEXT("Type")))
	{
		Entry.Type = JsonObj->GetStringField(TEXT("Type"));
	}

	if (JsonObj->HasField(TEXT("bIsVariable")))
	{
		Entry.bIsVariable = JsonObj->GetBoolField(TEXT("bIsVariable"));
	}

	if (JsonObj->HasField(TEXT("Slot")))
	{
		const TSharedPtr<FJsonObject>* SlotObj;
		if (JsonObj->TryGetObjectField(TEXT("Slot"), SlotObj))
		{
			for (const auto& Pair : (*SlotObj)->Values)
			{
				if (Pair.Value->Type == EJson::String)
				{
					Entry.SlotProperties.Add(Pair.Key, Pair.Value->AsString());
				}
				else
				{
					FString ValueStr;
					TSharedRef<TJsonWriter<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>> Writer =
						TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&ValueStr);
					FJsonSerializer::Serialize(Pair.Value, Pair.Key, Writer);
					Entry.SlotProperties.Add(Pair.Key, MoveTemp(ValueStr));
				}
			}
		}
	}

	for (const auto& Pair : JsonObj->Values)
	{
		if (Pair.Key == TEXT("Type") || Pair.Key == TEXT("bIsVariable") || Pair.Key == TEXT("Slot"))
		{
			continue;
		}

		if (Pair.Value->Type == EJson::String)
		{
			Entry.Properties.Add(Pair.Key, Pair.Value->AsString());
		}
		else
		{
			FString ValueStr;
			TSharedRef<TJsonWriter<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>> Writer =
				TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&ValueStr);
			FJsonSerializer::Serialize(Pair.Value, Pair.Key, Writer);
			Entry.Properties.Add(Pair.Key, MoveTemp(ValueStr));
		}
	}

	return Entry;
}

// ---- Apply ----

FNodeCodeDiffResult FWidgetTreeSerializer::Apply(UWidgetBlueprint* WidgetBP, const FString& TreeText)
{
	FNodeCodeDiffResult Result;
	if (!WidgetBP || !WidgetBP->WidgetTree)
	{
		return Result;
	}

	FScopedTransaction Transaction(NSLOCTEXT("UCPWidget", "WriteWidgetTree", "UCP: Write Widget Tree"));
	WidgetBP->Modify();

	TArray<FWidgetEntry> Entries = ParseTreeText(TreeText);
	if (Entries.Num() == 0)
	{
		return Result;
	}

	UWidgetTree* Tree = WidgetBP->WidgetTree;

	TMap<FString, UWidget*> ExistingWidgets;
	Tree->ForEachWidget([&ExistingWidgets](UWidget* Widget)
	{
		if (Widget)
		{
			ExistingWidgets.Add(Widget->GetName(), Widget);
		}
	});

	TSet<FString> DesiredWidgetNames;
	for (const FWidgetEntry& Entry : Entries)
	{
		DesiredWidgetNames.Add(Entry.Name);
	}

	TMap<FString, UWidget*> WidgetMap;
	TArray<int32> ParentStack;

	for (int32 EntryIdx = 0; EntryIdx < Entries.Num(); ++EntryIdx)
	{
		const FWidgetEntry& Entry = Entries[EntryIdx];

		UWidget** ExistingPtr = ExistingWidgets.Find(Entry.Name);
		UWidget* Widget = ExistingPtr ? *ExistingPtr : nullptr;

		if (!Widget)
		{
			UClass* WidgetClass = FNodeCodeClassCache::Get().FindClass(Entry.Type);
			if (!WidgetClass || !WidgetClass->IsChildOf(UWidget::StaticClass()))
			{
				UE_LOG(LogUCPWidget, Error, TEXT("Apply: Unknown widget class: %s"), *Entry.Type);
				continue;
			}

			Widget = Tree->ConstructWidget<UWidget>(WidgetClass, FName(*Entry.Name));
			if (!Widget)
			{
				UE_LOG(LogUCPWidget, Error, TEXT("Apply: Failed to create widget: %s (%s)"), *Entry.Name, *Entry.Type);
				continue;
			}

			Result.NodesAdded.Add(FString::Printf(TEXT("%s (%s)"), *Entry.Name, *Entry.Type));
		}

		Widget->bIsVariable = Entry.bIsVariable;

		ApplyWidgetProperties(Widget, Entry.Properties);

		if (Entry.Depth == 0)
		{
			if (Tree->RootWidget != Widget)
			{
				Tree->RootWidget = Widget;
			}
			ParentStack.Empty();
			ParentStack.Add(EntryIdx);
		}
		else
		{
			while (ParentStack.Num() > 0 && Entries[ParentStack.Last()].Depth >= Entry.Depth)
			{
				ParentStack.Pop();
			}

			if (ParentStack.Num() > 0)
			{
				FString ParentName = Entries[ParentStack.Last()].Name;
				UWidget** ParentPtr = WidgetMap.Find(ParentName);
				if (ParentPtr)
				{
					UPanelWidget* ParentPanel = Cast<UPanelWidget>(*ParentPtr);
					if (ParentPanel)
					{
						UPanelWidget* CurrentParent = Widget->Slot ? Cast<UPanelWidget>(Widget->Slot->Parent) : nullptr;
						if (CurrentParent != ParentPanel)
						{
							if (CurrentParent)
							{
								CurrentParent->RemoveChild(Widget);
							}
							ParentPanel->AddChild(Widget);
						}
					}
				}
			}

			ParentStack.Add(EntryIdx);
		}

		WidgetMap.Add(Entry.Name, Widget);
	}

	for (const auto& Pair : ExistingWidgets)
	{
		if (!DesiredWidgetNames.Contains(Pair.Key))
		{
			Tree->RemoveWidget(Pair.Value);
			Result.NodesRemoved.Add(FString::Printf(TEXT("%s"), *Pair.Key));
		}
	}

	// Reorder children to match desired order from text
	TMap<UPanelWidget*, TArray<UWidget*>> DesiredChildOrder;
	{
		TArray<int32> ReorderParentStack;
		for (int32 EntryIdx = 0; EntryIdx < Entries.Num(); ++EntryIdx)
		{
			const FWidgetEntry& Entry = Entries[EntryIdx];
			UWidget** WidgetPtr = WidgetMap.Find(Entry.Name);
			if (!WidgetPtr) continue;

			if (Entry.Depth == 0)
			{
				ReorderParentStack.Empty();
				ReorderParentStack.Add(EntryIdx);
			}
			else
			{
				while (ReorderParentStack.Num() > 0 && Entries[ReorderParentStack.Last()].Depth >= Entry.Depth)
				{
					ReorderParentStack.Pop();
				}
				if (ReorderParentStack.Num() > 0)
				{
					UWidget** ParentWidgetPtr = WidgetMap.Find(Entries[ReorderParentStack.Last()].Name);
					if (ParentWidgetPtr)
					{
						UPanelWidget* Panel = Cast<UPanelWidget>(*ParentWidgetPtr);
						if (Panel)
						{
							DesiredChildOrder.FindOrAdd(Panel).Add(*WidgetPtr);
						}
					}
				}
				ReorderParentStack.Add(EntryIdx);
			}
		}
	}

	for (auto& Pair : DesiredChildOrder)
	{
		UPanelWidget* Panel = Pair.Key;
		const TArray<UWidget*>& DesiredOrder = Pair.Value;

		bool bNeedsReorder = false;
		if (Panel->GetChildrenCount() == DesiredOrder.Num())
		{
			for (int32 i = 0; i < DesiredOrder.Num(); ++i)
			{
				if (Panel->GetChildAt(i) != DesiredOrder[i])
				{
					bNeedsReorder = true;
					break;
				}
			}
		}

		if (bNeedsReorder)
		{
			Panel->ClearChildren();
			for (UWidget* Child : DesiredOrder)
			{
				Panel->AddChild(Child);
			}
		}
	}

	// Apply slot properties after all parenting and reordering is finalized
	for (const FWidgetEntry& Entry : Entries)
	{
		if (Entry.SlotProperties.Num() == 0) continue;
		UWidget** WidgetPtr = WidgetMap.Find(Entry.Name);
		if (WidgetPtr && *WidgetPtr && (*WidgetPtr)->Slot)
		{
			ApplySlotProperties(*WidgetPtr, Entry.SlotProperties);
		}
	}

	WidgetBP->PostEditChange();
	FBlueprintEditorUtils::MarkBlueprintAsModified(WidgetBP);

	return Result;
}

void FWidgetTreeSerializer::ApplyWidgetProperties(UWidget* Widget, const TMap<FString, FString>& Properties)
{
	UClass* WidgetClass = Widget->GetClass();

	for (const auto& Pair : Properties)
	{
		FProperty* Prop = WidgetClass->FindPropertyByName(FName(*Pair.Key));
		if (!Prop)
		{
			continue;
		}

		void* ValuePtr = Prop->ContainerPtrToValuePtr<void>(Widget);

		FString ImportValue = Pair.Value;
		if (ImportValue.StartsWith(TEXT("\"")) && ImportValue.EndsWith(TEXT("\"")))
		{
			ImportValue = ImportValue.Mid(1, ImportValue.Len() - 2);
			ImportValue = ImportValue.ReplaceEscapedCharWithChar();
		}

		Prop->ImportText_Direct(*ImportValue, ValuePtr, Widget, PPF_None);
	}
}

void FWidgetTreeSerializer::ApplySlotProperties(UWidget* Widget, const TMap<FString, FString>& SlotProperties)
{
	UPanelSlot* Slot = Widget->Slot;
	if (!Slot)
	{
		return;
	}

	UClass* SlotClass = Slot->GetClass();

	for (const auto& Pair : SlotProperties)
	{
		FProperty* Prop = SlotClass->FindPropertyByName(FName(*Pair.Key));
		if (!Prop)
		{
			continue;
		}

		void* ValuePtr = Prop->ContainerPtrToValuePtr<void>(Slot);

		FString ImportValue = Pair.Value;
		if (ImportValue.StartsWith(TEXT("\"")) && ImportValue.EndsWith(TEXT("\"")))
		{
			ImportValue = ImportValue.Mid(1, ImportValue.Len() - 2);
			ImportValue = ImportValue.ReplaceEscapedCharWithChar();
		}

		Prop->ImportText_Direct(*ImportValue, ValuePtr, Slot, PPF_None);
	}
}
