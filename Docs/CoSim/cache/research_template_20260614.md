# CoSim Research Decision Template

Each reviewed research decision document should answer the same questions so
models and humans can compare backends without loading every raw note.

## Template

```text
# <Technology / Ecosystem Name>

Status:
Source raw notes:
External sources:

## 1. Position

What this technology is, in one paragraph.

## 2. Best-Fit Vehicle Families

| Vehicle family | Fit | Reason |

## 3. Authority Classification

| Authority surface | Classification |
| Plant truth |
| Flight-control authority |
| ROS2 / algorithm bus |
| UE / rendering frontend |
| Sensor generation |
| RL / batch training |
| SIL / HIL / deployment |

Allowed claims and forbidden claims must be explicit.

## 4. Integration Pattern

Show the preferred data flow.

## 5. Strengths

## 6. Gaps And Risks

## 7. CoSim Adoption Decision

Use one of:

- default backend;
- optional backend;
- reference architecture only;
- research-only;
- not recommended.

## 8. Required Next Evidence

What must be proven before this technology can move from design to runtime
authority.
```

## Review Rule

Reviewed research decisions are not transcripts. They must compress raw notes
into decisions and preserve pointers back to raw files for trace-back.
