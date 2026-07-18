# Final Controller A/B Motor-Fault Infrastructure Blocker

Date: 2026-07-18

Status: `closed_as_infrastructure_blocked`.

One clean, single-case retry was run for `official_pid + motor_efficiency_fault`
after the ROS1/Sunray/Gazebo/PX4 preflight passed. The FTC actuator plugin built,
the injector had one command connection, and 18-column telemetry was available.
The injector nevertheless timed out after 180 seconds before an airborne window:
local odometry reached only `0.075075 m` and Sunray truth reached `0.035016 m`.
The flight gate started late and later produced a passed ordinary
takeoff-hover-land metric, but the fault was never applied; this is not a
motor-fault controller result.

The outer 360-second budget stopped the orchestration. All task-owned Gazebo,
PX4, MAVROS, ROS master, px4ctrl and wrapper processes were then terminated,
and no runtime lock remained.

Decision: keep both C3 motor-fault A/B rows as `not_run`, stop retries in the
current closeout, and retain the accepted P7 rotor-1 effectiveness `0.65` run as
the bounded FTC authority. Do not claim either PID profile passed a motor-fault
A/B from this directory.
