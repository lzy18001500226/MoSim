using UnrealBuildTool;
using System.Collections.Generic;

public class MoSimSceneLibraryEditorTarget : TargetRules
{
    public MoSimSceneLibraryEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("MoSimSceneLibrary");
    }
}
