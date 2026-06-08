# Future Live Audit Queue Update

021 removes the R2 017 source-level unresolved-target blocker for the current Dynamics alias chain. Future live work is still not authorized by this packet.

## Serialized Queue

1. Verify `MoSimQuadrotorModel` root package-browser visibility: 12 categories, with `Parameters` after `Dynamics`.
2. Verify `MoSimQuadrotorModel.Dynamics` 12 formal entries in package browser and, if authorized, `check_model`.
3. Verify `QuadrotorExperiments.DynamicsUpgrade` 12 public compatibility aliases, while keeping `Sunray150*.mo` implementation classes out of the public `package.order`.
4. Verify `MoSimQuadrotorModel.Parameters.Sunray150ParameterProvenance` visibility/load/check if live MWORKS is authorized.
5. Run R2 graphical/layout/wiring review only after package/load/check gates are available.

## Resource Lock

Use one reusable existing MWORKS/Sysplorer session. Do not use a route that starts a new MWORKS/Sysplorer window. Stop on demo/login/authorization/error-report/visible-unknown evidence.
