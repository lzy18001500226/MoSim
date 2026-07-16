# Model Studio D4 Gate Summary

Status: `pass`

MWORKS.Syslab `26.3.1.7499` packaged MoSim Model Studio `0.2.0` as a clean
four-entry `.slappinstall`. The native APP uses the Registry/Profile Catalog,
prepares accepted profiles through the persistent Orchestrator, and retains the
same `run_id` for model-context and result requests.

The accepted three-UAV request used `px4ctrl` and produced:

```text
run_id: run-20260717-043043-92b4b031
profile_hash: 1ab843fd75297f13a1935db9c79021413ac951a0656d6df8b96b32e237c52783
request_id: req-d69ee49337b94a1cb97edae54d5a8bfa
```

`Open model` returned `model_context_requested`. `Open result` correctly
returned `result_packet_not_available` because no runtime result exists. Four
to nine UAVs and controllers without accepted runtime evidence remain rejected.
The targeted suite passed all 11 tests.

Installable artifact:

`apps/model_studio/dist/MoSim Model Studio.slappinstall`

This D4 gate does not prove MWORKS simulation/codegen, Gazebo/PX4/MAVROS
runtime, RViz/UE attachment, or flight performance. Those remain D6-D7 work.
