# Model Studio D1 Gate Summary

Status: `pass`

MWORKS.Syslab `26.3.1.7499` successfully ran and packaged the lightweight native
MoSim Model Studio APP. The UI rendered its selectors, numeric input, buttons,
status area, and native plot. A `px4ctrl` three-UAV request increased the request
count from two to three. A five-UAV selection and the unavailable `nmpc_outer`
controller were rejected without creating request files.

Installable artifact:

`apps/model_studio/dist/MoSim Model Studio.slappinstall`

This is a D1 APP capability gate. Runtime request consumption and the complete
MWORKS/codegen/Gazebo/PX4/MAVROS/RViz/UE loop remain D3-D7 work.
