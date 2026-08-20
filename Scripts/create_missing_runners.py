#!/usr/bin/env python3
"""
批量生成27个缺失的GraphicalRunner文件
"""
from pathlib import Path
import json

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
CATALOG_PATH = BASE_DIR / 'Config/control_platform/control_scheme_catalog.json'

def to_pkg(sid):
    special = {
        'pid': 'Pid', 'lqr': 'Lqr', 'lqi': 'Lqi', 'lqg': 'Lqg',
        'h2': 'H2', 'hinf': 'Hinf', 'mrac': 'Mrac', 'ndi': 'Ndi',
        'smc': 'Smc', 'mpc': 'Mpc', 'ilqr': 'Ilqr', 'mppi': 'Mppi',
        'nmpc': 'Nmpc', 'se3': 'Se3', 'dfbc': 'Dfbc', 'rl': 'Rl',
        'fopid': 'Fopid', 'awff': 'Awff', 'cbf': 'Cbf', 'eso': 'Eso',
        'fuzzy': 'Fuzzy', 'neural': 'Neural', 'explicit': 'Explicit',
        'feedback': 'Feedback', 'linearization': 'Linearization',
        'gain': 'Gain', 'scheduled': 'Scheduled', 'super': 'Super',
        'twisting': 'Twisting', 'robust': 'Robust', 'smooth': 'Smooth',
        'bodyrate': 'Bodyrate', 'scheduler': 'Scheduler', 'official': 'Official',
        'hover': 'Hover', 'wrench': 'Wrench', 'cascade': 'Cascade',
        'adaptive': 'Adaptive', 'backstepping': 'Backstepping', 'baseline': 'Baseline',
        'high': 'High', 'order': 'Order', 'attitude': 'Attitude',
        'state': 'State', 'output': 'Output', 'rate': 'Rate',
        'integral': 'Integral', 'boundary': 'Boundary', 'layer': 'Layer',
        'linear': 'Linear', 'trained': 'Trained', 'residual': 'Residual',
        'fixed': 'Fixed', 'basic': 'Basic', 'outer': 'Outer',
        'terminal': 'Terminal', 'nonsingular': 'Nonsingular', 'passivity': 'Passivity',
        'based': 'Based', 'control': 'Control', 'placement': 'Placement',
        'luenberger': 'Luenberger', 'pole': 'Pole', 'tube': 'Tube',
        'qp': 'Qp', 'l1': 'L1', 'indi': 'Indi',
    }
    parts = sid.split('_')
    return ''.join([special.get(p, p.capitalize()) for p in parts])

# Load catalog
data = json.load(open(CATALOG_PATH, encoding='utf-8'))
schemes = {s['scheme_id']: s for s in data['schemes']}

# Find all missing runners
missing_runners = []
for sid, scheme in schemes.items():
    if 'implementation_package' not in scheme:
        continue
    family = scheme['implementation_package']
    pkg = to_pkg(sid)
    runner_path = BASE_DIR / f'Models/MoSimQuadrotorModel/Experiment/{family}/{pkg}GraphicalRunner.mo'

    if not runner_path.exists():
        missing_runners.append((sid, family, pkg))

print(f"发现{len(missing_runners)}个缺失的GraphicalRunner")
print()

# Generate each runner
for sid, family, pkg in missing_runners:
    target_dir = BASE_DIR / f'Models/MoSimQuadrotorModel/Experiment/{family}'
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f'{pkg}GraphicalRunner.mo'

    content = f'''within MoSimQuadrotorModel.Experiment.{family};
model {pkg}GraphicalRunner
  "{sid} graphical Sysblock review runner with the common aircraft template"

  parameter Real gust_force[3](each unit = "N") = {{0, 0, 0}};
  parameter Real gust_start_s(unit = "s") = 0;
  parameter Real gust_duration_s(unit = "s") = 0;
  parameter Real mass_scale(min = 0.01) = 1;
  parameter Real inertia_scale[3](each min = 0.01) = {{1, 1, 1}};
  parameter Real rotor_effectiveness[4](each min = 0, each max = 1) = {{1, 1, 1, 1}};
  parameter Real fault_start_s(unit = "s") = 1e9;
  parameter Integer fault_rotor_index(min = 1, max = 4) = 1;
  parameter Real fault_rotor_effectiveness(min = 0, max = 1) = 1;
  parameter Real nominal_esc_limit_abs(unit = "rad/s", min = 0) = 110;
  parameter Integer scenario_mode(min = 0, max = 4) = 0;
  Modelica.Blocks.Sources.Constant zero(k = 0)
    annotation(Placement(transformation(origin = {{-470, -180}}, extent = {{{{-16, -16}}, {{16, 16}}}})));
  Modelica.Blocks.Sources.Constant dt(k = 0.01)
    annotation(Placement(transformation(origin = {{-470, -220}}, extent = {{{{-16, -16}}, {{16, 16}}}})));
  Modelica.Blocks.Sources.Constant enable(k = 1)
    annotation(Placement(transformation(origin = {{-470, -260}}, extent = {{{{-16, -16}}, {{16, 16}}}})));
  MoSimQuadrotorModel.Guidance.Trajectories.MultiModeTrajectory reference(scenario_mode = scenario_mode)
    annotation(Placement(transformation(origin = {{-380, 185}}, extent = {{{{-50, -65}}, {{50, 65}}}})));
  MoSimQuadrotorModel.Control.{family}.{pkg}.{pkg}Core core
    annotation(Placement(transformation(origin = {{-65, 185}}, extent = {{{{-80, -65}}, {{80, 65}}}})), __MWORKS(SECInstance = true));
  MoSimQuadrotorModel.Experiment.Adapters.GraphicalScalarRotorPreview output_adapter
    annotation(Placement(transformation(origin = {{108, 185}}, extent = {{{{-50, -50}}, {{50, 50}}}})));
  MoSimQuadrotorModel.Experiment.Baselines.ScheduledRotorEfficiencyCompensator fault_compensator(
    rotor_effectiveness = rotor_effectiveness, fault_start_s = fault_start_s,
    fault_rotor_index = fault_rotor_index, fault_rotor_effectiveness = fault_rotor_effectiveness)
    annotation(Placement(transformation(origin = {{320, 5}}, extent = {{{{-50, -50}}, {{50, 50}}}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.ESCDrive esc(motor_limit_abs = nominal_esc_limit_abs)
    annotation(Placement(transformation(origin = {{190, 5}}, extent = {{{{-50, -50}}, {{50, 50}}}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.BatteryPower battery(voltage_drop_per_second = 0)
    annotation(Placement(transformation(origin = {{55, 5}}, extent = {{{{-50, -50}}, {{50, 50}}}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor1(channel_index = 1)
    annotation(Placement(transformation(origin = {{465, 220}}, extent = {{{{-28.75, -30}}, {{28.75, 30}}}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor2(channel_index = 2)
    annotation(Placement(transformation(origin = {{465, 142}}, extent = {{{{-28.75, -30}}, {{28.75, 30}}}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor3(channel_index = 3)
    annotation(Placement(transformation(origin = {{465, 64}}, extent = {{{{-28.75, -30}}, {{28.75, 30}}}})));
  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor4(channel_index = 4)
    annotation(Placement(transformation(origin = {{465, -14}}, extent = {{{{-28.75, -30}}, {{28.75, 30}}}})));
  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant(
    rotor_effectiveness = rotor_effectiveness, gust_force = gust_force,
    gust_start_s = gust_start_s, gust_duration_s = gust_duration_s,
    mass_scale = mass_scale, inertia_scale = inertia_scale,
    fault_start_s = fault_start_s, fault_rotor_index = fault_rotor_index,
    fault_rotor_effectiveness = fault_rotor_effectiveness)
    annotation(Placement(transformation(origin = {{650, 100}}, extent = {{{{-127.5, -147.5}}, {{127.5, 147.5}}}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.PerceptionInterface perception
    annotation(Placement(transformation(origin = {{-380, 5}}, extent = {{{{-50, -50}}, {{50, 50}}}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.FlightController flight_controller
    annotation(Placement(transformation(origin = {{-95, 5}}, extent = {{{{-50, -50}}, {{50, 50}}}})));
  MoSimQuadrotorModel.Vehicle.BaseModules.MissionComputer mission_computer
    annotation(Placement(transformation(origin = {{-235, 5}}, extent = {{{{-50, -50}}, {{50, 50}}}})));

  Real position_ref[3];
  Real position[3];
  Real attitude[3];
  Real rotor_command[4];
  Real esc_motor_command[4];
  Real rotor_speed[4];
  Real esc_health[4];
  Real esc_saturation_ratio;
  Real mission_reference_position[3];
  Real position_error_norm;

equation
  connect(core.command, output_adapter.command) annotation(Line(points={{{{-440,240}},{{-120,258}}}}, color={{0,0,127}}));
  connect(output_adapter.rotor_command[1], fault_compensator.command_in[1]) annotation(Line(points={{{{-440,226}},{{-120,244}}}}, color={{0,0,127}}));
  connect(output_adapter.rotor_command[2], fault_compensator.command_in[2]) annotation(Line(points={{{{-440,212}},{{-120,230}}}}, color={{0,0,127}}));
  connect(output_adapter.rotor_command[3], fault_compensator.command_in[3]) annotation(Line(points={{{{-440,198}},{{-120,216}}}}, color={{0,0,127}}));
  connect(output_adapter.rotor_command[4], fault_compensator.command_in[4]) annotation(Line(points={{{{-440,184}},{{-120,202}}}}, color={{0,0,127}}));
  connect(fault_compensator.command_out[1], esc.motor_command_raw[1]) annotation(Line(points={{{{-440,170}},{{-120,188}}}}, color={{0,0,127}}));
  connect(fault_compensator.command_out[2], esc.motor_command_raw[2]) annotation(Line(points={{{{-440,156}},{{-120,174}}}}, color={{0,0,127}}));
  connect(fault_compensator.command_out[3], esc.motor_command_raw[3]) annotation(Line(points={{{{-440,142}},{{-120,160}}}}, color={{0,0,127}}));
  connect(fault_compensator.command_out[4], esc.motor_command_raw[4]) annotation(Line(points={{{{-440,128}},{{-120,146}}}}, color={{0,0,127}}));
  connect(esc.motor_command[1], motor1.command) annotation(Line(points={{{{-440,114}},{{-120,132}}}}, color={{0,0,127}}));
  connect(esc.motor_command[2], motor2.command) annotation(Line(points={{{{-440,100}},{{-120,118}}}}, color={{0,0,127}}));
  connect(esc.motor_command[3], motor3.command) annotation(Line(points={{{{-440,86}},{{-120,104}}}}, color={{0,0,127}}));
  connect(esc.motor_command[4], motor4.command) annotation(Line(points={{{{-440,72}},{{-120,90}}}}, color={{0,0,127}}));
  connect(motor1.command_to_plant, plant.rotor_command[1]) annotation(Line(points={{{{-440,58}},{{-120,76}}}}, color={{0,0,127}}));
  connect(motor2.command_to_plant, plant.rotor_command[2]) annotation(Line(points={{{{-440,44}},{{-120,62}}}}, color={{0,0,127}}));
  connect(motor3.command_to_plant, plant.rotor_command[3]) annotation(Line(points={{{{-440,30}},{{-120,48}}}}, color={{0,0,127}}));
  connect(motor4.command_to_plant, plant.rotor_command[4]) annotation(Line(points={{{{-440,16}},{{-120,34}}}}, color={{0,0,127}}));
  connect(plant.rotor_speed[1], motor1.speed) annotation(Line(points={{{{-440,2}},{{-120,20}}}}, color={{0,0,127}}));
  connect(plant.rotor_speed[2], motor2.speed) annotation(Line(points={{{{-440,-12}},{{-120,6}}}}, color={{0,0,127}}));
  connect(plant.rotor_speed[3], motor3.speed) annotation(Line(points={{{{-440,-26}},{{-120,-8}}}}, color={{0,0,127}}));
  connect(plant.rotor_speed[4], motor4.speed) annotation(Line(points={{{{-440,-40}},{{-120,-22}}}}, color={{0,0,127}}));
  connect(battery.bus_voltage, esc.bus_voltage) annotation(Line(points={{{{-440,-54}},{{-120,-36}}}}, color={{0,0,127}}));
  connect(battery.power_ok, esc.power_ok) annotation(Line(points={{{{-440,-68}},{{-120,-50}}}}, color={{0,0,127}}));
  connect(plant.position, perception.position_raw) annotation(Line(points={{{{-440,-82}},{{-120,-64}}}}, color={{0,0,127}}));
  connect(perception.gps_position, flight_controller.gps_position) annotation(Line(points={{{{-440,-96}},{{-120,-78}}}}, color={{0,0,127}}));
  connect(perception.gps_valid, flight_controller.gps_valid) annotation(Line(points={{{{-440,-110}},{{-120,-92}}}}, color={{0,0,127}}));
  connect(plant.attitude, flight_controller.attitude_raw) annotation(Line(points={{{{-440,-124}},{{-120,-106}}}}, color={{0,0,127}}));
  connect(plant.rotor_speed, flight_controller.motor_speed_raw) annotation(Line(points={{{{-440,-138}},{{-120,-120}}}}, color={{0,0,127}}));
  connect(perception.local_position, mission_computer.local_position) annotation(Line(points={{{{-440,-152}},{{-120,-134}}}}, color={{0,0,127}}));
  connect(flight_controller.position_est, mission_computer.aircraft_position) annotation(Line(points={{{{-440,-166}},{{-120,-148}}}}, color={{0,0,127}}));
  connect(perception.obstacle_margin, mission_computer.obstacle_margin) annotation(Line(points={{{{-440,-180}},{{-120,-162}}}}, color={{0,0,127}}));
  connect(flight_controller.estimator_quality, mission_computer.estimator_quality) annotation(Line(points={{{{-440,-194}},{{-120,-176}}}}, color={{0,0,127}}));

  position_ref = reference.position_command;
  position = plant.position;
  attitude = plant.attitude;
  rotor_command = output_adapter.rotor_command;
  esc_motor_command = esc.motor_command;
  rotor_speed[1] = motor1.speed_telemetry;
  rotor_speed[2] = motor2.speed_telemetry;
  rotor_speed[3] = motor3.speed_telemetry;
  rotor_speed[4] = motor4.speed_telemetry;
  esc_health = esc.esc_health;
  esc_saturation_ratio = esc.saturation_ratio_est;
  mission_reference_position = mission_computer.reference_position;
  position_error_norm = sqrt((position_ref[1] - position[1])^2 + (position_ref[2] - position[2])^2 + (position_ref[3] - position[3])^2);

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Interval = 0.01),
    Diagram(coordinateSystem(extent = {{{{-520, -400}}, {{830, 300}}}}, grid = {{2, 2}})),
    __MWORKS(version = "26.3.0"));
end {pkg}GraphicalRunner;
'''

    target_path.write_text(content, encoding='utf-8')
    print(f"[OK] {sid:35s} -> {family}/{pkg}GraphicalRunner.mo")

print()
print(f"已生成{len(missing_runners)}个GraphicalRunner文件")
