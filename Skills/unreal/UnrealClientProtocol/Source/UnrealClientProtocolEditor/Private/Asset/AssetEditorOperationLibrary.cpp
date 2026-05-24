// MIT License - Copyright (c) 2025 Italink

#include "Asset/AssetEditorOperationLibrary.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "ObjectTools.h"
#include "AssetToolsModule.h"
#include "IAssetTools.h"
#include "UObject/UObjectGlobals.h"

TScriptInterface<IAssetRegistry> UAssetEditorOperationLibrary::GetAssetRegistry()
{
	IAssetRegistry& Registry = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry").Get();
	return TScriptInterface<IAssetRegistry>(Cast<UObject>(&Registry));
}

int32 UAssetEditorOperationLibrary::ForceDeleteAssets(const TArray<FString>& AssetPaths)
{
	TArray<UObject*> ObjectsToDelete;
	for (const FString& Path : AssetPaths)
	{
		UObject* Obj = StaticLoadObject(UObject::StaticClass(), nullptr, *Path);
		if (Obj)
		{
			ObjectsToDelete.Add(Obj);
		}
		else
		{
			UE_LOG(LogTemp, Warning, TEXT("[UCP] ForceDeleteAssets: Could not load asset: %s"), *Path);
		}
	}

	if (ObjectsToDelete.Num() == 0)
	{
		return 0;
	}

	return ObjectTools::ForceDeleteObjects(ObjectsToDelete, false);
}

bool UAssetEditorOperationLibrary::FixupReferencers(const TArray<FString>& AssetPaths)
{
	IAssetRegistry& Registry = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry").Get();

	TArray<UObjectRedirector*> Redirectors;
	for (const FString& Path : AssetPaths)
	{
		FAssetData AssetData = Registry.GetAssetByObjectPath(FSoftObjectPath(Path));
		if (AssetData.IsValid() && AssetData.IsRedirector())
		{
			UObject* Obj = AssetData.GetAsset();
			if (UObjectRedirector* Redirector = Cast<UObjectRedirector>(Obj))
			{
				Redirectors.Add(Redirector);
			}
		}
	}

	if (Redirectors.Num() == 0)
	{
		UE_LOG(LogTemp, Warning, TEXT("[UCP] FixupReferencers: No redirectors found in the provided paths"));
		return false;
	}

	IAssetTools& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools").Get();
	AssetTools.FixupReferencers(Redirectors, false);
	return true;
}
