// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
#include "UnrealMCP/Public/EpicUnrealMCPBridge.h"
PRAGMA_DISABLE_DEPRECATION_WARNINGS
void EmptyLinkFunctionForGeneratedCodeEpicUnrealMCPBridge() {}

// Begin Cross Module References
EDITORSUBSYSTEM_API UClass* Z_Construct_UClass_UEditorSubsystem();
UNREALMCP_API UClass* Z_Construct_UClass_UEpicUnrealMCPBridge();
UNREALMCP_API UClass* Z_Construct_UClass_UEpicUnrealMCPBridge_NoRegister();
UPackage* Z_Construct_UPackage__Script_UnrealMCP();
// End Cross Module References

// Begin Class UEpicUnrealMCPBridge
void UEpicUnrealMCPBridge::StaticRegisterNativesUEpicUnrealMCPBridge()
{
}
IMPLEMENT_CLASS_NO_AUTO_REGISTRATION(UEpicUnrealMCPBridge);
UClass* Z_Construct_UClass_UEpicUnrealMCPBridge_NoRegister()
{
	return UEpicUnrealMCPBridge::StaticClass();
}
struct Z_Construct_UClass_UEpicUnrealMCPBridge_Statics
{
#if WITH_METADATA
	static constexpr UECodeGen_Private::FMetaDataPairParam Class_MetaDataParams[] = {
#if !UE_BUILD_SHIPPING
		{ "Comment", "/**\n * Editor subsystem for MCP Bridge\n * Handles communication between external tools and the Unreal Editor\n * through a TCP socket connection. Commands are received as JSON and\n * routed to appropriate command handlers.\n */" },
#endif
		{ "IncludePath", "EpicUnrealMCPBridge.h" },
		{ "ModuleRelativePath", "Public/EpicUnrealMCPBridge.h" },
#if !UE_BUILD_SHIPPING
		{ "ToolTip", "Editor subsystem for MCP Bridge\nHandles communication between external tools and the Unreal Editor\nthrough a TCP socket connection. Commands are received as JSON and\nrouted to appropriate command handlers." },
#endif
	};
#endif // WITH_METADATA
	static UObject* (*const DependentSingletons[])();
	static constexpr FCppClassTypeInfoStatic StaticCppClassTypeInfo = {
		TCppClassTypeTraits<UEpicUnrealMCPBridge>::IsAbstract,
	};
	static const UECodeGen_Private::FClassParams ClassParams;
};
UObject* (*const Z_Construct_UClass_UEpicUnrealMCPBridge_Statics::DependentSingletons[])() = {
	(UObject* (*)())Z_Construct_UClass_UEditorSubsystem,
	(UObject* (*)())Z_Construct_UPackage__Script_UnrealMCP,
};
static_assert(UE_ARRAY_COUNT(Z_Construct_UClass_UEpicUnrealMCPBridge_Statics::DependentSingletons) < 16);
const UECodeGen_Private::FClassParams Z_Construct_UClass_UEpicUnrealMCPBridge_Statics::ClassParams = {
	&UEpicUnrealMCPBridge::StaticClass,
	nullptr,
	&StaticCppClassTypeInfo,
	DependentSingletons,
	nullptr,
	nullptr,
	nullptr,
	UE_ARRAY_COUNT(DependentSingletons),
	0,
	0,
	0,
	0x001000A0u,
	METADATA_PARAMS(UE_ARRAY_COUNT(Z_Construct_UClass_UEpicUnrealMCPBridge_Statics::Class_MetaDataParams), Z_Construct_UClass_UEpicUnrealMCPBridge_Statics::Class_MetaDataParams)
};
UClass* Z_Construct_UClass_UEpicUnrealMCPBridge()
{
	if (!Z_Registration_Info_UClass_UEpicUnrealMCPBridge.OuterSingleton)
	{
		UECodeGen_Private::ConstructUClass(Z_Registration_Info_UClass_UEpicUnrealMCPBridge.OuterSingleton, Z_Construct_UClass_UEpicUnrealMCPBridge_Statics::ClassParams);
	}
	return Z_Registration_Info_UClass_UEpicUnrealMCPBridge.OuterSingleton;
}
template<> UNREALMCP_API UClass* StaticClass<UEpicUnrealMCPBridge>()
{
	return UEpicUnrealMCPBridge::StaticClass();
}
DEFINE_VTABLE_PTR_HELPER_CTOR(UEpicUnrealMCPBridge);
// End Class UEpicUnrealMCPBridge

// Begin Registration
struct Z_CompiledInDeferFile_FID_Docs_Skills_Unreal_mcp_unreal_engine_mcp_FlopperamUnrealMCP_Plugins_UnrealMCP_Source_UnrealMCP_Public_EpicUnrealMCPBridge_h_Statics
{
	static constexpr FClassRegisterCompiledInInfo ClassInfo[] = {
		{ Z_Construct_UClass_UEpicUnrealMCPBridge, UEpicUnrealMCPBridge::StaticClass, TEXT("UEpicUnrealMCPBridge"), &Z_Registration_Info_UClass_UEpicUnrealMCPBridge, CONSTRUCT_RELOAD_VERSION_INFO(FClassReloadVersionInfo, sizeof(UEpicUnrealMCPBridge), 3933228240U) },
	};
};
static FRegisterCompiledInInfo Z_CompiledInDeferFile_FID_Docs_Skills_Unreal_mcp_unreal_engine_mcp_FlopperamUnrealMCP_Plugins_UnrealMCP_Source_UnrealMCP_Public_EpicUnrealMCPBridge_h_1389877631(TEXT("/Script/UnrealMCP"),
	Z_CompiledInDeferFile_FID_Docs_Skills_Unreal_mcp_unreal_engine_mcp_FlopperamUnrealMCP_Plugins_UnrealMCP_Source_UnrealMCP_Public_EpicUnrealMCPBridge_h_Statics::ClassInfo, UE_ARRAY_COUNT(Z_CompiledInDeferFile_FID_Docs_Skills_Unreal_mcp_unreal_engine_mcp_FlopperamUnrealMCP_Plugins_UnrealMCP_Source_UnrealMCP_Public_EpicUnrealMCPBridge_h_Statics::ClassInfo),
	nullptr, 0,
	nullptr, 0);
// End Registration
PRAGMA_ENABLE_DEPRECATION_WARNINGS
