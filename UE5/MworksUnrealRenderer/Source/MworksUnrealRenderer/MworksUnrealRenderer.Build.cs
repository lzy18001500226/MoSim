using UnrealBuildTool;

public class MworksUnrealRenderer : ModuleRules
{
    public MworksUnrealRenderer(ReadOnlyTargetRules Target) : base(Target)
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
