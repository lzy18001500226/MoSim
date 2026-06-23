# CoSim Documentation Index

Status: rebuild draft, 2026-06-14.

CoSim is the long-term simulation-platform blueprint that sits beyond the
current A8 competition slice. It is organized by product capability tree first,
not by simulator names.

## Reading Order

| Order | Path | Purpose |
|---:|---|---|
| 1 | `cache/cosim_rebuild_plan_20260614.md` | Rebuild goal, captured user requirements, and preservation rules. |
| 2 | `research/README.md` | Short, template-based research conclusions and backend decisions. |
| 3 | `00_platform/00_CoSim总体蓝图.md` | Product-level blueprint and authority tree. |
| 4 | `10_shared_core/01_共享内核与数据契约.md` | Shared kernel, contracts, clock, logs, replay, and evidence. |
| 5 | `20_vehicle_families/README.md` | Vehicle-family capability tree. |
| 6 | `30_backend_adapters/README.md` | Backend adapter decisions and comparison matrix. |

## Directory Map

| Directory | Role |
|---|---|
| `00_platform/` | Platform-level purpose, principles, and roadmap. |
| `10_shared_core/` | Shared services used by all vehicle families. |
| `20_vehicle_families/` | Product trees for multirotor, fixed-wing, VTOL, and ducted model-aircraft lines. |
| `30_backend_adapters/` | Gazebo, JSBSim, Simulink, MuJoCo, Isaac, AirSim, and other backend adapter boundaries. |
| `research/` | Condensed research conclusions that architecture docs can cite. |
| `research/raw/` | Preserved original long-form research notes. Do not treat as deleted. |
| `cache/` | Rebuild plan, migration manifest, research template, and audit notes. |

## Core Architecture Rule

```text
vehicle family defines product needs
  -> shared core defines common contracts
  -> backend adapter supplies one authority surface
  -> architecture cites reviewed research decisions
  -> implementation follows reviewed architecture
```

Simulator names are not the product tree. Gazebo, JSBSim, MuJoCo, Isaac,
AirSim, Webots, CARLA, Bullet, and Flightmare are backend/reference candidates
that must be evaluated against a vehicle-family need.

## Safety Scope

CoSim may cover hobby/model-aircraft simulation, benign test bodies, and
non-destructive simulation research. It must not provide weaponization,
targeting, destructive payload, terminal guidance, or deployment guidance.
