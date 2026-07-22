within MoSimQuadrotorModel.Controllers.Sysblocks;
model AWFF_FaultCompensationControllerEquation_Sysblock
  "AWFF controller with known rotor-1 efficiency allocation compensation"
  extends AWFF_L1FaultAllocationControllerEquation_Sysblock(
    l1_gain_xy = 0,
    l1_gain_z = 0,
    l1_comp_limit_xy = 0,
    l1_comp_limit_z = 0,
    rotor1_efficiency = 0.85,
    rotor1_allocation_blend = 0.52);
end AWFF_FaultCompensationControllerEquation_Sysblock;