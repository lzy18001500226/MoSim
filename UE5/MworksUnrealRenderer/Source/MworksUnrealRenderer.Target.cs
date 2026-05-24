using UnrealBuildTool;
using System.Collections.Generic;

public class MworksUnrealRendererTarget : TargetRules
{
    public MworksUnrealRendererTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V6;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("MworksUnrealRenderer");
    }
}
