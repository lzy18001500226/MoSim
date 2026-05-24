// MIT License - Copyright (c) 2025 Italink

#include "Object/ObjectEditorOperationLibrary.h"
#include "UCPJsonUtils.h"
#include "Editor.h"
#include "Editor/Transactor.h"
#include "Misc/ITransaction.h"
#include "ObjectTools.h"

DEFINE_LOG_CATEGORY_STATIC(LogObjectEditorOp, Log, All);

using namespace UCPUtils;

FString UObjectEditorOperationLibrary::UndoTransaction(const FString& Keyword)
{
	if (!GEditor || !GEditor->Trans)
	{
		UE_LOG(LogObjectEditorOp, Error, TEXT("Undo: GEditor not available"));
		return FString();
	}

	if (!Keyword.IsEmpty())
	{
		if (!GEditor->Trans->CanUndo())
		{
			TSharedPtr<FJsonObject> Err = MakeShared<FJsonObject>();
			Err->SetStringField(TEXT("error"), TEXT("Nothing to undo"));
			Err->SetStringField(TEXT("keyword"), Keyword);
			return JsonToString(Err);
		}
		FTransactionContext Ctx = GEditor->Trans->GetUndoContext();
		FString Title = Ctx.Title.ToString();
		if (!Title.Contains(Keyword))
		{
			TSharedPtr<FJsonObject> Err = MakeShared<FJsonObject>();
			Err->SetStringField(TEXT("error"), TEXT("Top undo transaction does not match keyword"));
			Err->SetStringField(TEXT("keyword"), Keyword);
			Err->SetStringField(TEXT("topTransaction"), Title);
			return JsonToString(Err);
		}
	}

	if (!GEditor->UndoTransaction())
	{
		UE_LOG(LogObjectEditorOp, Warning, TEXT("Undo: Nothing to undo"));
	}

	return FString();
}

FString UObjectEditorOperationLibrary::RedoTransaction(const FString& Keyword)
{
	if (!GEditor || !GEditor->Trans)
	{
		UE_LOG(LogObjectEditorOp, Error, TEXT("Redo: GEditor not available"));
		return FString();
	}

	if (!Keyword.IsEmpty())
	{
		if (!GEditor->Trans->CanRedo())
		{
			TSharedPtr<FJsonObject> Err = MakeShared<FJsonObject>();
			Err->SetStringField(TEXT("error"), TEXT("Nothing to redo"));
			Err->SetStringField(TEXT("keyword"), Keyword);
			return JsonToString(Err);
		}
		FTransactionContext Ctx = GEditor->Trans->GetRedoContext();
		FString Title = Ctx.Title.ToString();
		if (!Title.Contains(Keyword))
		{
			TSharedPtr<FJsonObject> Err = MakeShared<FJsonObject>();
			Err->SetStringField(TEXT("error"), TEXT("Top redo transaction does not match keyword"));
			Err->SetStringField(TEXT("keyword"), Keyword);
			Err->SetStringField(TEXT("topTransaction"), Title);
			return JsonToString(Err);
		}
	}

	if (!GEditor->RedoTransaction())
	{
		UE_LOG(LogObjectEditorOp, Warning, TEXT("Redo: Nothing to redo"));
	}

	return FString();
}

FString UObjectEditorOperationLibrary::GetTransactionState()
{
	TSharedPtr<FJsonObject> Result = MakeShared<FJsonObject>();

	if (!GEditor || !GEditor->Trans)
	{
		UE_LOG(LogObjectEditorOp, Error, TEXT("GetTransactionState: GEditor or transaction system not available"));
		return FString();
	}

	bool bCanUndo = GEditor->Trans->CanUndo();
	bool bCanRedo = GEditor->Trans->CanRedo();
	Result->SetBoolField(TEXT("canUndo"), bCanUndo);
	Result->SetBoolField(TEXT("canRedo"), bCanRedo);

	if (bCanUndo)
	{
		FTransactionContext UndoCtx = GEditor->Trans->GetUndoContext();
		Result->SetStringField(TEXT("undoTitle"), UndoCtx.Title.ToString());
	}
	else
	{
		Result->SetStringField(TEXT("undoTitle"), TEXT(""));
	}

	if (bCanRedo)
	{
		FTransactionContext RedoCtx = GEditor->Trans->GetRedoContext();
		Result->SetStringField(TEXT("redoTitle"), RedoCtx.Title.ToString());
	}
	else
	{
		Result->SetStringField(TEXT("redoTitle"), TEXT(""));
	}

	Result->SetNumberField(TEXT("undoCount"), GEditor->Trans->GetUndoCount());
	Result->SetNumberField(TEXT("queueLength"), GEditor->Trans->GetQueueLength());

	return JsonToString(Result);
}

bool UObjectEditorOperationLibrary::ForceReplaceReferences(const FString& ReplacementObjectPath, const TArray<FString>& ObjectsToReplacePaths)
{
	UObject* Replacement = StaticLoadObject(UObject::StaticClass(), nullptr, *ReplacementObjectPath);
	if (!Replacement)
	{
		UE_LOG(LogObjectEditorOp, Error, TEXT("ForceReplaceReferences: Replacement object not found: %s"), *ReplacementObjectPath);
		return false;
	}

	TArray<UObject*> ObjectsToReplace;
	for (const FString& Path : ObjectsToReplacePaths)
	{
		UObject* Obj = StaticLoadObject(UObject::StaticClass(), nullptr, *Path);
		if (Obj)
		{
			ObjectsToReplace.Add(Obj);
		}
		else
		{
			UE_LOG(LogObjectEditorOp, Warning, TEXT("ForceReplaceReferences: Object not found: %s"), *Path);
		}
	}

	if (ObjectsToReplace.Num() == 0)
	{
		UE_LOG(LogObjectEditorOp, Warning, TEXT("ForceReplaceReferences: No valid objects to replace"));
		return false;
	}

	ObjectTools::ForceReplaceReferences(Replacement, ObjectsToReplace);
	return true;
}
