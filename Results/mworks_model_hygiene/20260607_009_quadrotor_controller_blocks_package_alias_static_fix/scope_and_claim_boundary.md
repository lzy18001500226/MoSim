# QuadrotorControllerBlocks 009 Static Alias Repair Boundary

Request: `RFLY-MOSIM-MWORKS-R2-QUADROTOR-CONTROLLER-BLOCKS-PACKAGE-ALIAS-STATIC-FIX-20260607-009`

This task only repairs the static package-shell alias target spelling in `Models/QuadrotorControllerBlocks/package.mo`.

Allowed claim:

- 19 wrapper aliases now use explicit package-local sibling targets of the form `extends QuadrotorControllerBlocks.AWFF_*`.
- No leading-dot `extends .AWFF_*` targets remain in `package.mo`.
- `package.order` remains the seven-entry 007 shell order.
- The 19 controller `.mo` files and six backup/upgrade `.mo` files match the 007 hash baseline.

Forbidden claims:

- No live Sysplorer/MWORKS acceptance was performed.
- No MCP/GUI/check_model/simulation/Smart Layout/diagram writeback was run.
- No graphical/layout/manual review, controller performance, planner readiness, live runtime ack, or closed-loop result is claimed.
- Live validation remains a separate 010 task after the Sysplorer demo-edition/license sentinel state is resolved.
