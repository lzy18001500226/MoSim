// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
PRAGMA_DISABLE_DEPRECATION_WARNINGS
void EmptyLinkFunctionForGeneratedCodeUnrealMCP_init() {}
	static FPackageRegistrationInfo Z_Registration_Info_UPackage__Script_UnrealMCP;
	FORCENOINLINE UPackage* Z_Construct_UPackage__Script_UnrealMCP()
	{
		if (!Z_Registration_Info_UPackage__Script_UnrealMCP.OuterSingleton)
		{
			static const UECodeGen_Private::FPackageParams PackageParams = {
				"/Script/UnrealMCP",
				nullptr,
				0,
				PKG_CompiledIn | 0x00000040,
				0x7C12852B,
				0x1FB39DE5,
				METADATA_PARAMS(0, nullptr)
			};
			UECodeGen_Private::ConstructUPackage(Z_Registration_Info_UPackage__Script_UnrealMCP.OuterSingleton, PackageParams);
		}
		return Z_Registration_Info_UPackage__Script_UnrealMCP.OuterSingleton;
	}
	static FRegisterCompiledInInfo Z_CompiledInDeferPackage_UPackage__Script_UnrealMCP(Z_Construct_UPackage__Script_UnrealMCP, TEXT("/Script/UnrealMCP"), Z_Registration_Info_UPackage__Script_UnrealMCP, CONSTRUCT_RELOAD_VERSION_INFO(FPackageReloadVersionInfo, 0x7C12852B, 0x1FB39DE5));
PRAGMA_ENABLE_DEPRECATION_WARNINGS
