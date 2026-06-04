# Quadrotor Parameter Identification Workflow

> PX4 ULog based workflow for correcting Sunray150 / MWORKS quadrotor
> dynamics parameters. This is an executable project procedure, not a claim
> that current parameters have already been identified from real flight data.

---

## 1. Goal And Evidence Boundary

Use PX4 flight logs to identify or validate the Sunray150 airframe parameters
used by `QuadrotorModel.Mechanics.QuadChassis` and project experiments.

Primary target:

```text
PX4 ULog
  -> ARPL / sysid.tools identification
  -> Sunray150 parameter YAML
  -> MWORKS field mapping
  -> short hover / trajectory verification
  -> report-ready parameter evidence
```

Evidence labels:

| Source | Meaning |
|---|---|
| `source=PX4_ULog_sysid` | Parameters estimated from real or bench PX4 ULog data |
| `source=reference_repo` | Parameter structure or sample values copied from a reference repository |
| `source=SDF_migration` | Parameters migrated from Gazebo/PX4 SDF files |
| `source=MWORKS_MCP` | MWORKS model check/simulation evidence after parameters are applied |

Do not describe a parameter set as Sunray150 identified truth until the matching
ULog files, identification config, output YAML, and MWORKS verification result
are all saved in the project evidence bundle.

---

## 2. Main Line: ARPL / sysid.tools

Use ARPL / `sysid.tools` as the main identification route because it is built
around PX4 logs and vehicle dynamics parameter estimation. The exact command
depends on the installed tool version, so record the command and tool commit or
release in the output bundle.

Recommended execution pattern:

```text
1. Export raw PX4 `.ulg` logs from the Sunray150 flight controller.
2. Verify required topics and time spans.
3. Convert or load logs through ARPL / sysid.tools.
4. Select valid identification windows.
5. Estimate mass, inertia, rotor thrust/moment constants, motor lag, and drag.
6. Save output as project YAML plus a fit report.
7. Apply the YAML to the MWORKS mapping table in this workflow.
8. Run the smallest MWORKS hover check, then one trajectory check.
```

Minimum output location:

```text
Results/identification/sunray150/<date_or_run_id>/
  raw/
    *.ulg
  processed/
    selected_windows.csv
    converted_log.csv
  metrics/
    fit_report.json
    residual_summary.json
  parameters/
    sunray150_identified.yaml
  logs/
    sysid_command.txt
    mworks_check.jsonl
```

---

## 3. Auxiliary Line: ETH data-driven-dynamics

The local reference `References/Data/data-driven-dynamics/` is an auxiliary
route for parameter structure, ULog topic expectations, and cross-checking. Do
not modify the reference repository.

Useful reference files:

| File | Use |
|---|---|
| `References/Data/data-driven-dynamics/README.md` | Pipeline concept, `estimate-model`, `predict-model`, and result YAML behavior |
| `References/Data/data-driven-dynamics/Tools/parametric_model/configs/quadrotor_model.yaml` | Required ULog topics, rotor layout, optimizer bounds, sample parameter names |
| `References/Data/data-driven-dynamics/resources/quadrotor_model.csv` | Example flattened CSV column names |

Reference command shape from the README:

```bash
make estimate-model model=quadrotor_model log=resources/quadrotor_model.ulg
make predict-model model=quadrotor_model log=<validation_log> model_results=<yaml>
```

Use this line to answer:

```text
Are the ULog fields complete?
Are rotor order and body-frame signs consistent?
Are fitted coefficients within physically plausible bounds?
Does a held-out log predict acceleration and angular acceleration better than the SDF baseline?
```

---

## 4. Required PX4 ULog Fields

Required core topics and fields:

| PX4 topic | Required fields | Project dataframe fields |
|---|---|---|
| `actuator_outputs` | `timestamp`, `output[0..3]` | `timestamp`, `u0`, `u1`, `u2`, `u3` |
| `vehicle_local_position` | `timestamp`, `vx`, `vy`, `vz` | `vx`, `vy`, `vz` |
| `vehicle_attitude` | `timestamp`, `q[0..3]` | `q0`, `q1`, `q2`, `q3` |
| `vehicle_angular_velocity` | `timestamp`, `xyz[0..2]` | `ang_vel_x`, `ang_vel_y`, `ang_vel_z` |
| `sensor_combined` | `timestamp`, `accelerometer_m_s2[0..2]`, `gyro_rad[0..2]` | `acc_b_x`, `acc_b_y`, `acc_b_z`, angular-rate or angular-acceleration input depending on tool preprocessing |
| `vehicle_land_detected` | `timestamp`, `landed` | `landed` |

Recommended extra topics:

| PX4 topic | Why |
|---|---|
| `actuator_controls_0` or equivalent control allocation output | Helps separate controller command from motor output |
| `battery_status` | Detect voltage sag and reject low-power windows |
| `vehicle_status` | Remove arming, failsafe, and mode-transition windows |
| `manual_control_setpoint` / `trajectory_setpoint` | Select excitation windows and reproduce test intent |
| `vehicle_acceleration` if available | Cross-check accelerometer processing |
| ESC RPM/telemetry if available | Identify motor constant against speed instead of PWM only |

Data quality gates:

1. Remove `landed=true`, arming transitions, takeoff touchdown transients unless
   the test specifically identifies ground effects.
2. Keep clocks monotonic after resampling.
3. Reject windows with motor saturation, failsafe, battery warning, or estimator
   resets unless they are explicitly modeled.
4. Record whether `u0..u3` are PWM, normalized command, or RPM-derived values.

---

## 5. Excitation Flights

Collect at least three classes of excitation logs. Use a safety pilot and local
flight-test rules; this document only defines the data needed by the model.

| Flight class | Purpose | Suggested maneuver |
|---|---|---|
| Hover / step throttle | Mass, hover thrust, motor lag, voltage sensitivity | Stable hover, small altitude steps, gentle collective pulses |
| Attitude chirp / rate excitation | Inertia, torque constants, cross-axis coupling | Small roll/pitch/yaw rate chirps or PRBS around hover |
| Translational trajectory / drag excitation | Fuselage drag and velocity-dependent terms | Slow figure-eight, forward/backward passes, lateral passes at multiple speeds |

Minimum split:

```text
identification set: 60-70% of valid windows
validation set:     30-40% of valid windows, from different flights when possible
```

Do not tune the MWORKS controller against the same windows used to claim
parameter identification quality. Keep one held-out validation log.

---

## 6. Output YAML Format

Save identified parameters in a project-owned YAML file with provenance and
units. Example:

```yaml
vehicle_profile: sunray150_mid360
source: PX4_ULog_sysid
tool:
  name: arpl_sysid_tools
  version: "<record version or commit>"
data:
  logs:
    - Results/identification/sunray150/2026xxxx/raw/hover_01.ulg
    - Results/identification/sunray150/2026xxxx/raw/chirp_01.ulg
    - Results/identification/sunray150/2026xxxx/raw/figure8_01.ulg
  selected_windows: Results/identification/sunray150/2026xxxx/processed/selected_windows.csv
  actuator_signal: pwm_or_normalized_or_rpm
frame:
  body_frame: FRD
  world_frame: NED_or_ENU_recorded
  mworks_frame_conversion: documented_in_mapping
parameters:
  mass_kg: 1.0
  inertia_kg_m2:
    Ixx: 0.0085
    Iyy: 0.0085
    Izz: 0.012
    Ixy: 0.0
    Ixz: 0.0
    Iyz: 0.0
  rotor_positions_m:
    - [0.065, -0.065, -0.025]
    - [-0.065, 0.065, -0.025]
    - [0.065, 0.065, -0.025]
    - [-0.065, -0.065, -0.025]
  rotor_directions:
    - cw
    - cw
    - ccw
    - ccw
  thrust_coefficient_n_per_rad_s2: 8.54858e-06
  moment_coefficient_nm_per_rad_s2: null
  thrust_to_moment_ratio_m: null
  motor_time_constant_s: null
  fuselage_drag:
    c_d_x: null
    c_d_y: null
    c_d_z: null
validation:
  fit_report: Results/identification/sunray150/2026xxxx/metrics/fit_report.json
  mworks_check: Results/identification/sunray150/2026xxxx/logs/mworks_check.jsonl
notes:
  - "Numeric values above are placeholders or SDF migration seeds until ULog identification is complete."
```

Keep nulls when a parameter is not identified. Do not fill unknown values from
unrelated vehicles just to complete the table.

---

## 7. Mapping To MWORKS Fields

Apply parameters to project-owned model variants or documented component
modifiers. Do not silently overwrite the official baseline.

| Identified YAML field | MWORKS target | Notes |
|---|---|---|
| `mass_kg` | `QuadChassis.body.m` or wrapper modifier `quadChassisTest17_1(body(m=...))` | Current Sunray migration seed is `1.0 kg`; mass-disturbance scenarios may intentionally override this. |
| `inertia_kg_m2.Ixx/Iyy/Izz` | `QuadChassis.body.I_11/I_22/I_33` or equivalent body inertia fields after model inspection | Verify exact field names through MCP/model text before editing. |
| `rotor_positions_m` | rotor/propeller placements inside `QuadChassis` | Must preserve motor order and sign convention before changing control allocation. |
| `rotor_directions` | yaw torque sign and allocation matrix direction signs | Confirm against current project order and MWORKS positive torque convention. |
| `thrust_coefficient_n_per_rad_s2` | `lift_cofficient` / rotor gain fields, currently represented by `gain2..gain5(k=...)` overrides in some experiments | MWORKS may use a visualized shaft speed scaled by `rotorVelocitySlowdownSim`; document the conversion. |
| `moment_coefficient_nm_per_rad_s2` or `thrust_to_moment_ratio_m` | yaw moment coefficient or allocation ratio `c = k_m / k_f` | Needed for INDI/fault allocation yaw authority. |
| `motor_time_constant_s` | actuator lag block or controller-side motor model | Add only where the model has an explicit actuator dynamic block. |
| `fuselage_drag` | disturbance/aerodynamic drag block or future wrapper | Current plant may not expose this directly; keep as wrapper-level correction if needed. |

Current known Sunray/MWORKS seed values:

| Parameter | Current seed | Source/risk |
|---|---:|---|
| mass | `1.0 kg` | SDF migration seed, not ULog-identified |
| inertia | `Ixx=0.0085`, `Iyy=0.0085`, `Izz=0.012` | SDF migration seed, payload/battery sensitive |
| rotor arm location | approximately `(±0.065, ±0.065, -0.025) m` | SDF migration seed, verify motor order |
| SDF motor constant | `8.54858e-06 N/(rad/s)^2` | Physical rotor-speed coefficient from Sunray SDF |
| MWORKS lift coefficient seed | `0.000854858` | Converted by `rotorVelocitySlowdownSim=10`; high risk if shaft-speed convention changes |
| experiment rotor-loss overrides | `0.0007266293` in selected loss cases | Scenario-specific degraded coefficient, not nominal truth |

Before editing a model, inspect:

```bash
rg -n "QuadChassis|lift_cofficient|gain[2-5]\\(k|body\\(m|I_11|I_22|I_33" models QuadrotorModel
```

Then verify with Sysplorer MCP:

```text
model_manager(load_file/open)
  -> model_manager(get_model_text or lookup_component)
  -> check_model
  -> smallest hover simulation
```

---

## 8. Current SDF / iris Parameter Risks

The ETH sample config and classic PX4 `iris` values are useful references, but
they are not Sunray150 truth.

Risks to track:

1. `iris` mass/inertia/rotor positions differ from Sunray150 with Mid360 and
   project battery/payload configuration.
2. PX4/Gazebo motor constants may include simulation-only scaling such as
   `rotorVelocitySlowdownSim`; MWORKS coefficient conversion must match the
   actual speed signal used by the lift model.
3. ULog actuator outputs may be PWM/normalized commands instead of rotor speed,
   so the fitted thrust coefficient can absorb ESC/motor mapping unless RPM or
   a calibrated command-to-speed model is available.
4. FRD/NED conventions in PX4 logs must be converted before comparing to the
   project's MWORKS/world-frame convention.
5. Added Mid360, battery, propeller guards, or mounting hardware changes mass
   and inertia; update the profile name when hardware changes.
6. Drag coefficients identified in outdoor logs include wind and estimator
   bias unless wind is measured or the selected windows are calm.

### 8.1 Suspect Parameters And Identification Route

Current priority is not only to list missing data, but to turn available PX4
logs into usable MWORKS parameters. Use this table as the working plan:

| Parameter | Why current value is suspect | Minimum data route | Preferred method | MWORKS update target |
|---|---|---|---|---|
| `mass_kg` | Current `1.0 kg` is an SDF migration seed; Sunray150 laser version public mass is about `1.08 kg`, and battery/Mid360/guard changes matter | Direct weighing of the exact flight configuration; hover ULog for sanity | Weighing first, then hover-thrust consistency check from `hover_thrust_estimate`, acceleration, battery voltage | `QuadChassis.body.m` or wrapper modifier |
| `inertia_kg_m2` | Current `Ixx/Iyy/Izz` are SDF seeds and very sensitive to battery, Mid360, payload, frame, and prop guards | PX4 ULog attitude/rate excitation with `vehicle_angular_velocity`, attitude, actuator outputs | ARPL `data-driven-system-identification` / nonlinear least squares on angular dynamics; validate on held-out rate maneuvers | `body.I_11/I_22/I_33` or equivalent body inertia fields |
| `rotor_positions_m` | Current arm values come from model geometry and may not match actual motor-axis-to-CG after payload shift | Frame measurement plus motor order / rotor direction | Manual geometry measurement; cross-check yaw/roll/pitch signs in PX4 logs | rotor placement and allocation matrix |
| `rotor_directions` / motor order | Wrong order/sign can make fault isolation and allocation look valid only by accident | PX4 actuator ordering, mixer/control allocation output, motor spin direction | Vendor/PX4 airframe config plus small motor command sanity test | yaw torque signs and fault allocation mapping |
| `thrust_coefficient` / `lift_cofficient` | Current `0.000854858` is converted from SDF `8.54858e-06` using `rotorVelocitySlowdownSim=10`; it depends on whether MWORKS signal is visual shaft speed or physical rotor speed | Hover ULog plus mass; better with ESC RPM or thrust stand | If RPM exists: fit `T=k_f*omega^2`. If only normalized actuator command: fit command-to-thrust map and keep source label `command_model` | `lift_cofficient`, rotor gains, or wrapper thrust map |
| `moment_coefficient` / yaw torque | Usually copied from PX4/Gazebo and hard to infer from position tracking alone | Yaw-rate excitation ULog, motor commands, preferably RPM | Fit angular z dynamics jointly with inertia and thrust/yaw coefficient ratio | yaw allocation / mixer coefficient |
| `motor_time_constant_s` | Current model may omit or simplify actuator lag; affects aggressive and fault scenarios | Motor command step/chirp logs; ESC RPM if available | First-order lag fit from command to RPM; without RPM fit closed-loop residual only and mark low confidence | actuator lag block or controller-side motor model |
| `fuselage_drag` | Current plant likely lacks identified drag; outdoor logs mix drag with wind | calm translational passes in x/y, local velocity, acceleration, attitude, wind note | data-driven-dynamics residual force fit; validate on independent figure-eight/forward-back passes | wrapper-level drag/disturbance block |
| `sensor_noise` / delay | Sensor noise/delay affects planner/control robustness but current values may be arbitrary | stationary logs and flight logs from PX4 estimators/sensors | estimate variance, latency, and dropout rates from logs; keep separate from plant parameters | scenario noise profiles and observer/sensor wrapper |

Current practical constraint:

```text
Do not require battery, Mid360, flight-controller, or computer mounting
positions as hard inputs. The available STL is an integrated visual/engineering
model and does not reliably expose semantic parts or exact component centers.
Use STL only for outer geometry, rotor-axis sanity checks, and visual scale.
Use PX4 logs and motor/prop public data as the main route for dynamics
identification.
```

Code-first open-source route priority:

1. Use `pyulog` to inspect topic availability and export aligned CSV.
2. Use `References/Data/data-driven-dynamics` for ULog-to-parametric-model
   structure, topic names, and held-out prediction workflow.
3. Use ARPL `data-driven-system-identification` / `sysid.tools` style
   angular/translational
   identification for inertia, thrust, yaw moment, lag, and drag when enough
   excitation logs exist.
4. If only ordinary PX4 logs are available, start with mass, motor order,
   hover-thrust sanity, and coarse inertia/motor sensitivity bands; do not
   claim high-confidence full identification.

Prefer reproducible repositories over paper-only methods. Paper-only methods
may stay in the bibliography, but the implementation queue should be built from
code that can be cloned, run, inspected, and adapted to Sunray150 logs.

### 8.2 Local Code Audit: Required Logs

The local code in `References/Data/` shows that the first useful data package
can be collected by normal RC/manual operation. The special requirement is not
a special flight computer or lab rig; it is enabling the right PX4 log topics
and flying maneuvers that excite throttle, roll, pitch, yaw, and translation.

| Local repository | What it can provide | Required log data | Verdict for Sunray150 |
|---|---|---|---|
| `References/Data/data-driven-system-identification` | Main route for inertia, thrust curve, yaw torque ratio, and motor first-order delay | `actuator_motors` or `actuator_motors_mux` `control[0..3]`, `vehicle_acceleration.xyz`, `vehicle_angular_velocity.xyz`, `vehicle_angular_velocity.xyz_derivative` when available; high-rate/system-ID logging recommended | Best route if PX4 can log high-rate actuator plus IMU-derived acceleration/rate data. Needs deliberate RC excitation, not just smooth autonomous flight. |
| `References/Data/data-driven-dynamics` | Parametric multirotor force/moment model, fit-quality report, held-out prediction workflow | `actuator_outputs.output[0..3]`, `vehicle_local_position.vx/vy/vz`, `vehicle_attitude.q[0..3]`, `vehicle_angular_velocity.xyz`, `sensor_combined.accelerometer_m_s2/gyro_rad`, `vehicle_land_detected.landed` | Good auxiliary route and topic-completeness checker. Its sample vehicle parameters are not Sunray150 truth. |
| `References/Data/airo_control_interface` | Offboard/MAVROS control-interface calibration: hover thrust and first-order inner-loop time constants (`tau_phi`, `tau_theta`, `tau_psi`) | MAVROS target attitude, local position pose, and local velocity topics from its auto system-identification launch workflow | Useful for MPC/control-interface calibration if we later run ROS/offboard tests. It is not a full physical mass/inertia estimator. |
| `References/Data/px4_pid_tuner` | Rate-loop transfer behavior and PID sanity check | `actuator_controls_0.control[0..2]` and attitude/rate response (`rollspeed`, `pitchspeed`, `yawspeed` or equivalent modern PX4 topics) | Useful for controller tuning evidence only; do not use as physical mass/inertia truth. |
| `References/Data/px4tools` | ULog/Pandas analysis, noise analysis, simple system-ID/control-design utilities | Standard ULog with attitude, rate, actuator, sensor, battery topics | Useful for topic audit, noise, delay, and sanity plots. |
| `References/Data/esc_test` | Motor/prop/ESC bench characterization: thrust-vs-RPM and torque-vs-thrust | Bench data with RPM, thrust, torque, voltage/current | Optional. Use only if a thrust stand or ESC/RPM bench log is available. |
| `References/Data/pyulog` | ULog parser and CSV exporter | Any PX4 `.ulg` | First-pass topic audit tool before running estimators. |

Minimal RC-collected ULog package:

| Log | Duration | RC operation | Main purpose |
|---|---:|---|---|
| `static_imu_01.ulg` | 30-60 s | Props disarmed or motors safe; vehicle stationary | Sensor bias/noise and topic audit. |
| `hover_collective_01.ulg` | 60-90 s | Take off, hold 1.5-3 m, then apply gentle collective/altitude pulses within safe margin | Mass sanity, hover thrust, command-to-thrust trend, motor lag if actuator/RPM data exists. |
| `attitude_excitation_01.ulg` | 90-120 s | Around hover, apply small roll, pitch, yaw stick pulses or slow chirps one axis at a time | Inertia, yaw moment ratio, cross-axis coupling, rate-loop dynamics. |
| `translation_validation_01.ulg` | 90-120 s | Forward/back, left/right, slow figure-eight or box path at modest speed | Drag/residual validation and held-out trajectory check. |

Practical RC constraints:

1. Keep the vehicle in a safe stabilized/position/altitude mode. The estimator
   does not require fully autonomous trajectory generation.
2. Avoid aggressive maneuvers, crashes, motor saturation, failsafe, and large
   battery sag during identification windows.
3. Excite one main axis at a time for attitude logs. Mixed random stick motion
   is useful later, but it makes the first fit harder to debug.
4. Keep one complete log as held-out validation; do not tune or identify on
   every available window.

Preferred PX4 logging setup:

```text
Enable SDLOG_PROFILE entries for high-rate and system-identification topics.
Minimum useful resampling target: 250 Hz.
Preferred for ARPL-style identification if the SD card can keep up: 500-1000 Hz.
If MAVLink shell access is available:
  logger stop
  logger start -r 250 -b 100
or, for high-rate ARPL tests:
  logger stop
  logger start -r 1000 -b 100
```

Required topics by priority:

| Priority | Topic / field | Reason |
|---|---|---|
| P0 | `actuator_outputs.output[0..3]` and/or `actuator_motors.control[0..3]` / `actuator_motors_mux.control[0..3]` | Motor command input. Need to know whether values are PWM, normalized command, or RPM-related. |
| P0 | `vehicle_angular_velocity.xyz[0..2]` | Body-rate response for inertia, yaw, and controller dynamics. |
| P0 | `vehicle_acceleration.xyz[0..2]` if available, otherwise `sensor_combined.accelerometer_m_s2[0..2]` | Thrust and translational acceleration fitting. |
| P0 | `vehicle_attitude.q[0..3]` | Body/world-frame conversion and validation. |
| P0 | `vehicle_local_position.vx/vy/vz` | Drag and trajectory validation. |
| P0 | `vehicle_land_detected.landed` | Remove ground/takeoff/landing windows. |
| P0 | PX4 parameter export (`.params`) | Decode control allocation, motor order, actuator scaling, logging configuration. |
| P1 | `battery_status.voltage_v/current_a/remaining` or equivalents | Reject voltage-sag windows and calibrate thrust-envelope assumptions. |
| P1 | ESC telemetry / RPM topics if available (`esc_status`, `esc_report`, `rpm`, vendor equivalent) | Convert command-thrust model into physical `T=k_f omega^2`. |
| P1 | `manual_control_setpoint`, `vehicle_status`, `vehicle_rates_setpoint`, `rate_ctrl_status` if available | Reconstruct maneuver intent, flight mode, and controller saturation. |
| P2 | Wind/weather notes, payload notes, prop/motor/ESC exact model | Explain residuals and build separate parameter profiles. |

Do not block the first identification pass on exact battery, Mid360, flight
controller, or computer mounting positions. If the engineer can provide only
ULog + `.params` + exact takeoff mass + motor/prop/ESC model, that is enough to
start a defensible first parameter fit.

What each data level enables:

| Available data | Parameters we can estimate or validate | Confidence |
|---|---|---|
| One ordinary `.ulg` only | Topic completeness, motor order/sign sanity, hover-thrust plausibility, rough controller delay | Low to medium |
| RC logs above + `.params` + mass | Inertia band, command-thrust curve, yaw coefficient trend, motor lag trend, drag residual | Medium |
| Same logs + ESC RPM | Physical thrust coefficient, motor time constant, better yaw/moment fit | Medium-high |
| Thrust stand/bench data + flight logs | Motor/prop thrust/torque model plus flight-validated body dynamics | High |

### 8.3 Public Data, Geometry, And Low-Cost Identification Audit

Use three evidence tiers before asking for expensive lab measurements.

#### Tier A: Public / vendor data usable as priors

These values can seed the model or sanity-check logs, but they are not enough
to claim identified dynamics:

| Source | Data we can use | How to use it |
|---|---|---|
| YunZong Sunray-150 hardware page | 210 mm x 210 mm x 160 mm outer size, 150 mm wheelbase, about 1080 g for the listed hardware configuration | Use as mass/dimension prior; still weigh the exact battery/Mid360/payload configuration before final model update. |
| YunZong power-system page | Sunray BD-45 battery: 4S1P, 5000 mAh, 340 g, 92.5 mm x 46 mm x 52.3 mm; propeller diameter 90 mm, 5 blades, 2.4 inch pitch, 3.52 g | Use for component mass distribution, propeller sanity check, and hover thrust bounds. |
| User-provided GTS V3 2104-M2-3000KV motor table | motor mass `16 g`, size about `25.35 mm x 13.8 mm`, 3-4S support, D90 prop thrust samples at 16 V: `299 g` at 50% throttle and `806 g` at 100% throttle | Use as thrust-envelope and hover-throttle prior before ULog fitting. Do not treat table throttle percentage as PX4 actuator command without calibration. |
| User-provided D90 propeller spec | prop disc diameter `90 mm`, `5` blades, pitch `2.4 inch`, mass `3.52 g`; this is the propeller, while `3.5-inch` describes the frame class | Use for rotor/prop sanity check and thrust-table interpretation; do not call the propeller 3.5-inch in reports. |
| Livox Mid-360 spec | 265 g, 65 mm x 65 mm x 60 mm, 360 deg horizontal FOV, vertical -7 deg to 52 deg, 200k points/s, 10 Hz typical frame rate, 9-27 V, 6.5 W | Use for payload mass, lidar pose, lidar update rate, and perception scenario limits. |
| CUAV V6X / V6X V2 page | PX4-compatible controller, triple redundant IMU, barometer, RM3100 compass, Ethernet, PWM voltage-level switching, power module support | Use for log/topic expectations and hardware interface assumptions; page text is not enough for mass/inertia. |

Keep source links in the parameter evidence bundle:

```text
Sunray hardware: https://wiki.yundrone.cn/Docs/Sunray150-ying-jian-zheng-ti-jie-shao
Sunray power system: https://wiki.yundrone.cn/Docs/dong-li-xi-tong
Sunray PX4 logs: https://wiki.yundrone.cn/Docs/PX4-fei-xing-ri-zhi
Mid360 on Sunray: https://wiki.yundrone.cn/Docs/san-wei-ji-guang-lei-da
Livox Mid-360 official specs: https://www.livoxtech.com/cn/mid-360/specs
CUAV V6X: https://www.cuav.net/v6x/
```

#### Tier B: Geometry measurable from project assets

The Sunray SDF and STL assets are valid geometry priors, not physical dynamics
truth by themselves.

Current project geometry audit:

| Item | Local source | Current value / observation |
|---|---|---|
| Body visual STL | `References/MWORKS/QuadrotorModel/Resources/Visualization/sunray150_mid360_body.stl` and original `sunray.stl` | Raw STL bbox `8.3268 x 8.4508 x 6.3742`; SDF visual scale `0.03`, giving about `0.2498 x 0.2535 x 0.1912 m`. |
| Propeller visual STL | `References/MWORKS/QuadrotorModel/Resources/Visualization/sunray150_mid360_propeller.stl` and original `sunray_cw.stl` | Raw STL bbox `71.1655 x 80.5003 x 7.3182`; SDF visual scale `0.001`, giving about `0.0712 x 0.0805 x 0.0073 m`. |
| Rotor positions | `References/Sunray/.../sunray150_with_mid360.sdf` | rotor 0 `(0.065,-0.065,-0.025)`, rotor 1 `(-0.065,0.065,-0.025)`, rotor 2 `(0.065,0.065,-0.025)`, rotor 3 `(-0.065,-0.065,-0.025)`. |
| Rotor directions | same SDF motor plugins | rotor 0/1 `ccw`, rotor 2/3 `cw`; confirm against PX4 motor order before changing allocation. |
| Mid360 pose | same SDF | `(0.036,-0.0155,0.075)` relative to `base_link`. |

Important consistency check:

```text
The SDF rotor coordinates are a migrated simulator seed, not final hardware
truth. They imply x/y motor-axis spacing of 0.13 m and a diagonal motor-axis
distance of about 0.184 m, while the public/user-provided Sunray150 / 3.5-inch
frame-class evidence points to an about-150-mm frame class. The propeller is a
D90/90-mm 5-blade prop, not a 3.5-inch prop. Do not overwrite either
value blindly; define which wheelbase convention is used, then cross-check with
STL, real motor-axis measurement, and PX4 motor order before changing dynamics
or mixer geometry.
```

User audit update:

```text
For the current Sunray150 work, treat a user-provided or directly measured
takeoff mass as the accepted mass input for that exact flight configuration
unless a later weighing/log consistency check contradicts it. This does not
upgrade inertia, rotor geometry, motor coefficients, drag, controller evidence,
or the full parameter set to `identified`; those still require the ULog,
held-out validation, and MWORKS verification bundle above. Treat
wheelbase/rotor geometry as a geometry-measurement issue: use STL and real
motor-axis measurement as the primary source, and use the 3.5-inch frame class /
about-150-mm frame class as the plausibility check. Do not copy YunZong/Gazebo
inertia values across vehicles just because the simulator runs.
```

#### Tier C: Low-cost identification routes

Use these before requesting expensive professional measurement:

| Parameter | Low-cost route | Confidence |
|---|---|---|
| `mass_kg` | Direct weighing of exact battery + Mid360 + guard + payload; cross-check with hover logs | High |
| `center_of_gravity` | Balance/knife-edge method or component mass and lever-arm table | Medium-high |
| `rotor_positions_m` | STL/SDF + ruler/caliper measurement from actual motor axes to CG | High |
| `inertia_kg_m2` | Component mass distribution / CAD mesh as seed; bifilar/trifilar pendulum for low-cost physical measurement; PX4 ULog angular excitation for final fit | Medium to high when validated |
| `thrust_curve` | PX4 ULog with actuator/RPM if available; otherwise hover/throttle excitation and motor command curve; cheap scale/thrust-stand as optional cross-check | Medium without RPM, high with RPM/thrust stand |
| `moment_coefficient` | Yaw excitation logs after thrust curve and inertia are constrained | Medium |
| `motor_time_constant_s` | ESC RPM telemetry step/chirp if available; otherwise ARPL/sysid.tools latent time-constant fit from ULog | Medium |
| `drag` | Calm translational passes with velocity/acceleration/attitude logs; reject windy windows | Medium-low unless wind is measured |

Do not fit everything from one ordinary mission log unless it contains enough
excitation. One log can validate signs and rough hover behavior; it usually
cannot identify a defensible full dynamics model.

#### Tier D: Open-source / paper methods to reuse

Primary method:

```text
sysid.tools / ARPL paper:
Data-Driven System Identification of Quadrotors Subject to Motor Delays
https://sysid.tools/
https://arxiv.org/abs/2404.07837
```

Why it matches this project:

1. It is explicitly designed for quadrotor parameter identification from PX4
   ULog data.
2. It estimates inertia, thrust curve, motor torque coefficient, and first
   order motor delay.
3. It only requires easy-to-measure parameters such as mass, rotor positions,
   thrust directions, and torque directions, plus short excitation flights.
4. It supports the practical case where RPM is not measured by estimating a
   latent motor time constant.

Local auxiliary method:

```text
References/Data/data-driven-dynamics/
```

Use it for ULog parsing, topic completeness checks, dataframe structure,
optimizer configuration, and held-out prediction validation. It should not be
treated as Sunray150 truth because its included quadrotor example parameters
belong to a reference vehicle.

### 8.4 Minimal Engineer Data Request

If the engineer can only provide logs and ordinary product information, ask for
this package first:

| Priority | Request | Why |
|---|---|---|
| P0 | Exact takeoff mass of `sunray150_with_mid360` with battery, guards, payload, and current mounting | Mass affects every thrust and acceleration estimate. |
| P0 | PX4 `.ulg` logs for hover/collective, small roll-pitch-yaw excitation, and one normal trajectory | Needed to identify or validate thrust, inertia, yaw coefficient, motor lag, and drag. |
| P0 | PX4 parameter export (`.params`) and airframe/mixer/control-allocation config | Needed to decode actuator order, command scaling, motor direction, and logging setup. |
| P0 | Motor order, rotor spin direction, propeller model, motor/ESC model, battery model | Prevents wrong allocation signs and wrong thrust curve interpretation. |
| P1 | Whether ESC RPM telemetry exists; if yes, include RPM logs | Converts command-thrust fitting into physical `T=k_f omega^2` fitting. |
| P1 | Battery voltage/current logs and wind/weather notes | Rejects voltage-sag and wind-biased identification windows. |
| P2 | Simple measurements: motor-axis coordinates relative to CG, if available | Improves geometry seed. Component mounting positions are optional only; do not block identification on them because the integrated STL does not provide reliable semantic component centers. |

If only one ordinary `.ulg` is available, the first deliverable should be a
topic-completeness and sign-consistency report, not final parameters.

### 8.5 Extended Paper And Project Survey

Do not rely on a single paper or one repository. Use the following routes as a
method stack and select the cheapest route that can identify the parameter in
question.

| Route | What it can identify | What data it needs | Project use |
|---|---|---|---|
| ARPL `data-driven-system-identification` / `sysid.tools` | inertia, thrust curve, torque coefficient, first-order motor delay | about one minute of proprioceptive flight data / PX4 ULog, mass, rotor positions, thrust and torque directions | Primary no-extra-instrument route for Sunray150 logs. |
| ETH `data-driven-dynamics` | parametric dynamics from PX4 ULog/CSV, fit quality, held-out prediction, Gazebo parameter export | ULog topics configured per vehicle model; PX4/SITL tooling for full workflow | Local auxiliary pipeline for topic validation and MWORKS parameter YAML structure. |
| IMU/Newton-Euler inertia estimation | inertia tensor from IMU angular velocity/acceleration and torque model | IMU/rate data plus known or estimated torque input | Useful when we want inertia refinement without dedicated inertia hardware. |
| CAD/STL + component mass distribution | coarse mass, CG, inertia seed, rotor geometry | STL/CAD, actual component masses, mounting positions | Cheap first-pass seed; must be validated by flight logs. |
| Low-cost rig method | PWM-to-RPM, PWM-to-thrust, rotor drag moment | simple motor/prop rig, scale/tachometer or equivalent | Best practical route if ESC RPM is unavailable and thrust curve quality matters. |
| Drag coefficient from outdoor flight tests | translational drag / wind-related residual model | velocity, acceleration, attitude, mass, calm repeated flight segments | Use after thrust/inertia are stable; otherwise drag absorbs other model errors. |
| Online mass/inertia RLS / adaptive estimation | payload mass/inertia changes | closed-loop input-output data with enough excitation | Later extension for payload-change robustness, not first calibration. |
| Control-effectiveness / unknown actuator identification | motor effectiveness, thrust directions, IMU offset/orientation, motor dynamics | aggressive/throw/catch or rich excitation data; safety constraints | Reference for future fault/allocation work; not necessary for baseline Sunray model. |
| IMU-data mass estimation / instrumental variables | mass or mass-change estimate from inertial measurements and pilot commands | IMU acceleration/rate, attitude/rate command or pilot command, closed-loop data | Useful sanity check against accepted takeoff mass and later payload tests. |
| Motor-efficiency residual minimization | per-motor efficiency / degradation factors | measured flight states and motor thrust/moment model | Directly relevant to the motor-efficiency fault scenarios after baseline parameters are stable. |
| High-speed gray-box aerodynamic identification | aerodynamic force/moment residuals, interaction terms | high-speed flight data, ideally rotor speed and wind/tunnel data | Useful for future high-speed / frame-pass scenarios, not required for first Sunray hover/8-shape model. |
| MATLAB UAV Toolbox flight-log example | ULog import, time-window selection, parameter estimation workflow | PX4 ULog; MATLAB helper functions / UAV Toolbox | Useful workflow reference for our Syslab/MWORKS equivalent tooling. |
| PX4 log PID/system-ID tools | attitude-rate loop transfer behavior and tuning evidence | PX4 ULog attitude-rate setpoint/response and actuator outputs | Useful for controller tuning and sanity checks, but not a full physical parameter estimator. |
| MuJoCo body-regressor style identification | 10 rigid-body inertial parameters from dynamic maneuvers | known/estimated wrench or simulated ground truth; rich trajectory | Good conceptual reference for future toolchain; less direct for PX4-only logs unless wrench estimates are reliable. |

Reference links to keep with this survey:

```text
ARPL / sysid.tools paper: https://arxiv.org/abs/2404.07837
P0 code - ARPL data-driven-system-identification: https://github.com/arplaboratory/data-driven-system-identification
P0 code - ETH data-driven-dynamics: https://github.com/ethz-asl/data-driven-dynamics
P0 code - PX4 pyulog: https://github.com/PX4/pyulog
P1 code - px4tools log/system-ID toolbox: https://github.com/dronecrew/px4tools
P1 code - PX4 PID tuner: https://github.com/mzahana/px4_pid_tuner
P1 code - HKPolyU airo_control_interface MPC system-ID launch/workflow: https://github.com/HKPolyU-UAV/airo_control_interface
P1 code - motor/prop/ESC characterization scripts: https://github.com/alspitz/esc_test
P2 code/data - nano-drone sysid benchmark: https://github.com/idsia-robotics/nanodrone-sysid-benchmark
IMU-based inertia estimation: https://www.grasp.upenn.edu/publications/imu-based-inertia-estimation-for-a-quadrotor-using-newton-euler-dynamics/
Low-cost parameter/test-rig methodology: https://amekhalifa.github.io/files/conference/2013_meth_ident_AIM13.pdf
Quadrotor drag from flight tests: https://journals.sagepub.com/doi/10.1177/17568293221148378
Unknown actuator/sensor configuration identification: https://arxiv.org/abs/2409.01080
Mass estimation from IMU/pilot commands: https://liu.diva-portal.org/smash/record.jsf?pid=diva2%3A1133681
Real-time mass and inertia tensor estimation: https://scholarworks.aub.edu.lb/handle/10938/23088
Quadrotor gray-box aerodynamic identification: https://www.growkudos.com/publications/10.2514%25252F1.c035135/reader
Motor-efficiency residual minimization: https://arxiv.org/abs/2510.11388
PX4 control allocation rotor parameters: https://docs.px4.io/v1.13/en/advanced_Config/parameter_reference.html
MATLAB UAV Toolbox ULog parameter-estimation example: https://dokumen.pub/uav-toolbox-users-guide.html
MuJoCo inertial parameter identification reference: https://deepwiki.com/based-robotics/mujoco-sysid/4.3-skydio-x2-quadrotor-identification
```

Current priority order for Sunray150:

```text
1. Lock geometry: STL/actual motor-axis measurement, motor order, rotor direction.
2. Lock mass and component placement: measured or user-provided takeoff mass
   with provenance, plus battery/Mid360/FC/motor positions.
3. Run ULog topic audit: can we see actuator, gyro/rate, attitude, acceleration, battery, RPM?
4. If RPM exists: fit physical thrust curve and motor lag.
5. If RPM does not exist: use ARPL/sysid.tools latent delay + command-thrust fit.
6. Use attitude excitation to refine inertia and yaw coefficient.
7. Use calm translational logs only after 1-6 to fit drag.
8. Apply to MWORKS and validate with hover, 8-shape, spiral, wind, and motor-efficiency scenarios.
```

Current audit result: no YunZong/Sunray real ULog files are present in the
repository. The only usable local ULog-like material is reference/sample data
under `References/Data`, so all current MWORKS model values remain
`source=SDF_migration` until vendor/user logs are provided and the pipeline
passes held-out validation.

Hard blockers before claiming identified Sunray150 parameters:

```text
exact vehicle mass with battery, Mid360, guards, and payload
PX4 .ulg logs with high-rate actuator, acceleration, attitude, and gyro topics
PX4 motor order, rotor direction, and actuator signal meaning
rotor/prop/motor/ESC details and PWM/RPM/battery voltage context
confirmation that the tested hardware matches sunray150_with_mid360 geometry
wind/weather notes for drag identification
```

---

## 9. User Data Checklist

Ask the user for the following before claiming identified Sunray150 parameters:

| Needed data | Required? | Notes |
|---|---|---|
| PX4 `.ulg` files for hover/throttle excitation | Yes | Include stable hover and collective changes |
| PX4 `.ulg` files for attitude chirp/rate excitation | Yes | Needed for inertia and torque constants |
| PX4 `.ulg` files for translational/drag excitation | Yes | Needed for drag and validation |
| Vehicle mass with battery and Mid360 installed | Yes | Weigh the exact test configuration |
| Rotor/propeller model and size | Yes | Needed to interpret thrust coefficient |
| Motor/ESC mapping and PX4 motor order | Yes | Prevents wrong allocation signs |
| PWM range, mixer, or actuator normalization details | Yes | Required if no RPM telemetry is available |
| Battery voltage/current logs | Recommended | Reject voltage-sag windows |
| ESC RPM telemetry or tachometer data | Recommended | Best route to physical `k_f` and motor lag |
| Weather/wind notes and test location | Recommended | Helps separate drag from wind bias |
| Any payload changes during tests | Yes if changed | Create separate YAML profiles |

Stop if these are missing:

```text
No ULog files
No motor order / actuator signal meaning
No mass for the exact Sunray150 configuration
```

In that case, keep the current parameters labeled as `source=SDF_migration` or
`source=reference_repo`, and mark MWORKS results as sensitivity tests rather
than identified-parameter evidence.
