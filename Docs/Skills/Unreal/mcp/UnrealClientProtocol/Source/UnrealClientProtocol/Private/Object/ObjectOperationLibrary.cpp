// MIT License - Copyright (c) 2025 Italink

#include "Object/ObjectOperationLibrary.h"
#include "UCPFunctionInvoker.h"
#include "UCPParamConverter.h"
#include "UCPJsonUtils.h"
#include "UObject/UObjectGlobals.h"
#include "UObject/UObjectIterator.h"
#include "UObject/UObjectHash.h"
#include "UObject/UnrealType.h"
#include "UObject/Class.h"
#include "UObject/Package.h"
#include "Serialization/JsonReader.h"
#include "GameFramework/Actor.h"
#include "Components/ActorComponent.h"
#include "Components/SceneComponent.h"

DEFINE_LOG_CATEGORY_STATIC(LogObjectOp, Log, All);

using namespace UCPUtils;

FString UObjectOperationLibrary::GetObjectProperty(const FString& ObjectPath, const FString& PropertyName)
{
	if (ObjectPath.IsEmpty() || PropertyName.IsEmpty())
	{
		UE_LOG(LogObjectOp, Error, TEXT("GetObjectProperty: Missing ObjectPath or PropertyName"));
		return FString();
	}

	UObject* Obj = UCPUtils::LoadObject(ObjectPath);
	if (!Obj)
	{
		UE_LOG(LogObjectOp, Error, TEXT("GetObjectProperty: Object not found: %s"), *ObjectPath);
		return FString();
	}

	FProperty* Prop = FUCPParamConverter::FindPropertyByNameFlexible(Obj->GetClass(), PropertyName);
	if (!Prop)
	{
		UE_LOG(LogObjectOp, Error, TEXT("GetObjectProperty: Property not found: %s on %s"), *PropertyName, *Obj->GetClass()->GetPathName());
		return FString();
	}

	const void* ValuePtr = Prop->ContainerPtrToValuePtr<void>(Obj);
	TSharedPtr<FJsonValue> JsonVal = FUCPParamConverter::PropertyToJsonValue(Prop, ValuePtr);

	TSharedPtr<FJsonObject> Result = MakeShared<FJsonObject>();
	Result->SetField(PropertyName, JsonVal);
	return JsonToString(Result);
}

FString UObjectOperationLibrary::SetObjectProperty(const FString& ObjectPath, const FString& PropertyName, const FString& JsonValue)
{
	if (ObjectPath.IsEmpty() || PropertyName.IsEmpty())
	{
		UE_LOG(LogObjectOp, Error, TEXT("SetObjectProperty: Missing ObjectPath or PropertyName"));
		return FString();
	}

	UObject* Obj = UCPUtils::LoadObject(ObjectPath);
	if (!Obj)
	{
		UE_LOG(LogObjectOp, Error, TEXT("SetObjectProperty: Object not found: %s"), *ObjectPath);
		return FString();
	}

	FProperty* Prop = FUCPParamConverter::FindPropertyByNameFlexible(Obj->GetClass(), PropertyName);
	if (!Prop)
	{
		UE_LOG(LogObjectOp, Error, TEXT("SetObjectProperty: Property not found: %s on %s"), *PropertyName, *Obj->GetClass()->GetPathName());
		return FString();
	}

	FString WrappedJson = FString::Printf(TEXT("[%s]"), *JsonValue);
	TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(WrappedJson);
	TArray<TSharedPtr<FJsonValue>> ParsedArray;
	bool bJsonParsed = FJsonSerializer::Deserialize(Reader, ParsedArray) && ParsedArray.Num() > 0;

#if WITH_EDITOR
	Obj->SetFlags(RF_Transactional);
	Obj->Modify();
	Obj->PreEditChange(Prop);
#endif

	void* ValuePtr = Prop->ContainerPtrToValuePtr<void>(Obj);

	if (bJsonParsed)
	{
		FString Error = FUCPParamConverter::JsonValueToProperty(ParsedArray[0], Prop, ValuePtr);
		if (!Error.IsEmpty())
		{
			UE_LOG(LogObjectOp, Error, TEXT("SetObjectProperty: %s"), *Error);
			return FString();
		}
	}
	else
	{
		const TCHAR* Buffer = *JsonValue;
		if (!Prop->ImportText_Direct(Buffer, ValuePtr, Obj, PPF_None))
		{
			UE_LOG(LogObjectOp, Error, TEXT("SetObjectProperty: Failed to import value: %s"), *JsonValue);
			return FString();
		}
	}

#if WITH_EDITOR
	FPropertyChangedEvent ChangedEvent(Prop, EPropertyChangeType::ValueSet);
	Obj->PostEditChangeProperty(ChangedEvent);
#endif

	return FString();
}

FString UObjectOperationLibrary::DescribeObject(const FString& ObjectPath)
{
	TSharedPtr<FJsonObject> Result = FUCPFunctionInvoker::DescribeObject(ObjectPath);
	return JsonToString(Result);
}

FString UObjectOperationLibrary::DescribeObjectProperty(const FString& ObjectPath, const FString& PropertyName)
{
	TSharedPtr<FJsonObject> Result = FUCPFunctionInvoker::DescribeProperty(ObjectPath, PropertyName);
	return JsonToString(Result);
}

FString UObjectOperationLibrary::DescribeObjectFunction(const FString& ObjectPath, const FString& FunctionName)
{
	TSharedPtr<FJsonObject> Result = FUCPFunctionInvoker::DescribeFunction(ObjectPath, FunctionName);
	return JsonToString(Result);
}

FString UObjectOperationLibrary::FindObjectInstances(const FString& ClassName, int32 Limit)
{
	if (ClassName.IsEmpty())
	{
		UE_LOG(LogObjectOp, Error, TEXT("FindObjectInstances: Missing ClassName"));
		return FString();
	}

	UClass* TargetClass = FindObject<UClass>(nullptr, *ClassName);
	if (!TargetClass)
	{
		TargetClass = LoadObject<UClass>(nullptr, *ClassName);
	}
	if (!TargetClass)
	{
		UE_LOG(LogObjectOp, Error, TEXT("FindObjectInstances: Class not found: %s"), *ClassName);
		return FString();
	}

	Limit = FMath::Clamp(Limit, 1, 10000);

	TArray<TSharedPtr<FJsonValue>> ObjectPaths;
	int32 Count = 0;
	for (TObjectIterator<UObject> It; It; ++It)
	{
		if (It->IsA(TargetClass))
		{
			ObjectPaths.Add(MakeShared<FJsonValueString>(It->GetPathName()));
			if (++Count >= Limit)
			{
				break;
			}
		}
	}

	TSharedPtr<FJsonObject> Result = MakeShared<FJsonObject>();
	Result->SetArrayField(TEXT("objects"), ObjectPaths);
	Result->SetNumberField(TEXT("count"), Count);
	return JsonToString(Result);
}

FString UObjectOperationLibrary::FindDerivedClasses(const FString& ClassName, bool bRecursive, int32 Limit)
{
	if (ClassName.IsEmpty())
	{
		UE_LOG(LogObjectOp, Error, TEXT("FindDerivedClasses: Missing ClassName"));
		return FString();
	}

	UClass* TargetClass = FindObject<UClass>(nullptr, *ClassName);
	if (!TargetClass)
	{
		TargetClass = LoadObject<UClass>(nullptr, *ClassName);
	}
	if (!TargetClass)
	{
		UE_LOG(LogObjectOp, Error, TEXT("FindDerivedClasses: Class not found: %s"), *ClassName);
		return FString();
	}

	Limit = FMath::Clamp(Limit, 1, 10000);

	TArray<UClass*> DerivedClassList;
	::GetDerivedClasses(TargetClass, DerivedClassList, bRecursive);

	TArray<TSharedPtr<FJsonValue>> ClassPaths;
	int32 Count = 0;
	for (UClass* DerivedClass : DerivedClassList)
	{
		ClassPaths.Add(MakeShared<FJsonValueString>(DerivedClass->GetPathName()));
		if (++Count >= Limit)
		{
			break;
		}
	}

	TSharedPtr<FJsonObject> Result = MakeShared<FJsonObject>();
	Result->SetArrayField(TEXT("classes"), ClassPaths);
	Result->SetNumberField(TEXT("count"), Count);
	return JsonToString(Result);
}

FString UObjectOperationLibrary::ListComponents(const FString& ObjectPath)
{
	if (ObjectPath.IsEmpty())
	{
		UE_LOG(LogObjectOp, Error, TEXT("ListComponents: Missing ObjectPath"));
		return FString();
	}

	UObject* Obj = UCPUtils::LoadObject(ObjectPath);
	if (!Obj)
	{
		UE_LOG(LogObjectOp, Error, TEXT("ListComponents: Object not found: %s"), *ObjectPath);
		return FString();
	}

	TArray<TSharedPtr<FJsonValue>> CompArray;

	AActor* Actor = Cast<AActor>(Obj);
	if (Actor)
	{
		TInlineComponentArray<UActorComponent*> Components;
		Actor->GetComponents(Components);
		for (UActorComponent* Comp : Components)
		{
			if (!Comp) continue;
			TSharedPtr<FJsonObject> CompObj = MakeShared<FJsonObject>();
			CompObj->SetStringField(TEXT("name"), Comp->GetName());
			CompObj->SetStringField(TEXT("class"), Comp->GetClass()->GetName());
			CompObj->SetStringField(TEXT("path"), Comp->GetPathName());

			if (USceneComponent* SceneComp = Cast<USceneComponent>(Comp))
			{
				USceneComponent* Parent = SceneComp->GetAttachParent();
				CompObj->SetStringField(TEXT("parent"), Parent ? Parent->GetName() : TEXT(""));
			}

			CompArray.Add(MakeShared<FJsonValueObject>(CompObj));
		}
	}
	else
	{
		ForEachObjectWithOuter(Obj, [&CompArray](UObject* SubObj)
		{
			TSharedPtr<FJsonObject> SubObjJson = MakeShared<FJsonObject>();
			SubObjJson->SetStringField(TEXT("name"), SubObj->GetName());
			SubObjJson->SetStringField(TEXT("class"), SubObj->GetClass()->GetName());
			SubObjJson->SetStringField(TEXT("path"), SubObj->GetPathName());
			CompArray.Add(MakeShared<FJsonValueObject>(SubObjJson));
		}, false);
	}

	TSharedPtr<FJsonObject> Result = MakeShared<FJsonObject>();
	Result->SetArrayField(TEXT("components"), CompArray);
	Result->SetNumberField(TEXT("count"), CompArray.Num());
	return JsonToString(Result);
}

FString UObjectOperationLibrary::FindObjectsByOuter(const FString& OuterPath, const FString& ClassName, int32 Limit)
{
	if (OuterPath.IsEmpty())
	{
		UE_LOG(LogObjectOp, Error, TEXT("FindObjectsByOuter: Missing OuterPath"));
		return FString();
	}

	UObject* OuterObj = UCPUtils::LoadObject(OuterPath);
	if (!OuterObj)
	{
		UE_LOG(LogObjectOp, Error, TEXT("FindObjectsByOuter: Outer not found: %s"), *OuterPath);
		return FString();
	}

	UClass* FilterClass = nullptr;
	if (!ClassName.IsEmpty())
	{
		FilterClass = FindObject<UClass>(nullptr, *ClassName);
		if (!FilterClass)
		{
			FilterClass = LoadObject<UClass>(nullptr, *ClassName);
		}
		if (!FilterClass)
		{
			UE_LOG(LogObjectOp, Error, TEXT("FindObjectsByOuter: Class not found: %s"), *ClassName);
			return FString();
		}
	}

	Limit = FMath::Clamp(Limit, 1, 10000);

	TArray<TSharedPtr<FJsonValue>> ObjectArray;
	int32 Count = 0;

	ForEachObjectWithOuter(OuterObj, [&](UObject* SubObj)
	{
		if (Count >= Limit) return;
		if (FilterClass && !SubObj->IsA(FilterClass)) return;

		TSharedPtr<FJsonObject> ObjJson = MakeShared<FJsonObject>();
		ObjJson->SetStringField(TEXT("name"), SubObj->GetName());
		ObjJson->SetStringField(TEXT("class"), SubObj->GetClass()->GetName());
		ObjJson->SetStringField(TEXT("path"), SubObj->GetPathName());
		ObjectArray.Add(MakeShared<FJsonValueObject>(ObjJson));
		Count++;
	}, true);

	TSharedPtr<FJsonObject> Result = MakeShared<FJsonObject>();
	Result->SetArrayField(TEXT("objects"), ObjectArray);
	Result->SetNumberField(TEXT("count"), Count);
	return JsonToString(Result);
}
