within MoSimQuadrotorModel.Control.LegacyExamples;
package PidVariants
  "Original Example1/2/3 PID variants retained for direct review, not FormalRunner experiments"
  extends Modelica.Icons.ExamplesPackage;

  model Example1AWFFBaseline
    "Step climb: AWFF PID legacy example"
    extends MoSimQuadrotorModel.Control.LegacyExamples.PidVariants.Example1AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Example1AWFFBaseline;

  model Example2AWFFBaseline
    "Spiral climb: AWFF PID legacy example"
    extends MoSimQuadrotorModel.Control.LegacyExamples.PidVariants.Example2AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Example2AWFFBaseline;

  model Example2HelixTunedAWFFBaseline
    "Spiral climb: tuned AWFF PID legacy example"
    extends MoSimQuadrotorModel.Control.LegacyExamples.PidVariants.Example2HelixTunedAntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Example2HelixTunedAWFFBaseline;

  model Example3AWFFBaseline
    "Figure eight: AWFF PID legacy example"
    extends MoSimQuadrotorModel.Control.LegacyExamples.PidVariants.Example3AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Example3AWFFBaseline;

  model Example1ImprovedPIDBaseline
    "Step climb: improved PID legacy example"
    extends MoSimQuadrotorModel.Control.LegacyExamples.PidVariants.Example1ImprovedPID;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Example1ImprovedPIDBaseline;

  model Example1EnhancedPIDBaseline
    "Step climb: enhanced PID legacy example"
    extends MoSimQuadrotorModel.Control.LegacyExamples.PidVariants.Example1EnhancedPID;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Example1EnhancedPIDBaseline;

  model Example2ImprovedPIDBaseline
    "Spiral climb: improved PID legacy example"
    extends MoSimQuadrotorModel.Control.LegacyExamples.PidVariants.Example2ImprovedPID;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Example2ImprovedPIDBaseline;

  model Example2EnhancedPIDBaseline
    "Spiral climb: enhanced PID legacy example"
    extends MoSimQuadrotorModel.Control.LegacyExamples.PidVariants.Example2EnhancedPID;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Example2EnhancedPIDBaseline;

  model Example2HelixTunedEnhancedPIDBaseline
    "Spiral climb: tuned enhanced PID legacy example"
    extends MoSimQuadrotorModel.Control.LegacyExamples.PidVariants.Example2HelixTunedEnhancedPID;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Example2HelixTunedEnhancedPIDBaseline;

  model Example3ImprovedPIDBaseline
    "Figure eight: improved PID legacy example"
    extends MoSimQuadrotorModel.Control.LegacyExamples.PidVariants.Example3ImprovedPID;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Example3ImprovedPIDBaseline;

  model Example3EnhancedPIDBaseline
    "Figure eight: enhanced PID legacy example"
    extends MoSimQuadrotorModel.Control.LegacyExamples.PidVariants.Example3EnhancedPID;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Example3EnhancedPIDBaseline;

  annotation(__MWORKS(hide=false,version="26.3.0"));
end PidVariants;
