within MoSimQuadrotorModel.Guidance.Planning;
block ThreeUavPairwiseEcbfReferenceSmoother
  "Critically damped position governor between raw ECBF corrections and the sampled PX4CTRL reference boundary"

  parameter Real correction_time_constant_s(min = 0.02, unit = "s") = 0.20
    "Second-order position-correction response time";
  parameter Real correction_damping_ratio(min = 0.5) = 1.0
    "Critically damped correction response avoids reference-channel overshoot";
  parameter Real maximum_correction_acceleration_m_s2(min = 0.01, unit = "m/s2") = 1.5
    "Bound the safety correction acceleration before it reaches PX4CTRL";

  Modelica.Blocks.Interfaces.RealInput nominal_position_1[3];
  Modelica.Blocks.Interfaces.RealInput nominal_velocity_1[3];
  Modelica.Blocks.Interfaces.RealInput nominal_acceleration_1[3];
  Modelica.Blocks.Interfaces.RealInput nominal_position_2[3];
  Modelica.Blocks.Interfaces.RealInput nominal_velocity_2[3];
  Modelica.Blocks.Interfaces.RealInput nominal_acceleration_2[3];
  Modelica.Blocks.Interfaces.RealInput nominal_position_3[3];
  Modelica.Blocks.Interfaces.RealInput nominal_velocity_3[3];
  Modelica.Blocks.Interfaces.RealInput nominal_acceleration_3[3];

  Modelica.Blocks.Interfaces.RealInput raw_safe_position_1[3];
  Modelica.Blocks.Interfaces.RealInput raw_safe_position_2[3];
  Modelica.Blocks.Interfaces.RealInput raw_safe_position_3[3];

  Modelica.Blocks.Interfaces.RealOutput safe_position_1[3];
  Modelica.Blocks.Interfaces.RealOutput safe_velocity_1[3];
  Modelica.Blocks.Interfaces.RealOutput safe_acceleration_1[3];
  Modelica.Blocks.Interfaces.RealOutput safe_position_2[3];
  Modelica.Blocks.Interfaces.RealOutput safe_velocity_2[3];
  Modelica.Blocks.Interfaces.RealOutput safe_acceleration_2[3];
  Modelica.Blocks.Interfaces.RealOutput safe_position_3[3];
  Modelica.Blocks.Interfaces.RealOutput safe_velocity_3[3];
  Modelica.Blocks.Interfaces.RealOutput safe_acceleration_3[3];
  Modelica.Blocks.Interfaces.RealOutput maximum_applied_reference_offset_m(unit = "m");

protected
  Real nominalPosition[3, 3];
  Real nominalVelocity[3, 3];
  Real nominalAcceleration[3, 3];
  Real rawSafePosition[3, 3];
  Real positionCorrectionTarget[3, 3];
  Real positionCorrection[3, 3](each start = 0, each fixed = true);
  Real velocityCorrection[3, 3](each start = 0, each fixed = true);
  Real correctionAccelerationRaw[3, 3];
  Real correctionAccelerationNorm[3];
  Real correctionAccelerationScale[3];
  Real correctionAcceleration[3, 3];

equation
  for axis in 1:3 loop
    nominalPosition[1, axis] = nominal_position_1[axis];
    nominalVelocity[1, axis] = nominal_velocity_1[axis];
    nominalAcceleration[1, axis] = nominal_acceleration_1[axis];
    nominalPosition[2, axis] = nominal_position_2[axis];
    nominalVelocity[2, axis] = nominal_velocity_2[axis];
    nominalAcceleration[2, axis] = nominal_acceleration_2[axis];
    nominalPosition[3, axis] = nominal_position_3[axis];
    nominalVelocity[3, axis] = nominal_velocity_3[axis];
    nominalAcceleration[3, axis] = nominal_acceleration_3[axis];

    rawSafePosition[1, axis] = raw_safe_position_1[axis];
    rawSafePosition[2, axis] = raw_safe_position_2[axis];
    rawSafePosition[3, axis] = raw_safe_position_3[axis];
  end for;

  for vehicle in 1:3 loop
    for axis in 1:3 loop
      positionCorrectionTarget[vehicle, axis] = rawSafePosition[vehicle, axis]
        - nominalPosition[vehicle, axis];
      der(positionCorrection[vehicle, axis]) = velocityCorrection[vehicle, axis];
      correctionAccelerationRaw[vehicle, axis] = (positionCorrectionTarget[vehicle, axis]
        - positionCorrection[vehicle, axis]) / correction_time_constant_s ^ 2
        - 2 * correction_damping_ratio * velocityCorrection[vehicle, axis]
          / correction_time_constant_s;
    end for;
    correctionAccelerationNorm[vehicle] = sqrt(sum(
      correctionAccelerationRaw[vehicle, axis] ^ 2 for axis in 1:3));
    correctionAccelerationScale[vehicle] = min(1.0,
      maximum_correction_acceleration_m_s2 /
      max(Modelica.Constants.eps, correctionAccelerationNorm[vehicle]));
    for axis in 1:3 loop
      correctionAcceleration[vehicle, axis] = correctionAccelerationScale[vehicle]
        * correctionAccelerationRaw[vehicle, axis];
      der(velocityCorrection[vehicle, axis]) = correctionAcceleration[vehicle, axis];
    end for;
  end for;

  for axis in 1:3 loop
    safe_position_1[axis] = nominalPosition[1, axis] + positionCorrection[1, axis];
    safe_velocity_1[axis] = nominalVelocity[1, axis] + velocityCorrection[1, axis];
    safe_acceleration_1[axis] = nominalAcceleration[1, axis] + correctionAcceleration[1, axis];
    safe_position_2[axis] = nominalPosition[2, axis] + positionCorrection[2, axis];
    safe_velocity_2[axis] = nominalVelocity[2, axis] + velocityCorrection[2, axis];
    safe_acceleration_2[axis] = nominalAcceleration[2, axis] + correctionAcceleration[2, axis];
    safe_position_3[axis] = nominalPosition[3, axis] + positionCorrection[3, axis];
    safe_velocity_3[axis] = nominalVelocity[3, axis] + velocityCorrection[3, axis];
    safe_acceleration_3[axis] = nominalAcceleration[3, axis] + correctionAcceleration[3, axis];
  end for;

  maximum_applied_reference_offset_m = max(
    sqrt(sum(positionCorrection[1, axis] ^ 2 for axis in 1:3)),
    max(sqrt(sum(positionCorrection[2, axis] ^ 2 for axis in 1:3)),
      sqrt(sum(positionCorrection[3, axis] ^ 2 for axis in 1:3))));

  annotation(
    Icon(coordinateSystem(extent = {{-140, -120}, {140, 120}}), graphics = {
      Rectangle(extent = {{-140, -120}, {140, 120}}, lineColor = {0, 92, 74}, fillColor = {226, 246, 238}, fillPattern = FillPattern.Solid),
      Text(extent = {{-126, 30}, {126, 70}}, textString = "ECBF Correction"),
      Text(extent = {{-126, -16}, {126, 24}}, textString = "Continuous Governor"),
      Text(extent = {{-126, -80}, {126, -42}}, textString = "position / velocity / acceleration", textColor = {0, 92, 74})}),
    Diagram(coordinateSystem(extent = {{-140, -120}, {140, 120}})),
    __MWORKS(hide = false, version = "26.3.0"));
end ThreeUavPairwiseEcbfReferenceSmoother;