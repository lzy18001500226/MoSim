---
name: unreal-large-blueprint-analysis
description: Systematically analyze and translate large UE Blueprints (10+ functions) into C++ or other targets. Use when the user asks to convert a Blueprint to C++, audit a complex Blueprint, or understand a large Blueprint's full logic.
---

# Large Blueprint Analysis

Systematic strategy for reading, understanding, and translating large Blueprints (10+ sections, 100+ nodes). Builds on the `unreal-blueprint-editing` and `unreal-object-operation` skills.

**Prerequisite**: UE editor running with UCP plugin enabled. Read the `unreal-blueprint-editing` skill first for API details.

## Why This Skill Exists

Large Blueprints can have 40+ sections and 1000+ nodes. A single ReadGraph call for the EventGraph alone can return 100KB+ of text. Naive approaches fail because:

- Reading all sections at once exceeds context window limits
- Skipping sections and "guessing" from general knowledge produces inaccurate code
- Unstructured reading leads to missed dependencies between functions

## Phase 1 — Inventory

Get the complete structure before reading any graph content.

### Step 1.1: List all sections

```json
{"object":"/Script/UnrealClientProtocolEditor.Default__NodeCodeEditingLibrary","function":"Outline","params":{"AssetPath":"<asset_path>"}}
```

Record the full list. Categorize each section:

| Category | Examples | Priority |
|----------|---------|----------|
| Entry points | EventGraph, Event:Construct, Event:Tick | Read first |
| Core logic | Function:Initialize, Function:CaptureGrid | Read second |
| Helpers | Macro:CheckAndCreateRT, Macro:DeriveAxes | Read on-demand |
| UI-only | Macro:UpdateProgress, Macro:CollapsedOrVisible | Read last |

### Step 1.2: Read the Blueprint's variables

Use `unreal-object-operation` skill's `DescribeObject` to get all UPROPERTY variables on the Blueprint's CDO. This reveals the full state model — every variable the Blueprint uses.

```json
{"object":"/Script/UnrealClientProtocol.Default__ObjectOperationLibrary","function":"DescribeObject","params":{"ObjectPath":"<blueprint_default_object_path>"}}
```

The CDO path for a Blueprint class `MyBlueprint_C` in package `/Game/BP/MyBlueprint` is:
`/Game/BP/MyBlueprint.Default__MyBlueprint_C`

### Step 1.3: Build a section dependency map

Before reading graph content, infer dependencies from section names:

- `Function:Initialize` likely calls `Function:SetupRT`, `Function:SetCaptureMesh`, etc.
- `EventGraph` likely calls most functions and responds to UI events
- Macros are called by functions — read the caller first, then the macro when you encounter it

## Phase 2 — Systematic Reading

**Rule: Read sections in dependency order, not alphabetical order. Process each section completely before moving to the next.**

### Reading strategy

1. **Read one section at a time** — keep output manageable
2. **Start with entry points** — EventGraph first, then Construct/PreConstruct
3. **Follow the call chain** — when a section calls `Function:Foo`, queue `Function:Foo` for reading
4. **Use a SubAgent for each section's pseudocode translation** — see below

### Use SubAgents for pseudocode translation

**For each section you read, launch a SubAgent to translate the NodeCode into pseudocode.** This is critical for large Blueprints because:

- Raw NodeCode for a 50-node function easily fills 5KB+ of text — it will crowd out your reasoning context
- SubAgent processes the NodeCode in isolation, returns a compact pseudocode summary
- You keep only the pseudocode in your main context, staying focused on the big picture

**SubAgent prompt template:**

> Translate the following Blueprint NodeCode into pseudocode. Trace execution flow from entry nodes, resolve all data dependencies into inline expressions.
>
> ```
> (paste the ReadGraph output here)
> ```
>
> Return:
> 1. Pseudocode (one line per statement, with comments for non-obvious logic)
> 2. Summary: what this section does, what variables it reads/writes, what functions it calls

**Workflow per section:**

1. ReadGraph → get NodeCode
2. Launch SubAgent with the NodeCode → get pseudocode back
3. Record the pseudocode summary in your main context
4. Move to next section

### Reading template

Read one section at a time:

```json
{"object":"/Script/UnrealClientProtocolEditor.Default__NodeCodeEditingLibrary","function":"ReadGraph","params":{"AssetPath":"<path>","Section":"Function:Initialize"}}
```

### Handling large outputs

If a single section's ReadGraph output exceeds ~50KB (e.g., a 200+ node EventGraph):

1. Read it alone (not batched with other sections)
2. If the Shell output is written to a file, split and read in chunks
3. Focus on extracting: **node types, function calls, variable reads/writes, and link topology**
4. For EventGraph specifically, identify all **event handlers** (Event:*, K2Node_ComponentBoundEvent) as separate logical blocks

### Pseudocode translation

**CRITICAL: After reading each section, immediately translate the NodeCode into pseudocode.** This is the most important step — NodeCode describes structure, not logic. You must reconstruct the control flow and data flow to understand what the section actually does.

1. Find the entry node (FunctionEntry, Event, CustomEvent)
2. Follow `then`/`execute` exec links to build statement order
3. At each node, resolve data inputs by tracing backwards through data links
4. Collapse math/utility chains into inline expressions
5. Branch → `if/else`, ForEachLoop → `for`, Sequence → sequential blocks

### Section summary format

After translating each section, record a summary like:

```
## Function:Initialize
- Pseudocode:
    if Orthographic:
        OrthoWidth = ObjectRadius * 2
        ProjectionType = Orthographic
    else:
        FOVAngle = Clamp(CameraFOV, 10, 170)
        ProjectionType = Perspective
    SceneCapture.TextureTarget = CreateRT(...)
    SetupShowOnlyList(SceneCapture, TargetMeshes)
    DynamicMesh.SetMaterial(0, CreateMID(BaseMaterial))
    ResetAllCaptureModes()
- Calls: SetupRTAndSaveList, SetCaptureMeshAndSizeInfo, SetupOctahedronLayout, ClearRenderTargets, CreateAndSetupMIDs, ResetAllCaptureModes
- Reads: SceneCaptureComponent2D, StaticMeshComponent, DynamicMeshComponent, CaptureUsingGBuffer, Orthographic, CameraDistance, ObjectRadius
- Writes: OrthoWidth, FOVAngle, ProjectionType, TextureTarget, CurrentMapIndex
- Nodes: 47
```

## Phase 3 — Translation

When converting Blueprint to C++, follow these rules:

### Variable mapping

1. All Blueprint variables → UPROPERTY members on a UObject or grouped into settings/state structs
2. Blueprint enums (UserDefinedEnum) → C++ UENUM with **different names** to avoid conflicts
3. Blueprint structs (UserDefinedStruct) → C++ USTRUCT with **different names**
4. Local variables in functions → local C++ variables

### Function mapping

| Blueprint construct | C++ equivalent |
|---|---|
| Function | Member function |
| Macro | Private helper function (inline the logic) |
| CustomEvent | Member function (called via delegate or directly) |
| Event:Construct / Event:Tick | Override virtual functions |
| K2Node_ComponentBoundEvent | Delegate binding in initialization |
| Delay / SetTimerByEvent | FTimerManager::SetTimer |
| ForEachLoop macro | Range-based for loop |
| Sequence node | Sequential statements |
| Branch node | if/else |
| Select node | Ternary or switch |
| SwitchOnName/Enum | switch statement |

### Node-by-node translation

For each node in a section, translate directly:

| Node text | C++ code |
|---|---|
| `CallFunction:KismetMathLibrary.Multiply_VectorFloat` | `FVector Result = Vec * Scalar;` |
| `CallFunction:KismetRenderingLibrary.DrawMaterialToRenderTarget` | `UKismetRenderingLibrary::DrawMaterialToRenderTarget(World, RT, MID);` |
| `CallFunction:KismetMaterialLibrary.SetVectorParameterValue` | `UKismetMaterialLibrary::SetVectorParameterValue(World, MPC, Name, Value);` |
| `VariableGet:MyVar` | `MyVar` (member access) |
| `VariableSet:MyVar` | `MyVar = Value;` |
| `K2Node_IfThenElse` | `if (Condition) { ... } else { ... }` |
| `K2Node_ForEachLoop` | `for (auto& Elem : Array) { ... }` |
| `K2Node_DynamicCast` | `if (auto* Casted = Cast<TargetClass>(Obj)) { ... }` |
| `K2Node_Self` | `this` |

### Execution flow reconstruction

Links define the execution order. Reconstruct C++ control flow by:

1. Find the entry node (FunctionEntry, Event, CustomEvent)
2. Follow `then`/`execute` exec pins to build the statement sequence
3. At Branch nodes, create if/else blocks
4. At Sequence nodes, emit statements in order (then_0, then_1, ...)
5. Data flow pins become variable assignments or inline expressions

### Material / MPC references

When the Blueprint references content assets (materials, MPC, textures):

1. Record every asset path referenced in node properties (e.g., `pin.Collection:/Game/MPC/MyMPC.MyMPC`)
2. In C++, load these via `LoadObject<T>(nullptr, TEXT("/Path/To/Asset"))` or `ConstructorHelpers::FObjectFinder`
3. If creating an independent plugin, copy the referenced assets and update all paths

## Phase 4 — Verification

### Completeness check

After translation, verify every section has been processed:

1. Re-read the Outline output
2. Check off each section against your C++ implementation
3. Any unprocessed section = missing functionality

### Compile and test

1. Build with UBT using `-Module=YourModule` to isolate compilation
2. Fix errors iteratively
3. If UE editor is running, use UCP to test the C++ code at runtime

## Anti-Patterns

| Bad practice | Why it fails | Correct approach |
|---|---|---|
| Read 4 sections, write all C++ | 90% of logic is guessed, not translated | Read every section, translate each one |
| Read all 40 sections in one batch | Output too large, context overflow | Batch 3-5 at a time |
| Skip macros ("they're just helpers") | Macros contain critical logic (RT creation, mip chain, mesh saving) | Read every macro that's called |
| Use general UE knowledge instead of reading the graph | Actual implementation may differ from standard patterns | Always read first, then translate what you see |
| Translate EventGraph as one monolithic function | EventGraph has many independent event handlers | Split each event handler into its own C++ function |
