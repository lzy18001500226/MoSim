model MoSim_PID_Unified_CFunction_Sysblock
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(modelType=Control,PortArrangement(Left(controller_id_in, setpoint_in, measurement_in, inner_measurement_in, feedforward_in, schedule_in, fuzzy_error_in, neural_residual_in, dt_in, enable_in, reset_in), Right(command_out, outer_command_out, unsaturated_command_out, integral_out, scheduled_gain_out, saturated_out, status_code_out)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0",version="26.3.0",CodeGeneration(Config = {"code_placement":{"mode":"Compact"},"code_replacement":{"standard_c_library":"C99"},"custom_code":{"code":{"function_declare":{"head":"","item_head":"","item_tail":"","tail":""},"function_define":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_declare":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_define":{"head":"","item_head":"","item_tail":"","tail":""},"include":{"head":"","item_head":"","item_tail":"","tail":""},"macro":{"head":"","item_head":"","item_tail":"","tail":""},"type":{"head":"","item_head":"","item_tail":"","tail":""}},"code_protection":{"integer_division_by_zero":false,"overflow":false}},"data_type":{"real_as_float":false},"experiment":{"task_and_sample":{"muti_task_mode":false,"whether_to_use_prefix":false}},"hardware_platform":{"largest_atomic_size":{"floating_point":"64","integer":"32"}},"identifier":{"max_length":32,"style":{"function":"camelCase","local_variable":"camelCase","macro":"camelCase","mem_var":"camelCase","type":"camelCase"}},"interface":{"function_name":{"initialize":"Init","step":"Step"}},"is_expand":{"is_expand":false},"optimization":{"array_loop_threshold":5,"logical_operator":"logical"}}, Sim_seting = {"sim_seting":{"output":"C:\\Users\\HP\\Desktop\\MoSim\\Results\\control_platform\\p1_pid_mworks_20260716\\codegen"}})),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.03,StoreEventValue
=0),Diagram(coordinateSystem(extent={{-340,-620},{340,280}},grid={2,2})));

  CFunction cFunction
    annotation (Placement(transformation(origin={0,0}, extent={{-28,-20},{28,20}})),__MWORKS(BlockSystem(SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport controller_id_in
    annotation (Placement(transformation(origin={-300,250},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport setpoint_in
    annotation (Placement(transformation(origin={-300,243},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport measurement_in
    annotation (Placement(transformation(origin={-300,236},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport inner_measurement_in
    annotation (Placement(transformation(origin={-300,229},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport feedforward_in
    annotation (Placement(transformation(origin={-300,222},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport schedule_in
    annotation (Placement(transformation(origin={-300,215},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport fuzzy_error_in
    annotation (Placement(transformation(origin={-300,208},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport neural_residual_in
    annotation (Placement(transformation(origin={-300,201},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport dt_in
    annotation (Placement(transformation(origin={-300,194},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport enable_in
    annotation (Placement(transformation(origin={-300,187},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport reset_in
    annotation (Placement(transformation(origin={-300,180},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport command_out
    annotation (Placement(transformation(origin={300,160},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport outer_command_out
    annotation (Placement(transformation(origin={300,151},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport unsaturated_command_out
    annotation (Placement(transformation(origin={300,142},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport integral_out
    annotation (Placement(transformation(origin={300,133},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport scheduled_gain_out
    annotation (Placement(transformation(origin={300,124},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport saturated_out
    annotation (Placement(transformation(origin={300,115},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport status_code_out
    annotation (Placement(transformation(origin={300,106},extent={{-8,-8},{8,8}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));

  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

  block CFunction
    annotation(__MWORKS(PortArrangement(Left(controller_id, setpoint, measurement, inner_measurement, feedforward, schedule, fuzzy_error, neural_residual, dt, enable, reset), Right(command, outer_command, unsaturated_command, integral, scheduled_gain, saturated, status_code)),PortLabels(labelType="CustomType",labels(label(text="controller_id",instance="controller_id"),label(text="setpoint",instance="setpoint"),label(text="measurement",instance="measurement"),label(text="inner_measurement",instance="inner_measurement"),label(text="feedforward",instance="feedforward"),label(text="schedule",instance="schedule"),label(text="fuzzy_error",instance="fuzzy_error"),label(text="neural_residual",instance="neural_residual"),label(text="dt",instance="dt"),label(text="enable",instance="enable"),label(text="reset",instance="reset"),label(text="command",instance="command"),label(text="outer_command",instance="outer_command"),label(text="unsaturated_command",instance="unsaturated_command"),label(text="integral",instance="integral"),label(text="scheduled_gain",instance="scheduled_gain"),label(text="saturated",instance="saturated"),label(text="status_code",instance="status_code"))),BlockSystem(blockKind=BlockKind.atomic,bltBlockKind=BltBlockKind.cfunction),independentInstance=true,sourceModel=SysplorerEmbeddedCoder.Utilities.CCaller,ExternalFunctionBlock,hide=true),
      Icon(coordinateSystem(extent={{-200,-100},{200,100}},preserveAspectRatio=false,initialScale=0.1,grid={2,2}),graphics={Rectangle(origin={0,0},fillColor={255,255,255},fillPattern=FillPattern.Solid,extent={{-200,100},{200,-100}}),Text(origin={0,0},extent={{-100,20},{100,-20}},textString="C",verticalAlignment=TextAlignment.VCenter),Text(origin={0,-120},lineColor={0,0,0},extent={{-150,20},{150,-20}},textString="%name",fontSize=14,textColor={0,0,0},verticalAlignment=TextAlignment.Top)}),
      Diagram(coordinateSystem(extent={{-100,-100},{100,100}},preserveAspectRatio=false,initialScale=0.1,grid={2,2})));

    function func_CFunction
      input SysplorerEmbeddedCoder.Types.Auto controller_id annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto setpoint annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto measurement annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto inner_measurement annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto feedforward annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto schedule annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto fuzzy_error annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto neural_residual annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto dt annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto enable annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      input SysplorerEmbeddedCoder.Types.Auto reset annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto command annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto outer_command annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto unsaturated_command annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto integral annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto scheduled_gain annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto saturated annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
      output SysplorerEmbeddedCoder.Types.Auto status_code annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));
    external "C" MosimPidUnifiedStepScalar(controller_id,setpoint,measurement,inner_measurement,feedforward,schedule,fuzzy_error,neural_residual,dt,enable,reset,command,outer_command,unsaturated_command,integral,scheduled_gain,saturated,status_code)
      annotation (Include="typedef struct {
    double kp;
    double ki;
    double kd;
    double feedforward_gain;
    double output_min;
    double output_max;
    double integral_min;
    double integral_max;
    double anti_windup_gain;
    double derivative_filter_tau;
    double schedule_gain;
    double fuzzy_gain;
    double neural_gain;
    double neural_residual_limit;
} MosimPidConfig;

typedef struct {
    double integral;
    double filtered_derivative;
    double previous_error;
    int initialized;
} MosimPidState;

typedef struct {
    double setpoint;
    double measurement;
    double feedforward;
    double schedule;
    double fuzzy_error;
    double neural_residual;
    double dt;
    int reset;
    int enable;
} MosimPidInput;

typedef struct {
    double command;
    double unsaturated_command;
    double error;
    double integral;
    double scheduled_gain;
    int saturated;
    int status_code;
} MosimPidOutput;

typedef struct {
    MosimPidState outer;
    MosimPidState inner;
} MosimCascadePidState;

typedef struct {
    double outer_reference;
    double outer_measurement;
    double inner_measurement;
    double feedforward;
    double schedule;
    double fuzzy_error;
    double neural_residual;
    double dt;
    int reset;
    int enable;
} MosimCascadePidInput;

typedef struct {
    double outer_command;
    double command;
    int saturated;
    int status_code;
} MosimCascadePidOutput;

void mosim_pid_default_config(MosimPidConfig *config);
void mosim_pid_reset(MosimPidState *state);
int mosim_pid_step(const MosimPidConfig *config, MosimPidState *state,
                   const MosimPidInput *input, MosimPidOutput *output);
int mosim_cascade_pid_step(const MosimPidConfig *outer_config,
                           const MosimPidConfig *inner_config,
                           MosimCascadePidState *state,
                           const MosimCascadePidInput *input,
                           MosimCascadePidOutput *output);




#include <math.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper)
{
    if (value < lower) return lower;
    if (value > upper) return upper;
    return value;
}

static int finite_config(const MosimPidConfig *config)
{
    const double values[] = {
        config->kp, config->ki, config->kd, config->feedforward_gain,
        config->output_min, config->output_max, config->integral_min,
        config->integral_max, config->anti_windup_gain,
        config->derivative_filter_tau, config->schedule_gain,
        config->fuzzy_gain, config->neural_gain,
        config->neural_residual_limit
    };
    size_t index;
    for (index = 0; index < sizeof(values) / sizeof(values[0]); ++index) {
        if (!isfinite(values[index])) return 0;
    }
    return config->output_min <= config->output_max &&
           config->integral_min <= config->integral_max &&
           config->derivative_filter_tau >= 0.0 &&
           config->neural_residual_limit >= 0.0;
}

static double effective_gain(const MosimPidConfig *config,
                             const MosimPidInput *input)
{
    const double residual = clamp_value(input->neural_residual,
                                        -config->neural_residual_limit,
                                        config->neural_residual_limit);
    const double fuzzy_term = tanh(input->fuzzy_error);
    const double gain = 1.0 + config->schedule_gain * input->schedule +
                        config->fuzzy_gain * fuzzy_term +
                        config->neural_gain * residual;
    return clamp_value(gain, 0.25, 4.0);
}

void mosim_pid_default_config(MosimPidConfig *config)
{
    const MosimPidConfig defaults = {
        1.0, 0.0, 0.0, 0.0, -1.0, 1.0, -1.0, 1.0, 0.2, 0.0,
        0.0, 0.0, 0.0, 0.0
    };
    if (config != NULL) *config = defaults;
}

void mosim_pid_reset(MosimPidState *state)
{
    if (state != NULL) memset(state, 0, sizeof(*state));
}

int mosim_pid_step(const MosimPidConfig *config, MosimPidState *state,
                   const MosimPidInput *input, MosimPidOutput *output)
{
    double error;
    double derivative;
    double gain;
    double unsaturated;
    double command;
    double saturation_error;
    if (config == NULL || state == NULL || input == NULL || output == NULL ||
        !finite_config(config) || !isfinite(input->setpoint) ||
        !isfinite(input->measurement) || !isfinite(input->feedforward) ||
        !isfinite(input->schedule) || !isfinite(input->fuzzy_error) ||
        !isfinite(input->neural_residual) || !isfinite(input->dt) ||
        input->dt <= 0.0) {
        if (output != NULL) memset(output, 0, sizeof(*output));
        if (output != NULL) output->status_code = -1;
        return -1;
    }
    memset(output, 0, sizeof(*output));
    if (input->reset) mosim_pid_reset(state);
    if (!input->enable) {
        output->status_code = 1;
        return 0;
    }
    error = input->setpoint - input->measurement;
    derivative = state->initialized ? (error - state->previous_error) / input->dt : 0.0;
    if (config->derivative_filter_tau > 0.0) {
        const double alpha = input->dt / (config->derivative_filter_tau + input->dt);
        state->filtered_derivative += alpha * (derivative - state->filtered_derivative);
        derivative = state->filtered_derivative;
    } else {
        state->filtered_derivative = derivative;
    }
    gain = effective_gain(config, input);
    state->integral += gain * error * input->dt;
    state->integral = clamp_value(state->integral, config->integral_min,
                                  config->integral_max);
    unsaturated = gain * config->kp * error + config->ki * state->integral +
                  gain * config->kd * derivative +
                  config->feedforward_gain * input->feedforward;
    command = clamp_value(unsaturated, config->output_min, config->output_max);
    saturation_error = command - unsaturated;
    if (config->anti_windup_gain > 0.0) {
        state->integral += config->anti_windup_gain * saturation_error * input->dt;
        state->integral = clamp_value(state->integral, config->integral_min,
                                      config->integral_max);
    }
    state->previous_error = error;
    state->initialized = 1;
    output->command = command;
    output->unsaturated_command = unsaturated;
    output->error = error;
    output->integral = state->integral;
    output->scheduled_gain = gain;
    output->saturated = fabs(command - unsaturated) > 1e-12;
    return 0;
}

int mosim_cascade_pid_step(const MosimPidConfig *outer_config,
                           const MosimPidConfig *inner_config,
                           MosimCascadePidState *state,
                           const MosimCascadePidInput *input,
                           MosimCascadePidOutput *output)
{
    MosimPidInput outer_input;
    MosimPidInput inner_input;
    MosimPidOutput outer_output;
    MosimPidOutput inner_output;
    int result;
    if (outer_config == NULL || inner_config == NULL || state == NULL ||
        input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    if (input->reset) {
        mosim_pid_reset(&state->outer);
        mosim_pid_reset(&state->inner);
    }
    outer_input.setpoint = input->outer_reference;
    outer_input.measurement = input->outer_measurement;
    outer_input.feedforward = input->feedforward;
    outer_input.schedule = input->schedule;
    outer_input.fuzzy_error = input->fuzzy_error;
    outer_input.neural_residual = input->neural_residual;
    outer_input.dt = input->dt;
    outer_input.reset = 0;
    outer_input.enable = input->enable;
    result = mosim_pid_step(outer_config, &state->outer, &outer_input, &outer_output);
    if (result != 0) { output->status_code = result; return result; }
    if (!input->enable) {
        output->status_code = outer_output.status_code;
        return 0;
    }
    inner_input = outer_input;
    inner_input.setpoint = outer_output.command;
    inner_input.measurement = input->inner_measurement;
    inner_input.reset = 0;
    result = mosim_pid_step(inner_config, &state->inner, &inner_input, &inner_output);
    if (result != 0) { output->status_code = result; return result; }
    output->outer_command = outer_output.command;
    output->command = inner_output.command;
    output->saturated = outer_output.saturated || inner_output.saturated;
    return 0;
}

static void MosimPidConfigure(int id, MosimPidConfig *outer, MosimPidConfig *inner)
{
    mosim_pid_default_config(outer);
    mosim_pid_default_config(inner);
    outer->kp = 1.2; outer->ki = 0.8; outer->kd = 0.1;
    outer->output_min = -1.0; outer->output_max = 1.0;
    outer->integral_min = -0.5; outer->integral_max = 0.5;
    outer->anti_windup_gain = 0.4; outer->derivative_filter_tau = 0.05;
    inner->kp = 1.5; inner->ki = 0.4; inner->kd = 0.05;
    inner->output_min = -1.0; inner->output_max = 1.0;
    inner->integral_min = -0.5; inner->integral_max = 0.5;
    inner->anti_windup_gain = 0.4; inner->derivative_filter_tau = 0.03;
    if (id == 2) outer->schedule_gain = 0.4;
    if (id == 3) outer->fuzzy_gain = 0.3;
    if (id == 4) { outer->neural_gain = 0.2; outer->neural_residual_limit = 0.25; }
    if (id == 5) outer->anti_windup_gain = 1.0;
    if (id == 6) outer->feedforward_gain = 0.5;
}

void MosimPidUnifiedStepScalar(
    double controller_id,
    double setpoint,
    double measurement,
    double inner_measurement,
    double feedforward,
    double schedule,
    double fuzzy_error,
    double neural_residual,
    double dt,
    double enable,
    double reset,
    double *command,
    double *outer_command,
    double *unsaturated_command,
    double *integral,
    double *scheduled_gain,
    double *saturated,
    double *status_code)
{
    static MosimPidState states[7];
    static MosimCascadePidState cascade_states[7];
    MosimPidConfig outer, inner;
    MosimPidInput input;
    MosimPidOutput output;
    MosimCascadePidInput cascade_input;
    MosimCascadePidOutput cascade_output;
    int id = (int)controller_id;
    int result;
    if (id < 1 || id > 6) id = 0;
    MosimPidConfigure(id, &outer, &inner);
    memset(&input, 0, sizeof(input));
    input.setpoint=setpoint; input.measurement=measurement;
    input.feedforward=feedforward; input.schedule=schedule;
    input.fuzzy_error=fuzzy_error; input.neural_residual=neural_residual;
    input.dt=dt; input.enable=enable != 0.0; input.reset=reset != 0.0;
    *outer_command = 0.0;
    if (id == 1) {
        memset(&cascade_input, 0, sizeof(cascade_input));
        cascade_input.outer_reference=setpoint;
        cascade_input.outer_measurement=measurement;
        cascade_input.inner_measurement=inner_measurement;
        cascade_input.feedforward=feedforward;
        cascade_input.schedule=schedule;
        cascade_input.fuzzy_error=fuzzy_error;
        cascade_input.neural_residual=neural_residual;
        cascade_input.dt=dt; cascade_input.enable=enable != 0.0;
        cascade_input.reset=reset != 0.0;
        result=mosim_cascade_pid_step(&outer,&inner,&cascade_states[id],&cascade_input,&cascade_output);
        *command=cascade_output.command; *outer_command=cascade_output.outer_command;
        *unsaturated_command=cascade_output.command; *integral=cascade_states[id].inner.integral;
        *scheduled_gain=1.0; *saturated=(double)cascade_output.saturated;
        *status_code=(double)(result != 0 ? result : cascade_output.status_code);
        return;
    }
    result=mosim_pid_step(&outer,&states[id],&input,&output);
    *command=output.command; *unsaturated_command=output.unsaturated_command;
    *integral=output.integral; *scheduled_gain=output.scheduled_gain;
    *saturated=(double)output.saturated;
    *status_code=(double)(result != 0 ? result : output.status_code);
}
");
    end func_CFunction;

    SysplorerEmbeddedCoder.Port.Inport controller_id
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport setpoint
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport measurement
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport inner_measurement
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport feedforward
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport schedule
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport fuzzy_error
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport neural_residual
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport dt
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport enable
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport reset
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport command
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport outer_command
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport unsaturated_command
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport integral
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport scheduled_gain
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport saturated
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Outport status_code
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));
  equation
    (command, outer_command, unsaturated_command, integral, scheduled_gain, saturated, status_code) = func_CFunction(controller_id, setpoint, measurement, inner_measurement, feedforward, schedule, fuzzy_error, neural_residual, dt, enable, reset);
  end CFunction;

equation
  connect(controller_id_in, cFunction.controller_id) annotation(Line(origin={0,0},points={{-250,250},{-50,250}},color={0,0,0}));
  connect(setpoint_in, cFunction.setpoint) annotation(Line(origin={0,0},points={{-250,244},{-50,244}},color={0,0,0}));
  connect(measurement_in, cFunction.measurement) annotation(Line(origin={0,0},points={{-250,238},{-50,238}},color={0,0,0}));
  connect(inner_measurement_in, cFunction.inner_measurement) annotation(Line(origin={0,0},points={{-250,232},{-50,232}},color={0,0,0}));
  connect(feedforward_in, cFunction.feedforward) annotation(Line(origin={0,0},points={{-250,226},{-50,226}},color={0,0,0}));
  connect(schedule_in, cFunction.schedule) annotation(Line(origin={0,0},points={{-250,220},{-50,220}},color={0,0,0}));
  connect(fuzzy_error_in, cFunction.fuzzy_error) annotation(Line(origin={0,0},points={{-250,214},{-50,214}},color={0,0,0}));
  connect(neural_residual_in, cFunction.neural_residual) annotation(Line(origin={0,0},points={{-250,208},{-50,208}},color={0,0,0}));
  connect(dt_in, cFunction.dt) annotation(Line(origin={0,0},points={{-250,202},{-50,202}},color={0,0,0}));
  connect(enable_in, cFunction.enable) annotation(Line(origin={0,0},points={{-250,196},{-50,196}},color={0,0,0}));
  connect(reset_in, cFunction.reset) annotation(Line(origin={0,0},points={{-250,190},{-50,190}},color={0,0,0}));
  connect(cFunction.command, command_out) annotation(Line(origin={0,0},points={{50,160},{250,160}},color={0,0,0}));
  connect(cFunction.outer_command, outer_command_out) annotation(Line(origin={0,0},points={{50,153},{250,153}},color={0,0,0}));
  connect(cFunction.unsaturated_command, unsaturated_command_out) annotation(Line(origin={0,0},points={{50,146},{250,146}},color={0,0,0}));
  connect(cFunction.integral, integral_out) annotation(Line(origin={0,0},points={{50,139},{250,139}},color={0,0,0}));
  connect(cFunction.scheduled_gain, scheduled_gain_out) annotation(Line(origin={0,0},points={{50,132},{250,132}},color={0,0,0}));
  connect(cFunction.saturated, saturated_out) annotation(Line(origin={0,0},points={{50,125},{250,125}},color={0,0,0}));
  connect(cFunction.status_code, status_code_out) annotation(Line(origin={0,0},points={{50,118},{250,118}},color={0,0,0}));
end MoSim_PID_Unified_CFunction_Sysblock;
