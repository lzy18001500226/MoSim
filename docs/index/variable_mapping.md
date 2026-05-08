# Result Variable Mapping

This file records how MWORKS/Sysplorer result variable names map to the project-standard CSV schema.

The initial table is a placeholder. After the first successful Sysplorer MCP simulation, update the `Model Result Variable` column with names confirmed by `result_manager`.

| Standard Name | Model Result Variable | Required | Notes |
|---|---|---:|---|
| `time` | `time` | yes | Simulation time axis |
| `x` | TBD | yes | World position x |
| `y` | TBD | yes | World position y |
| `z` | TBD | yes | World position z |
| `vx` | TBD | recommended | World velocity x |
| `vy` | TBD | recommended | World velocity y |
| `vz` | TBD | recommended | World velocity z |
| `roll` | TBD | recommended | Euler roll |
| `pitch` | TBD | recommended | Euler pitch |
| `yaw` | TBD | recommended | Euler yaw |
| `u1` | TBD | recommended | Motor command 1 |
| `u2` | TBD | recommended | Motor command 2 |
| `u3` | TBD | recommended | Motor command 3 |
| `u4` | TBD | recommended | Motor command 4 |
| `x_ref` | TBD | yes | Reference x |
| `y_ref` | TBD | yes | Reference y |
| `z_ref` | TBD | yes | Reference z |
| `controller_mode` | TBD | optional | Mode switching and video annotation |
| `event_log` | TBD | optional | Event-driven replay and report evidence |

## Update Procedure

1. Run or open a result file with Sysplorer MCP `result_manager`.
2. Query available result variables.
3. Fill the mapping table above.
4. Use the standard names when exporting `results/raw/*.csv`.
5. Keep non-obvious mappings in experiment logs under `results/test_reports/`.

