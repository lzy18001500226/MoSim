model FactoryTraceIso24DirectAttitudeFeedbackSmoke
  "Control feedback 24: direct AngleMea attitude feedback while preserving Iso23 display bridge"
  extends FactoryTraceIso23PositionSampleHoldBridgeSmoke(
    roll_estimated(y = sensors1_1.AngleMea[1]),
    pitch_estimated(y = sensors1_1.AngleMea[2]),
    yaw_estimated(y = sensors1_1.AngleMea[3]));

  Real direct_roll_mea;
  Real direct_pitch_mea;
  Real direct_yaw_mea;

equation
  direct_roll_mea = sensors1_1.AngleMea[1];
  direct_pitch_mea = sensors1_1.AngleMea[2];
  direct_yaw_mea = sensors1_1.AngleMea[3];
end FactoryTraceIso24DirectAttitudeFeedbackSmoke;
