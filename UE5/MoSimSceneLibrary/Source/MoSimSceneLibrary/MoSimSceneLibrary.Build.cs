using UnrealBuildTool;

public class MoSimSceneLibrary : ModuleRules
{
    public MoSimSceneLibrary(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "InputCore",
            "QuadrotorMworksBridge"
        });
    }
}
