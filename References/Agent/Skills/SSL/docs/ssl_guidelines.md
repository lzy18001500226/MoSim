# SSL Guidelines

SSL represents a skill artifact as a typed JSON graph with three linked layers:

- Scheduling Layer: the skill-level record used for capability matching and invocation.
- Structural Layer: a scene-level graph of execution phases.
- Logical Layer: a logic-step graph of source-grounded atomic actions and resource-use evidence.

Cross-layer links are deliberately limited to containment relations and entry pointers. Scenes belong to a skill, logic steps belong to scenes, and traversal begins from the declared entry records. This keeps interface evidence, phase structure, and action/resource-use evidence in distinct parts of the representation.

## Core Fields

### Scheduling Layer

Principal fields:

- `skill_id`
- `skill_name`
- `skill_goal`
- `intent_signature`
- `tags`
- `top_pattern`
- `expected_inputs`
- `expected_outputs`
- `dependencies`
- `control_flow_features`
- `entry_scene_id`
- `subscenes`

This layer should capture the stable capability-facing surface of the skill. It should not duplicate the full execution graph.

### Structural Layer

Principal fields:

- `scene_id`
- `scene_name`
- `scene_type`
- `scene_goal`
- `input`
- `output`
- `entry_conditions`
- `exit_conditions`
- `next_scene_rules`
- `entry_logic_step_id`
- `contained_logic_steps`

A scene should denote a coherent execution phase with its own goal, data contract, and exit conditions. Scene transitions are represented with `next_scene_rules`.

### Logical Layer

Principal fields:

- `logic_step_id`
- `act_type`
- `actor`
- `object`
- `instrument`
- `input_args`
- `output_binding`
- `preconditions`
- `effects`
- `resource_scope`
- `resource_target`
- `next_step_rules`

A logic step should be the smallest operational unit that the source artifact supports without inventing missing implementation details. Split a step when the source supports a change in action type, resource boundary, effect, or control-flow outcome.

## Restricted Vocabularies

`scene_type` values:

- `PREPARE`
- `ACQUIRE`
- `REASON`
- `ACT`
- `VERIFY`
- `RECOVER`
- `FINALIZE`

`act_type` values:

- `READ`
- `SELECT`
- `COMPARE`
- `VALIDATE`
- `INFER`
- `WRITE`
- `UPDATE_STATE`
- `CALL_TOOL`
- `REQUEST`
- `TRANSFER`
- `NOTIFY`
- `TERMINATE`

`resource_scope` values:

- `MEMORY`
- `LOCAL_FS`
- `CODEBASE`
- `PROCESS`
- `USER_DATA`
- `CREDENTIALS`
- `NETWORK`
- `OTHER`

Reserved terminal targets:

- `END_SUCCESS`
- `END_FAIL`
- `YIELD_SUCCESS`
- `YIELD_FAIL`
