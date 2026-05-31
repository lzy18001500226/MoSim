using UnrealBuildTool;
using System.Collections.Generic;

public class MoSimSceneLibraryTarget : TargetRules
{
    public MoSimSceneLibraryTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("MoSimSceneLibrary");
    }
}
