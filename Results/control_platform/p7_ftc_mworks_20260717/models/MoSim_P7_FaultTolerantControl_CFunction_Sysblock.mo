model MoSim_P7_FaultTolerantControl_CFunction_Sysblock
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(modelType=Control,PortArrangement(Left(mode_id_in, dt_in, desired_thrust_in, desired_roll_in, desired_pitch_in, desired_yaw_in, response_1_in, response_2_in, response_3_in, response_4_in, airborne_in, altitude_in, enable_in, reset_in), Right(motor_command_1_out, motor_command_2_out, motor_command_3_out, motor_command_4_out, eta_hat_1_out, eta_hat_2_out, eta_hat_3_out, eta_hat_4_out, achieved_thrust_out, achieved_roll_out, achieved_pitch_out, achieved_yaw_out, residual_norm_out, isolated_mask_out, fault_count_out, action_out, allocation_saturated_out, status_code_out)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0",version="26.3.0",CodeGeneration(Config = {"code_placement":{"mode":"Compact"},"code_replacement":{"standard_c_library":"C99"},"custom_code":{"code":{"function_declare":{"head":"","item_head":"","item_tail":"","tail":""},"function_define":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_declare":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_define":{"head":"","item_head":"","item_tail":"","tail":""},"include":{"head":"","item_head":"","item_tail":"","tail":""},"macro":{"head":"","item_head":"","item_tail":"","tail":""},"type":{"head":"","item_head":"","item_tail":"","tail":""}},"code_protection":{"integer_division_by_zero":false,"overflow":false}},"data_type":{"real_as_float":false},"experiment":{"task_and_sample":{"muti_task_mode":false,"whether_to_use_prefix":false}},"hardware_platform":{"largest_atomic_size":{"floating_point":"64","integer":"32"}},"identifier":{"max_length":32,"style":{"function":"camelCase","local_variable":"camelCase","macro":"camelCase","mem_var":"camelCase","type":"camelCase"}},"interface":{"function_name":{"initialize":"Init","step":"Step"}},"is_expand":{"is_expand":false},"optimization":{"array_loop_threshold":5,"logical_operator":"logical"}}, Sim_seting = {"sim_seting":{"output":"C:\\Users\\HP\\Desktop\\MoSim\\Results\\control_platform\\p7_ftc_mworks_20260717\\generated_c"
}})),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.03,StoreEventValue=0),Diagram(coordinateSystem(extent={{-340,-620},{340,280}},grid={2,2})));

  CFunction cFunction 
    annotation (Placement(transformation(origin={0,0}, extent={{-28,-20},{28,20}})),__MWORKS(BlockSystem(SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport mode_id_in 
    annotation (Placement(transformation(origin={-300,250},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport dt_in 
    annotation (Placement(transformation(origin={-300,243},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport desired_thrust_in 
    annotation (Placement(transformation(origin={-300,236},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport desired_roll_in 
    annotation (Placement(transformation(origin={-300,229},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport desired_pitch_in 
    annotation (Placement(transformation(origin={-300,222},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport desired_yaw_in 
    annotation (Placement(transformation(origin={-300,215},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport response_1_in 
    annotation (Placement(transformation(origin={-300,208},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport response_2_in 
    annotation (Placement(transformation(origin={-300,201},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport response_3_in 
    annotation (Placement(transformation(origin={-300,194},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport response_4_in 
    annotation (Placement(transformation(origin={-300,187},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport airborne_in 
    annotation (Placement(transformation(origin={-300,180},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport altitude_in 
    annotation (Placement(transformation(origin={-300,173},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport enable_in 
    annotation (Placement(transformation(origin={-300,166},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reset_in 
    annotation (Placement(transformation(origin={-300,159},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport motor_command_1_out 
    annotation (Placement(transformation(origin={300,160},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport motor_command_2_out 
    annotation (Placement(transformation(origin={300,151},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport motor_command_3_out 
    annotation (Placement(transformation(origin={300,142},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport motor_command_4_out 
    annotation (Placement(transformation(origin={300,133},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport eta_hat_1_out 
    annotation (Placement(transformation(origin={300,124},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport eta_hat_2_out 
    annotation (Placement(transformation(origin={300,115},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport eta_hat_3_out 
    annotation (Placement(transformation(origin={300,106},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport eta_hat_4_out 
    annotation (Placement(transformation(origin={300,97},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport achieved_thrust_out 
    annotation (Placement(transformation(origin={300,88},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport achieved_roll_out 
    annotation (Placement(transformation(origin={300,79},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport achieved_pitch_out 
    annotation (Placement(transformation(origin={300,70},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport achieved_yaw_out 
    annotation (Placement(transformation(origin={300,61},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport residual_norm_out 
    annotation (Placement(transformation(origin={300,52},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport isolated_mask_out 
    annotation (Placement(transformation(origin={300,43},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport fault_count_out 
    annotation (Placement(transformation(origin={300,34},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport action_out 
    annotation (Placement(transformation(origin={300,25},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport allocation_saturated_out 
    annotation (Placement(transformation(origin={300,16},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport status_code_out 
    annotation (Placement(transformation(origin={300,7},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));

  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

  block CFunction
    annotation(__MWORKS(PortArrangement(Left(mode_id, dt, desired_thrust, desired_roll, desired_pitch, desired_yaw, response_1, response_2, response_3, response_4, airborne, altitude, enable, reset), Right(motor_command_1, motor_command_2, motor_command_3, motor_command_4, eta_hat_1, eta_hat_2, eta_hat_3, eta_hat_4, achieved_thrust, achieved_roll, achieved_pitch, achieved_yaw, residual_norm, isolated_mask, fault_count, action, allocation_saturated, status_code)),PortLabels(labelType="CustomType",labels(label(text="mode_id",instance="mode_id"),label(text="dt",instance="dt"),label(text="desired_thrust",instance="desired_thrust"),label(text="desired_roll",instance="desired_roll"),label(text="desired_pitch",instance="desired_pitch"),label(text="desired_yaw",instance="desired_yaw"),label(text="response_1",instance="response_1"),label(text="response_2",instance="response_2"),label(text="response_3",instance="response_3"),label(text="response_4",instance="response_4"),label(text="airborne",instance="airborne"),label(text="altitude",instance="altitude"),label(text="enable",instance="enable"),label(text="reset",instance="reset"),label(text="motor_command_1",instance="motor_command_1"),label(text="motor_command_2",instance="motor_command_2"),label(text="motor_command_3",instance="motor_command_3"),label(text="motor_command_4",instance="motor_command_4"),label(text="eta_hat_1",instance="eta_hat_1"),label(text="eta_hat_2",instance="eta_hat_2"),label(text="eta_hat_3",instance="eta_hat_3"),label(text="eta_hat_4",instance="eta_hat_4"),label(text="achieved_thrust",instance="achieved_thrust"),label(text="achieved_roll",instance="achieved_roll"),label(text="achieved_pitch",instance="achieved_pitch"),label(text="achieved_yaw",instance="achieved_yaw"),label(text="residual_norm",instance="residual_norm"),label(text="isolated_mask",instance="isolated_mask"),label(text="fault_count",instance="fault_count"),label(text="action",instance="action"),label(text="allocation_saturated",instance=
"allocation_saturated"),label(text="status_code",instance="status_code"))),BlockSystem(blockKind=BlockKind.atomic,bltBlockKind=BltBlockKind.cfunction),independentInstance=true,sourceModel=SysplorerEmbeddedCoder.Utilities.CCaller,ExternalFunctionBlock,hide=true),
      Icon(coordinateSystem(extent={{-200,-100},{200,100}},preserveAspectRatio=false,initialScale=0.1,grid={2,2}),graphics={Rectangle(origin={0,0},fillColor={255,255,255},fillPattern=FillPattern.Solid,extent={{-200,100},{200,-100}}),Text(origin={0,0},extent={{-100,20},{100,-20}},textString="C",verticalAlignment=TextAlignment.VCenter),Text(origin={0,-120},lineColor={0,0,0},extent={{-150,20},{150,-20}},textString="%name",fontSize=14,textColor={0,0,0},verticalAlignment=TextAlignment.Top)}),
      Diagram(coordinateSystem(extent={{-100,-100},{100,100}},preserveAspectRatio=false,initialScale=0.1,grid={2,2})));

    function func_CFunction
      input SysplorerEmbeddedCoder.Types.Auto mode_id annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto dt annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto desired_thrust annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto desired_roll annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto desired_pitch annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto desired_yaw annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto response_1 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto response_2 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto response_3 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto response_4 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto airborne annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto altitude annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto enable annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reset annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto motor_command_1 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto motor_command_2 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto motor_command_3 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto motor_command_4 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto eta_hat_1 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto eta_hat_2 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto eta_hat_3 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto eta_hat_4 annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto achieved_thrust annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto achieved_roll annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto achieved_pitch annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto achieved_yaw annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto residual_norm annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto isolated_mask annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto fault_count annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto action annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto allocation_saturated annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto status_code annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
    external "C" MosimFaultTolerantControlStepScalar(mode_id,dt,desired_thrust,desired_roll,desired_pitch,desired_yaw,response_1,response_2,response_3,response_4,airborne,altitude,enable,reset,motor_command_1,motor_command_2,motor_command_3,motor_command_4,eta_hat_1,eta_hat_2,eta_hat_3,eta_hat_4,achieved_thrust,achieved_roll,achieved_pitch,achieved_yaw,residual_norm,isolated_mask,fault_count,action,allocation_saturated,status_code) 
      annotation (Include="enum {
    MOSIM_FTC_FDI = 1,
    MOSIM_FTC_PASSIVE = 2,
    MOSIM_FTC_ACTIVE = 3,
    MOSIM_FTC_FAULT_AWARE_ALLOCATION = 4,
    MOSIM_FTC_SINGLE_MOTOR_SAFE_LANDING = 5,
    MOSIM_FTC_MULTI_FAULT_RECONFIGURATION = 6
};

enum {
    MOSIM_FTC_ACTION_PASS = 0,
    MOSIM_FTC_ACTION_DETECT = 1,
    MOSIM_FTC_ACTION_RECONFIGURE = 2,
    MOSIM_FTC_ACTION_LAND = 3,
    MOSIM_FTC_ACTION_STOP = 4
};

typedef struct {
    double detection_threshold;
    double detection_persistence_s;
    double estimator_time_constant_s;
    double minimum_effectiveness;
    double passive_effectiveness_margin;
    double motor_command_min;
    double motor_command_max;
    double landing_thrust;
    double minimum_detection_command;
} MosimFtcParams;

typedef struct {
    double effectiveness_estimate[4];
    double residual_lpf[4];
    double fault_timer_s[4];
    unsigned int isolated_mask;
} MosimFtcState;

typedef struct {
    double dt;
    double desired_wrench[4];
    double measured_motor_response[4];
    int airborne;
    double altitude;
    int enable;
    int reset;
} MosimFtcInput;

typedef struct {
    double motor_command[4];
    double effectiveness_estimate[4];
    double achieved_wrench[4];
    double residual_norm;
    unsigned int isolated_mask;
    int fault_count;
    int action;
    int allocation_saturated;
    int status_code;
} MosimFtcOutput;

void mosim_ftc_default_params(MosimFtcParams *params);
void mosim_ftc_reset(MosimFtcState *state);
int mosim_ftc_step(int mode, const MosimFtcParams *params,
                   MosimFtcState *state, const MosimFtcInput *input,
                   MosimFtcOutput *output);




#include <math.h>
#include <stddef.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper) {
    return value < lower ? lower : (value > upper ? upper : value);
}

static int finite4(const double value[4]) {
    return isfinite(value[0]) && isfinite(value[1]) &&
           isfinite(value[2]) && isfinite(value[3]);
}

static int bit_count(unsigned int value) {
    int count = 0;
    while (value != 0u) {
        count += (int)(value & 1u);
        value >>= 1u;
    }
    return count;
}

static int valid_params(const MosimFtcParams *params) {
    return params != NULL && params->detection_threshold > 0.0 &&
           params->detection_threshold < 1.0 &&
           params->detection_persistence_s > 0.0 &&
           params->estimator_time_constant_s > 0.0 &&
           params->minimum_effectiveness > 0.0 &&
           params->minimum_effectiveness <= params->detection_threshold &&
           params->passive_effectiveness_margin >= params->minimum_effectiveness &&
           params->passive_effectiveness_margin <= 1.0 &&
           params->motor_command_max > params->motor_command_min &&
           params->landing_thrust >= params->motor_command_min &&
           params->landing_thrust <= params->motor_command_max;
}

void mosim_ftc_default_params(MosimFtcParams *params) {
    memset(params, 0, sizeof(*params));
    params->detection_threshold = 0.82;
    params->detection_persistence_s = 0.12;
    params->estimator_time_constant_s = 0.08;
    params->minimum_effectiveness = 0.25;
    params->passive_effectiveness_margin = 0.85;
    params->motor_command_min = 0.0;
    params->motor_command_max = 1.0;
    params->landing_thrust = 0.42;
    params->minimum_detection_command = 0.05;
}

void mosim_ftc_reset(MosimFtcState *state) {
    int rotor;
    memset(state, 0, sizeof(*state));
    for (rotor = 0; rotor < 4; ++rotor) state->effectiveness_estimate[rotor] = 1.0;
}

static void mix_wrench(const double wrench[4], double motor[4]) {
    const double thrust = wrench[0];
    const double roll = wrench[1];
    const double pitch = wrench[2];
    const double yaw = wrench[3];
    motor[0] = 0.25 * thrust - 0.5 * roll + 0.5 * pitch + 0.25 * yaw;
    motor[1] = 0.25 * thrust + 0.5 * roll + 0.5 * pitch - 0.25 * yaw;
    motor[2] = 0.25 * thrust + 0.5 * roll - 0.5 * pitch + 0.25 * yaw;
    motor[3] = 0.25 * thrust - 0.5 * roll - 0.5 * pitch - 0.25 * yaw;
}

static void reconstruct_wrench(const double motor[4], const double eta[4],
                               double wrench[4]) {
    double effective[4];
    int rotor;
    for (rotor = 0; rotor < 4; ++rotor) effective[rotor] = motor[rotor] * eta[rotor];
    wrench[0] = effective[0] + effective[1] + effective[2] + effective[3];
    wrench[1] = 0.5 * (-effective[0] + effective[1] + effective[2] - effective[3]);
    wrench[2] = 0.5 * (effective[0] + effective[1] - effective[2] - effective[3]);
    wrench[3] = effective[0] - effective[1] + effective[2] - effective[3];
}

static void update_fdi(const MosimFtcParams *params, MosimFtcState *state,
                       const MosimFtcInput *input, const double nominal[4]) {
    const double alpha = clamp_value(input->dt / params->estimator_time_constant_s, 0.0, 1.0);
    int rotor;
    for (rotor = 0; rotor < 4; ++rotor) {
        double observed = state->effectiveness_estimate[rotor];
        if (fabs(nominal[rotor]) >= params->minimum_detection_command) {
            observed = clamp_value(input->measured_motor_response[rotor] / nominal[rotor],
                                   0.0, 1.0);
        }
        state->residual_lpf[rotor] +=
            alpha * ((1.0 - observed) - state->residual_lpf[rotor]);
        state->effectiveness_estimate[rotor] =
            clamp_value(1.0 - state->residual_lpf[rotor],
                        params->minimum_effectiveness, 1.0);
        if (state->effectiveness_estimate[rotor] < params->detection_threshold) {
            state->fault_timer_s[rotor] += input->dt;
            if (state->fault_timer_s[rotor] >= params->detection_persistence_s)
                state->isolated_mask |= 1u << (unsigned int)rotor;
        } else {
            state->fault_timer_s[rotor] = 0.0;
        }
    }
}

static void bounded_allocation(const MosimFtcParams *params, const double nominal[4],
                               const double eta[4], double output[4], int *saturated) {
    int rotor;
    for (rotor = 0; rotor < 4; ++rotor) {
        const double compensated = nominal[rotor] /
            clamp_value(eta[rotor], params->minimum_effectiveness, 1.0);
        output[rotor] = clamp_value(compensated, params->motor_command_min,
                                    params->motor_command_max);
        if (output[rotor] != compensated) *saturated = 1;
    }
}

int mosim_ftc_step(int mode, const MosimFtcParams *params,
                   MosimFtcState *state, const MosimFtcInput *input,
                   MosimFtcOutput *output) {
    double nominal[4];
    double allocation_eta[4];
    int rotor;
    if (state == NULL || input == NULL || output == NULL || !valid_params(params) ||
        mode < MOSIM_FTC_FDI || mode > MOSIM_FTC_MULTI_FAULT_RECONFIGURATION ||
        !isfinite(input->dt) || input->dt <= 0.0 || !finite4(input->desired_wrench) ||
        !finite4(input->measured_motor_response) || !isfinite(input->altitude)) {
        if (output != NULL) { memset(output, 0, sizeof(*output)); output->status_code = -1; }
        return -1;
    }
    if (input->reset) mosim_ftc_reset(state);
    memset(output, 0, sizeof(*output));
    mix_wrench(input->desired_wrench, nominal);
    for (rotor = 0; rotor < 4; ++rotor) {
        nominal[rotor] = clamp_value(nominal[rotor], params->motor_command_min,
                                     params->motor_command_max);
        output->motor_command[rotor] = nominal[rotor];
        allocation_eta[rotor] = 1.0;
    }
    if (!input->enable) { output->status_code = 1; return 0; }

    update_fdi(params, state, input, nominal);
    output->isolated_mask = state->isolated_mask;
    output->fault_count = bit_count(state->isolated_mask);
    for (rotor = 0; rotor < 4; ++rotor) {
        output->effectiveness_estimate[rotor] = state->effectiveness_estimate[rotor];
        output->residual_norm += state->residual_lpf[rotor] * state->residual_lpf[rotor];
    }
    output->residual_norm = sqrt(output->residual_norm);

    if (mode == MOSIM_FTC_PASSIVE) {
        for (rotor = 0; rotor < 4; ++rotor)
            allocation_eta[rotor] = params->passive_effectiveness_margin;
        bounded_allocation(params, nominal, allocation_eta, output->motor_command,
                           &output->allocation_saturated);
        output->action = MOSIM_FTC_ACTION_RECONFIGURE;
    } else if ((mode == MOSIM_FTC_ACTIVE ||
                mode == MOSIM_FTC_FAULT_AWARE_ALLOCATION) && output->fault_count > 0) {
        for (rotor = 0; rotor < 4; ++rotor)
            allocation_eta[rotor] = state->effectiveness_estimate[rotor];
        bounded_allocation(params, nominal, allocation_eta, output->motor_command,
                           &output->allocation_saturated);
        output->action = MOSIM_FTC_ACTION_RECONFIGURE;
    } else if (mode == MOSIM_FTC_SINGLE_MOTOR_SAFE_LANDING && output->fault_count > 0) {
        for (rotor = 0; rotor < 4; ++rotor) {
            allocation_eta[rotor] = state->effectiveness_estimate[rotor];
            output->motor_command[rotor] = params->landing_thrust /
                (4.0 * clamp_value(allocation_eta[rotor], params->minimum_effectiveness, 1.0));
            output->motor_command[rotor] = clamp_value(output->motor_command[rotor],
                params->motor_command_min, params->motor_command_max);
        }
        output->action = input->airborne ? MOSIM_FTC_ACTION_LAND : MOSIM_FTC_ACTION_STOP;
    } else if (mode == MOSIM_FTC_MULTI_FAULT_RECONFIGURATION && output->fault_count > 0) {
        for (rotor = 0; rotor < 4; ++rotor)
            allocation_eta[rotor] = state->effectiveness_estimate[rotor];
        bounded_allocation(params, nominal, allocation_eta, output->motor_command,
                           &output->allocation_saturated);
        output->action = output->fault_count <= 2 ?
            MOSIM_FTC_ACTION_RECONFIGURE : MOSIM_FTC_ACTION_LAND;
    } else if (output->fault_count > 0) {
        output->action = MOSIM_FTC_ACTION_DETECT;
    }
    reconstruct_wrench(output->motor_command, allocation_eta, output->achieved_wrench);
    output->status_code = 1;
    return 0;
}
void MosimFaultTolerantControlStepScalar(
    double mode_id,
    double dt,
    double desired_thrust,
    double desired_roll,
    double desired_pitch,
    double desired_yaw,
    double response_1,
    double response_2,
    double response_3,
    double response_4,
    double airborne,
    double altitude,
    double enable,
    double reset,
    double *motor_command_1,
    double *motor_command_2,
    double *motor_command_3,
    double *motor_command_4,
    double *eta_hat_1,
    double *eta_hat_2,
    double *eta_hat_3,
    double *eta_hat_4,
    double *achieved_thrust,
    double *achieved_roll,
    double *achieved_pitch,
    double *achieved_yaw,
    double *residual_norm,
    double *isolated_mask,
    double *fault_count,
    double *action,
    double *allocation_saturated,
    double *status_code)
{
    static MosimFtcState states[7];
    static int initialized[7];
    MosimFtcParams params;
    MosimFtcInput input;
    MosimFtcOutput output;
    int id = (int)mode_id;
    int result;
    memset(&input, 0, sizeof(input));
    input.dt = dt;
    input.desired_wrench[0] = desired_thrust; input.desired_wrench[1] = desired_roll;
    input.desired_wrench[2] = desired_pitch; input.desired_wrench[3] = desired_yaw;
    input.measured_motor_response[0] = response_1;
    input.measured_motor_response[1] = response_2;
    input.measured_motor_response[2] = response_3;
    input.measured_motor_response[3] = response_4;
    input.airborne = airborne != 0.0; input.altitude = altitude;
    input.enable = enable != 0.0; input.reset = reset != 0.0;
    mosim_ftc_default_params(&params);
    if (id < 1 || id > 6) id = 0;
    if (!initialized[id]) { mosim_ftc_reset(&states[id]); initialized[id] = 1; }
    result = mosim_ftc_step(id, &params, &states[id], &input, &output);
    if (result != 0) { memset(&output, 0, sizeof(output)); output.status_code = result; }
    *motor_command_1 = output.motor_command[0]; *motor_command_2 = output.motor_command[1];
    *motor_command_3 = output.motor_command[2]; *motor_command_4 = output.motor_command[3];
    *eta_hat_1 = output.effectiveness_estimate[0]; *eta_hat_2 = output.effectiveness_estimate[1];
    *eta_hat_3 = output.effectiveness_estimate[2]; *eta_hat_4 = output.effectiveness_estimate[3];
    *achieved_thrust = output.achieved_wrench[0]; *achieved_roll = output.achieved_wrench[1];
    *achieved_pitch = output.achieved_wrench[2]; *achieved_yaw = output.achieved_wrench[3];
    *residual_norm = output.residual_norm; *isolated_mask = (double)output.isolated_mask;
    *fault_count = (double)output.fault_count; *action = (double)output.action;
    *allocation_saturated = (double)output.allocation_saturated;
    *status_code = (double)output.status_code;
}
");
    end func_CFunction;

    SysplorerEmbeddedCoder.Port.Inport mode_id 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport dt 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport desired_thrust 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport desired_roll 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport desired_pitch 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport desired_yaw 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport response_1 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport response_2 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport response_3 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport response_4 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport airborne 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport altitude 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport enable 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reset 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport motor_command_1 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport motor_command_2 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport motor_command_3 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport motor_command_4 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport eta_hat_1 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport eta_hat_2 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport eta_hat_3 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport eta_hat_4 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport achieved_thrust 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport achieved_roll 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport achieved_pitch 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport achieved_yaw 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport residual_norm 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport isolated_mask 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport fault_count 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport action 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport allocation_saturated 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport status_code 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
  equation
    (motor_command_1, motor_command_2, motor_command_3, motor_command_4, eta_hat_1, eta_hat_2, eta_hat_3, eta_hat_4, achieved_thrust, achieved_roll, achieved_pitch, achieved_yaw, residual_norm, isolated_mask, fault_count, action, allocation_saturated, status_code) = func_CFunction(mode_id, dt, desired_thrust, desired_roll, desired_pitch, desired_yaw, response_1, response_2, response_3, response_4, airborne, altitude, enable, reset);
  end CFunction;

equation
  connect(mode_id_in, cFunction.mode_id) annotation(Line(origin={0,0},points={{-250,250},{-50,250}},color={0,0,0}));
  connect(dt_in, cFunction.dt) annotation(Line(origin={0,0},points={{-250,244},{-50,244}},color={0,0,0}));
  connect(desired_thrust_in, cFunction.desired_thrust) annotation(Line(origin={0,0},points={{-250,238},{-50,238}},color={0,0,0}));
  connect(desired_roll_in, cFunction.desired_roll) annotation(Line(origin={0,0},points={{-250,232},{-50,232}},color={0,0,0}));
  connect(desired_pitch_in, cFunction.desired_pitch) annotation(Line(origin={0,0},points={{-250,226},{-50,226}},color={0,0,0}));
  connect(desired_yaw_in, cFunction.desired_yaw) annotation(Line(origin={0,0},points={{-250,220},{-50,220}},color={0,0,0}));
  connect(response_1_in, cFunction.response_1) annotation(Line(origin={0,0},points={{-250,214},{-50,214}},color={0,0,0}));
  connect(response_2_in, cFunction.response_2) annotation(Line(origin={0,0},points={{-250,208},{-50,208}},color={0,0,0}));
  connect(response_3_in, cFunction.response_3) annotation(Line(origin={0,0},points={{-250,202},{-50,202}},color={0,0,0}));
  connect(response_4_in, cFunction.response_4) annotation(Line(origin={0,0},points={{-250,196},{-50,196}},color={0,0,0}));
  connect(airborne_in, cFunction.airborne) annotation(Line(origin={0,0},points={{-250,190},{-50,190}},color={0,0,0}));
  connect(altitude_in, cFunction.altitude) annotation(Line(origin={0,0},points={{-250,184},{-50,184}},color={0,0,0}));
  connect(enable_in, cFunction.enable) annotation(Line(origin={0,0},points={{-250,178},{-50,178}},color={0,0,0}));
  connect(reset_in, cFunction.reset) annotation(Line(origin={0,0},points={{-250,172},{-50,172}},color={0,0,0}));
  connect(cFunction.motor_command_1, motor_command_1_out) annotation(Line(origin={0,0},points={{50,160},{250,160}},color={0,0,0}));
  connect(cFunction.motor_command_2, motor_command_2_out) annotation(Line(origin={0,0},points={{50,153},{250,153}},color={0,0,0}));
  connect(cFunction.motor_command_3, motor_command_3_out) annotation(Line(origin={0,0},points={{50,146},{250,146}},color={0,0,0}));
  connect(cFunction.motor_command_4, motor_command_4_out) annotation(Line(origin={0,0},points={{50,139},{250,139}},color={0,0,0}));
  connect(cFunction.eta_hat_1, eta_hat_1_out) annotation(Line(origin={0,0},points={{50,132},{250,132}},color={0,0,0}));
  connect(cFunction.eta_hat_2, eta_hat_2_out) annotation(Line(origin={0,0},points={{50,125},{250,125}},color={0,0,0}));
  connect(cFunction.eta_hat_3, eta_hat_3_out) annotation(Line(origin={0,0},points={{50,118},{250,118}},color={0,0,0}));
  connect(cFunction.eta_hat_4, eta_hat_4_out) annotation(Line(origin={0,0},points={{50,111},{250,111}},color={0,0,0}));
  connect(cFunction.achieved_thrust, achieved_thrust_out) annotation(Line(origin={0,0},points={{50,104},{250,104}},color={0,0,0}));
  connect(cFunction.achieved_roll, achieved_roll_out) annotation(Line(origin={0,0},points={{50,97},{250,97}},color={0,0,0}));
  connect(cFunction.achieved_pitch, achieved_pitch_out) annotation(Line(origin={0,0},points={{50,90},{250,90}},color={0,0,0}));
  connect(cFunction.achieved_yaw, achieved_yaw_out) annotation(Line(origin={0,0},points={{50,83},{250,83}},color={0,0,0}));
  connect(cFunction.residual_norm, residual_norm_out) annotation(Line(origin={0,0},points={{50,76},{250,76}},color={0,0,0}));
  connect(cFunction.isolated_mask, isolated_mask_out) annotation(Line(origin={0,0},points={{50,69},{250,69}},color={0,0,0}));
  connect(cFunction.fault_count, fault_count_out) annotation(Line(origin={0,0},points={{50,62},{250,62}},color={0,0,0}));
  connect(cFunction.action, action_out) annotation(Line(origin={0,0},points={{50,55},{250,55}},color={0,0,0}));
  connect(cFunction.allocation_saturated, allocation_saturated_out) annotation(Line(origin={0,0},points={{50,48},{250,48}},color={0,0,0}));
  connect(cFunction.status_code, status_code_out) annotation(Line(origin={0,0},points={{50,41},{250,41}},color={0,0,0}));
end MoSim_P7_FaultTolerantControl_CFunction_Sysblock;