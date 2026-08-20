within MoSimQuadrotorModel.Guidance.Formation;
model ThreeUavPairwiseEcbfReferenceSafetyFilter
  "Three-UAV pairwise ECBF reference governor for the PX4CTRL formation route"

  parameter Boolean enabled = true
    "Keep the isolated safety branch explicit; the baseline route bypasses this model";
  parameter Real pair_minimum_distance_m(min = 0.1, unit = "m") = 1.0
    "Hard review threshold; this model does not turn it into a plant-contact claim";
  parameter Real pair_activation_distance_m(min = pair_minimum_distance_m, unit = "m") = 1.5
    "Predictive intervention distance above the hard review threshold";
  parameter Real ecbf_lambda(min = 0.01) = 1.0
    "Exponential-barrier pole for pairwise relative-degree-two projection";
  parameter Real prediction_horizon_s(min = 0.01, unit = "s") = 0.8
    "Short-horizon closing-speed preview used by the reference governor";
  parameter Real reference_lookahead_s(min = 0.01, unit = "s") = 0.35
    "Converts a bounded position correction into a consistent velocity reference";
  parameter Real max_reference_offset_m(min = 0.01, unit = "m") = 0.5
    "Per-vehicle safety-reference correction limit";
  parameter Real max_safety_acceleration_correction_m_s2(min = 0.01, unit = "m/s2") = 1.5
    "Per-vehicle correction limit; nominal A*/EGO acceleration is not clipped";
  parameter Integer projection_passes(min = 1) = 2
    "Fixed sequential half-space projection passes for the three pair constraints";
  parameter Real epsilon = 1e-8;

  Modelica.Blocks.Interfaces.RealInput nominal_position_1[3] 
    annotation(Placement(transformation(origin = {-140, 84}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealInput nominal_velocity_1[3] 
    annotation(Placement(transformation(origin = {-140, 60}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealInput nominal_acceleration_1[3] 
    annotation(Placement(transformation(origin = {-140, 36}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealInput nominal_position_2[3] 
    annotation(Placement(transformation(origin = {-140, 12}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealInput nominal_velocity_2[3] 
    annotation(Placement(transformation(origin = {-140, -12}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealInput nominal_acceleration_2[3] 
    annotation(Placement(transformation(origin = {-140, -36}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealInput nominal_position_3[3] 
    annotation(Placement(transformation(origin = {-140, -60}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealInput nominal_velocity_3[3] 
    annotation(Placement(transformation(origin = {-140, -84}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealInput nominal_acceleration_3[3] 
    annotation(Placement(transformation(origin = {-140, -108}, extent = {{-12, -12}, {12, 12}})));

  Modelica.Blocks.Interfaces.RealInput actual_position_1[3] 
    annotation(Placement(transformation(origin = {-72, 84}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealInput actual_velocity_1[3] 
    annotation(Placement(transformation(origin = {-72, 60}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealInput actual_position_2[3] 
    annotation(Placement(transformation(origin = {-72, 12}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealInput actual_velocity_2[3] 
    annotation(Placement(transformation(origin = {-72, -12}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealInput actual_position_3[3] 
    annotation(Placement(transformation(origin = {-72, -60}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealInput actual_velocity_3[3] 
    annotation(Placement(transformation(origin = {-72, -84}, extent = {{-12, -12}, {12, 12}})));

  Modelica.Blocks.Interfaces.RealOutput safe_position_1[3] 
    annotation(Placement(transformation(origin = {140, 84}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealOutput safe_velocity_1[3] 
    annotation(Placement(transformation(origin = {140, 60}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealOutput safe_acceleration_1[3] 
    annotation(Placement(transformation(origin = {140, 36}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealOutput safe_position_2[3] 
    annotation(Placement(transformation(origin = {140, 12}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealOutput safe_velocity_2[3] 
    annotation(Placement(transformation(origin = {140, -12}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealOutput safe_acceleration_2[3] 
    annotation(Placement(transformation(origin = {140, -36}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealOutput safe_position_3[3] 
    annotation(Placement(transformation(origin = {140, -60}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealOutput safe_velocity_3[3] 
    annotation(Placement(transformation(origin = {140, -84}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Interfaces.RealOutput safe_acceleration_3[3] 
    annotation(Placement(transformation(origin = {140, -108}, extent = {{-12, -12}, {12, 12}})));

  Real minimum_actual_pair_distance_m(unit = "m");
  Real minimum_predicted_pair_distance_m(unit = "m");
  Integer active_pair_count;
  Real maximum_reference_offset_m(unit = "m");
  Real maximum_ecbf_residual_m2_s2(unit = "m2/s2");
  Boolean correction_saturated;

protected
  function projectPairwiseReference
    input Real nominalPosition[3, 3];
    input Real nominalVelocity[3, 3];
    input Real nominalAcceleration[3, 3];
    input Real actualPosition[3, 3];
    input Real actualVelocity[3, 3];
    input Boolean safetyEnabled;
    input Real minimumDistance;
    input Real activationDistance;
    input Real lambda;
    input Real predictionHorizon;
    input Real referenceLookahead;
    input Real maximumReferenceOffset;
    input Real maximumAccelerationCorrection;
    input Integer projectionPasses;
    input Real small;
    output Real safePosition[3, 3];
    output Real safeVelocity[3, 3];
    output Real safeAcceleration[3, 3];
    output Real minimumActualPairDistance;
    output Real minimumPredictedPairDistance;
    output Integer activePairCount;
    output Real maximumReferenceOffsetObserved;
    output Real maximumEcbfResidual;
    output Boolean correctionSaturated;
  protected
    Real accelerationCorrection[3, 3];
    Real positionCorrection[3, 3];
    Real relativePosition[3];
    Real relativeVelocity[3];
    Real distanceSquared;
    Real distance;
    Real radialSpeed;
    Real predictedDistance;
    Real positionVelocityDot;
    Real relativeVelocitySquared;
    Real nominalRelativeAccelerationDot;
    Real correctionRelativeAccelerationDot;
    Real requiredRadialAcceleration;
    Real residual;
    Real correctionScale;
    Real anticipatedGap;
    Real positionCorrectionMagnitude;
    Real positionCorrectionNorm;
    Real accelerationCorrectionNorm;
    Real scale;
    Integer first;
    Integer second;
  algorithm
    for vehicle in 1:3 loop
      for axis in 1:3 loop
        safePosition[vehicle, axis] := nominalPosition[vehicle, axis];
        safeVelocity[vehicle, axis] := nominalVelocity[vehicle, axis];
        safeAcceleration[vehicle, axis] := nominalAcceleration[vehicle, axis];
        accelerationCorrection[vehicle, axis] := 0.0;
        positionCorrection[vehicle, axis] := 0.0;
      end for;
    end for;
    minimumActualPairDistance := 1e6;
    minimumPredictedPairDistance := 1e6;
    activePairCount := 0;
    maximumReferenceOffsetObserved := 0.0;
    maximumEcbfResidual := 0.0;
    correctionSaturated := false;

    for pair in 1:3 loop
      first := if pair == 1 then 1 else if pair == 2 then 1 else 2;
      second := if pair == 1 then 2 else 3;
      for axis in 1:3 loop
        relativePosition[axis] := actualPosition[first, axis] - actualPosition[second, axis];
        relativeVelocity[axis] := actualVelocity[first, axis] - actualVelocity[second, axis];
      end for;
      distanceSquared := sum(relativePosition[axis] ^ 2 for axis in 1:3);
      distance := sqrt(max(small, distanceSquared));
      radialSpeed := sum(relativePosition[axis] * relativeVelocity[axis] for axis in 1:3) / distance;
      predictedDistance := max(0.0, distance + min(0.0, radialSpeed) * predictionHorizon);
      minimumActualPairDistance := min(minimumActualPairDistance, sqrt(max(0.0, distanceSquared)));
      minimumPredictedPairDistance := min(minimumPredictedPairDistance, predictedDistance);
    end for;

    if safetyEnabled then
      for pass in 1:projectionPasses loop
        for pair in 1:3 loop
          first := if pair == 1 then 1 else if pair == 2 then 1 else 2;
          second := if pair == 1 then 2 else 3;
          for axis in 1:3 loop
            relativePosition[axis] := actualPosition[first, axis] - actualPosition[second, axis];
            relativeVelocity[axis] := actualVelocity[first, axis] - actualVelocity[second, axis];
          end for;
          distanceSquared := sum(relativePosition[axis] ^ 2 for axis in 1:3);
          distance := sqrt(max(small, distanceSquared));
          positionVelocityDot := sum(relativePosition[axis] * relativeVelocity[axis] for axis in 1:3);
          radialSpeed := positionVelocityDot / distance;
          predictedDistance := max(0.0, distance + min(0.0, radialSpeed) * predictionHorizon);
          relativeVelocitySquared := sum(relativeVelocity[axis] ^ 2 for axis in 1:3);
          nominalRelativeAccelerationDot := sum(relativePosition[axis] *
            (nominalAcceleration[first, axis] - nominalAcceleration[second, axis]) for axis in 1:3);
          correctionRelativeAccelerationDot := sum(relativePosition[axis] *
            (accelerationCorrection[first, axis] - accelerationCorrection[second, axis]) for axis in 1:3);
          requiredRadialAcceleration := -relativeVelocitySquared - 2.0 * lambda * positionVelocityDot
            - 0.5 * lambda ^ 2 * (distanceSquared - activationDistance ^ 2);
          residual := max(0.0, requiredRadialAcceleration
            - nominalRelativeAccelerationDot - correctionRelativeAccelerationDot);
          anticipatedGap := max(0.0, activationDistance - predictedDistance);

          if pass == 1 and (residual > small or anticipatedGap > small) then
            activePairCount := activePairCount + 1;
          end if;
          maximumEcbfResidual := max(maximumEcbfResidual, residual);

          if distanceSquared > small then
            correctionScale := 0.5 * residual / distanceSquared;
            positionCorrectionMagnitude := 0.5 * anticipatedGap;
            for axis in 1:3 loop
              accelerationCorrection[first, axis] := accelerationCorrection[first, axis]
                + correctionScale * relativePosition[axis];
              accelerationCorrection[second, axis] := accelerationCorrection[second, axis]
                - correctionScale * relativePosition[axis];
              positionCorrection[first, axis] := positionCorrection[first, axis]
                + positionCorrectionMagnitude * relativePosition[axis] / distance;
              positionCorrection[second, axis] := positionCorrection[second, axis]
                - positionCorrectionMagnitude * relativePosition[axis] / distance;
            end for;
          end if;
        end for;
      end for;

      for vehicle in 1:3 loop
        positionCorrectionNorm := sqrt(sum(positionCorrection[vehicle, axis] ^ 2 for axis in 1:3));
        if positionCorrectionNorm > maximumReferenceOffset then
          scale := maximumReferenceOffset / positionCorrectionNorm;
          correctionSaturated := true;
        else
          scale := 1.0;
        end if;
        for axis in 1:3 loop
          positionCorrection[vehicle, axis] := scale * positionCorrection[vehicle, axis];
        end for;

        accelerationCorrectionNorm := sqrt(sum(accelerationCorrection[vehicle, axis] ^ 2 for axis in 1:3));
        if accelerationCorrectionNorm > maximumAccelerationCorrection then
          scale := maximumAccelerationCorrection / accelerationCorrectionNorm;
          correctionSaturated := true;
        else
          scale := 1.0;
        end if;
        for axis in 1:3 loop
          accelerationCorrection[vehicle, axis] := scale * accelerationCorrection[vehicle, axis];
          safePosition[vehicle, axis] := nominalPosition[vehicle, axis] + positionCorrection[vehicle, axis];
          safeVelocity[vehicle, axis] := nominalVelocity[vehicle, axis]
            + positionCorrection[vehicle, axis] / referenceLookahead;
          safeAcceleration[vehicle, axis] := nominalAcceleration[vehicle, axis]
            + accelerationCorrection[vehicle, axis];
        end for;
        maximumReferenceOffsetObserved := max(maximumReferenceOffsetObserved,
          sqrt(sum(positionCorrection[vehicle, axis] ^ 2 for axis in 1:3)));
      end for;
    end if;
  end projectPairwiseReference;

  Real nominalPosition[3, 3];
  Real nominalVelocity[3, 3];
  Real nominalAcceleration[3, 3];
  Real actualPosition[3, 3];
  Real actualVelocity[3, 3];
  Real safePosition[3, 3];
  Real safeVelocity[3, 3];
  Real safeAcceleration[3, 3];

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

    actualPosition[1, axis] = actual_position_1[axis];
    actualVelocity[1, axis] = actual_velocity_1[axis];
    actualPosition[2, axis] = actual_position_2[axis];
    actualVelocity[2, axis] = actual_velocity_2[axis];
    actualPosition[3, axis] = actual_position_3[axis];
    actualVelocity[3, axis] = actual_velocity_3[axis];
  end for;

  (safePosition, safeVelocity, safeAcceleration, minimum_actual_pair_distance_m,
    minimum_predicted_pair_distance_m, active_pair_count, maximum_reference_offset_m,
    maximum_ecbf_residual_m2_s2, correction_saturated) = projectPairwiseReference(
      nominalPosition, nominalVelocity, nominalAcceleration, actualPosition, actualVelocity,
      enabled, pair_minimum_distance_m, pair_activation_distance_m, ecbf_lambda,
      prediction_horizon_s, reference_lookahead_s, max_reference_offset_m,
      max_safety_acceleration_correction_m_s2, projection_passes, epsilon);

  for axis in 1:3 loop
    safe_position_1[axis] = safePosition[1, axis];
    safe_velocity_1[axis] = safeVelocity[1, axis];
    safe_acceleration_1[axis] = safeAcceleration[1, axis];
    safe_position_2[axis] = safePosition[2, axis];
    safe_velocity_2[axis] = safeVelocity[2, axis];
    safe_acceleration_2[axis] = safeAcceleration[2, axis];
    safe_position_3[axis] = safePosition[3, axis];
    safe_velocity_3[axis] = safeVelocity[3, axis];
    safe_acceleration_3[axis] = safeAcceleration[3, axis];
  end for;

  annotation(
    Icon(coordinateSystem(extent = {{-140, -120}, {140, 120}}), graphics = {
      Rectangle(extent = {{-140, -120}, {140, 120}}, lineColor = {163, 94, 0}, fillColor = {255, 245, 224}, fillPattern = FillPattern.Solid),
      Text(extent = {{-124, 52}, {124, 86}}, textString = "Pairwise ECBF"),
      Text(extent = {{-124, 12}, {124, 46}}, textString = "Reference Safety"),
      Text(extent = {{-124, -72}, {124, -38}}, textString = "1.5 m preview / 1.0 m gate", textColor = {163, 94, 0})}),
    Diagram(coordinateSystem(extent = {{-140, -120}, {140, 120}})),
    __MWORKS(hide = false, version = "26.3.0"));
end ThreeUavPairwiseEcbfReferenceSafetyFilter;