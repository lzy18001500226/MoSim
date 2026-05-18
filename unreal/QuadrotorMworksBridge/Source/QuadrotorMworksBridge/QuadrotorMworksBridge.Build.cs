using UnrealBuildTool;

public class QuadrotorMworksBridge : ModuleRules
{
    public QuadrotorMworksBridge(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "Json",
            "JsonUtilities",
            "Networking",
            "Sockets"
        });
    }
}
