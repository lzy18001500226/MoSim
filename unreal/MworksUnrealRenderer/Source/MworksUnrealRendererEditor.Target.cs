using UnrealBuildTool;
using System.Collections.Generic;

public class MworksUnrealRendererEditorTarget : TargetRules
{
    public MworksUnrealRendererEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V6;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("MworksUnrealRenderer");
    }
}
