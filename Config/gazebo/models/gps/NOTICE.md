# PX4 GPS Model Notice

`gps.sdf` and `model.config` are a local, unmodified compatibility copy of:

```text
PX4-Autopilot/Tools/sitl_gazebo/models/gps/
```

from the repository snapshot at
`References/超维空间科技/PX4-Autopilot`. The upstream source is licensed under
the BSD 3-Clause License, Copyright (c) 2012 - 2022, PX4 Development Team.
The original license is retained at
`References/超维空间科技/PX4-Autopilot/LICENSE`.

This small local model is packaged so that the current runtime removes the
PX4 global model path without making `model://gps` resolution depend on a
machine-global Gazebo cache.
