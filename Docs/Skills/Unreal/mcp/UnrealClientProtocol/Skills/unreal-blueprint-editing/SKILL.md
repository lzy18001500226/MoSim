---
name: unreal-blueprint-editing
description: Edit UE Blueprint node graphs via text (ReadGraph/WriteGraph). Use when the user asks to add, remove, or rewire Blueprint nodes, create/modify functions, events, or variables in a Blueprint graph.
---

# Blueprint Editing

Edit Blueprint node graphs via a text-based representation. For setting object properties on the Blueprint asset itself, use the `unreal-object-operation` skill.

**Prerequisite**: UE editor running with UCP plugin enabled.

## Node Graph API

CDO: `/Script/UnrealClientProtocolEditor.Default__NodeCodeEditingLibrary`

| Function | Params | Description |
|----------|--------|-------------|
| `Outline` | `AssetPath` | Returns available sections (EventGraph, Function:Name, Macro:Name, Variables) |
| `ReadGraph` | `AssetPath`, `Section` | Returns text representation. Empty Section = all sections. |
| `WriteGraph` | `AssetPath`, `Section`, `GraphText` | Overwrite section. Empty GraphText = delete section. Auto-recompiles. |

## Reading Strategy

**CRITICAL: Never read all sections at once.** Blueprints can have dozens of functions/macros.

1. **Outline first** — get the structure
2. **Identify relevant sections** — based on the task, pick only what you need
3. **ReadGraph one section at a time** — read only what you need
4. **Summarize before reading more** — decide if you need more context

## Section Types

| Section Format | Description |
|---------------|-------------|
| `EventGraph` | Main event graph |
| `Function:<Name>` | A function graph |
| `Macro:<Name>` | A macro graph |
| `Variables` | Blueprint variable definitions |

Names with spaces use underscores: `Function:My_Function`.

## Text Format

```
[Function:CalculateDamage]

N_2kVm4xRp8bNw6yLq0dJs FunctionEntry
  > then -> N_8nQz4tJi0rAj7mRd3sFg.execute

N_9aEo3jXv2hQy8bFt4iLw VariableGet:BaseDamage
  > -> N_7tHn5cWs1fPx6zMr0gKu.A

N_5fIr7mBz3kTb1eJw9lOa VariableGet:DamageMultiplier
  > -> N_7tHn5cWs1fPx6zMr0gKu.B

N_7tHn5cWs1fPx6zMr0gKu CallFunction:KismetMathLibrary.Multiply_FloatFloat
  > ReturnValue -> N_0hKt8nDc5lUd2gLx6mPb.Value

N_0hKt8nDc5lUd2gLx6mPb CallFunction:KismetMathLibrary.FClamp {pin.Min:0, pin.Max:9999}
  > ReturnValue -> N_8nQz4tJi0rAj7mRd3sFg.ReturnValue

N_8nQz4tJi0rAj7mRd3sFg FunctionResult
```

### Nodes

- `N_<id>`: node reference ID. Two forms:
  - **Existing nodes**: `N_<base62>` — a 22-character Base62-encoded GUID (e.g. `N_2kVm4xRp8bNw6yLq0dJs`). ReadGraph always outputs this form. **Preserve these IDs when writing back.**
  - **New nodes**: `N_new<int>` — temporary ID for nodes you are creating (e.g. `N_new0`, `N_new1`). The system assigns a real GUID after WriteGraph.
- `<ClassName>`: semantic encoding (see below) or raw UE class name
- `{...}`: non-default properties, single line. Omit braces if none.

### ClassName Encoding

| Text Format | UE Node Type | Example |
|-------------|-------------|---------|
| `CallFunction:<Class>.<Func>` | `UK2Node_CallFunction` (external) | `CallFunction:KismetSystemLibrary.PrintString` |
| `CallFunction:<Func>` | `UK2Node_CallFunction` (self) | `CallFunction:MyBlueprintFunction` |
| `VariableGet:<Var>` | `UK2Node_VariableGet` | `VariableGet:Health` |
| `VariableSet:<Var>` | `UK2Node_VariableSet` | `VariableSet:Health` |
| `CustomEvent:<Name>` | `UK2Node_CustomEvent` | `CustomEvent:OnDamageReceived` |
| `Event:<Name>` | `UK2Node_Event` | `Event:ReceiveBeginPlay` |
| `FunctionEntry` | `UK2Node_FunctionEntry` | (auto-generated, cannot create/delete) |
| `FunctionResult` | `UK2Node_FunctionResult` | (auto-generated, cannot create/delete) |

Other node types use their raw class name (e.g. `K2Node_IfThenElse`, `K2Node_ForEachLoop`).

### Connections

Output connections from the owning node, indented with `>`:

```
  > OutputPin -> N_<target>.InputPin    # output to target
  > OutputPin -> [GraphOutput]          # output to graph output
  > -> N_<target>.InputPin              # single-output node (omit pin name)
```

Pin names match UE's internal `PinName`. Common exec pins: `execute`, `then`.

### Properties

Properties serialized in `{...}` via UE reflection. Pin default values use `pin.<PinName>` prefix.

Example: `{pin.InString:"Hello World", pin.Duration:5.0}`

## Variables Section

```
[Variables]
Health: {"PinCategory":"real", "PinSubCategory":"double", "DefaultValue":"100.0"}
bIsAlive: {"PinCategory":"bool", "DefaultValue":"true"}
TargetActor: {"PinCategory":"object", "PinSubCategoryObject":"/Script/Engine.Actor"}
DamageHistory: {"PinCategory":"real", "PinSubCategory":"double", "ContainerType":"Array"}
```

Fields map directly to `FEdGraphPinType` reflection fields. Optional: `"Replicated":true`, `"Category":"MyCategory"`.

The `[Variables]` section uses **full overwrite** semantics:
- Variables in the text that don't exist in the Blueprint are **created**.
- Variables in the text that already exist are **updated** (type, default value, replicated flag, category).
- Variables in the Blueprint but **not in the text** are **deleted**.

**Always ReadGraph("Variables") first** and include all variables you want to keep.

## Creating / Deleting Sections

- **Create function**: `WriteGraph(AssetPath, "Function:NewFunc", graphText)` — if the function doesn't exist, it's created automatically
- **Delete function**: `WriteGraph(AssetPath, "Function:OldFunc", "")` — empty text deletes the section
- Same for Macros

## Pseudocode Translation

**CRITICAL: After ReadGraph, translate the NodeCode into pseudocode before making changes.** NodeCode describes structure (nodes, properties, connections), not logic. You must reconstruct the logic to avoid breaking it.

### Workflow

1. **ReadGraph** — get NodeCode text
2. **Translate to pseudocode** — trace exec flow from entry nodes, resolve data flow into expressions
3. **Reason about the change** — use pseudocode to understand what needs to change
4. **Edit the NodeCode** — make structural changes with full understanding of the logic
5. **WriteGraph** — apply

## Key Rules

1. **Read on-demand, not all at once.** Outline first, then ReadGraph only the sections you need.
2. **Translate to pseudocode after reading** — understand the logic before editing.
3. **Preserve node IDs** — existing nodes have `N_<base62>` IDs that encode their GUID. Always keep them unchanged when writing back. Use `N_new<int>` only for genuinely new nodes.
4. **ReadGraph before WriteGraph** — always read the target section before writing.
5. **FunctionEntry and FunctionResult cannot be created or deleted.**
6. All operations support **Undo** (Ctrl+Z).
7. **Incremental diff** — only changed nodes/connections are modified.

## Error Handling

- Check `diff` object in response: `nodes_added`, `nodes_removed`, `nodes_modified`, `links_added`, `links_removed`.
- Property errors: `"Property not found: ..."` or `"Failed to import ..."`.
- Pin errors: `"Pin not found: ..."`.
- Re-read after write if unsure.
