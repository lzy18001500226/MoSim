# Applications

`apps/` holds project-facing application code. It does not own flight-control
truth, MWORKS model truth, or runtime acceptance.

| Application | Role |
|---|---|
| `flight_console/` | operator-facing mission, map, and review surface; submits approved experiment intent and displays state |
| `model_studio/` | controller/model composition and offline analysis surface; uses the canonical MWORKS package and profile contracts |

Applications consume declared interfaces from `Config/`, `Models/`, runtime
bridges, and `Results/`. They must not bypass the controller/runtime authority
or create private copies of models and configuration.
