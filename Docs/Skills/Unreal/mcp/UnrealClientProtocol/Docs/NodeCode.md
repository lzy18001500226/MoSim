# NodeCode V2 Architecture

NodeCode is a text-based intermediate representation (IR) for Unreal Engine node graphs. It converts visual node graphs into a concise, human-readable text format that AI agents can understand, reason about, and modify — then writes the changes back to the live graph via incremental diff.

## API

CDO: `/Script/UnrealClientProtocolEditor.Default__NodeCodeEditingLibrary`

| Function | Params | Description |
|----------|--------|-------------|
| `Outline` | `AssetPath` | Returns all Section headers for the asset |
| `ReadGraph` | `AssetPath`, `Section` (optional) | Returns text. Empty Section = all Sections. |
| `WriteGraph` | `AssetPath`, `Section`, `GraphText` | Overwrite Section content. Empty GraphText = delete Section. |

Semantics: **read a range, write a range, overwrite within that range, leave everything else untouched.**

## Text Format

### Section Headers

```
[Type:Name]    — named (Function:Foo, Composite:Bar)
[Type]         — singleton (Material, EventGraph, AnimGraph)
```

Type routes to the appropriate handler. Current types:

| Type | Asset | Description |
|------|-------|-------------|
| `EventGraph` | Blueprint | Main event graph or named ubergraph page |
| `Function` | Blueprint | Function graph |
| `Macro` | Blueprint | Macro graph |
| `Variables` | Blueprint | Variable definitions (data section) |
| `Material` | Material | Complete main material graph |
| `Composite` | Material | Composite subgraph |
| `Properties` | Material | Material properties (ShadingModel, BlendMode, etc.) |
| `WidgetTree` | Widget Blueprint | UI widget hierarchy (indentation-based tree format) |

### Node Lines

```
N<idx> <ClassName> {Key:Value, Key:Value} #<guid>
```

- Properties in `{...}`, single line
- Values are loose JSON: parsed as JSON first, fallback to UE ImportText
- GUID preserved for existing nodes, omitted for new nodes

### Connection Lines

```
  > OutputPin -> N<target>.InputPin
  > OutputPin -> [GraphOutput]
  > -> N<target>.InputPin              (omit OutputPin = single-output node)
```

Output direction only (`>`), indented under the owning node.

### Properties / Variables Sections

```
[Properties]
ShadingModel: MSM_DefaultLit
BlendMode: BLEND_Opaque
TwoSided: true

[Variables]
Health: {"PinCategory":"real", "PinSubCategory":"double", "DefaultValue":"100.0"}
bIsAlive: {"PinCategory":"bool", "DefaultValue":"true"}
```

`key: value` format, one per line. Values are loose JSON.

Variables use `FEdGraphPinType` reflection fields directly (`PinCategory`, `PinSubCategory`, `PinSubCategoryObject`, `ContainerType`).

## Data Flow

```
Read:   UE Asset ──→ SectionHandler.Read() ──→ FNodeCodeSectionIR ──→ DocumentToText ──→ Text
Write:  Text ──→ ParseDocument ──→ FNodeCodeDocumentIR ──→ SectionHandler.Write() ──→ UE Asset
```

## IR Structures

Defined in `Private/NodeCode/NodeCodeTypes.h`:

| Struct | Fields | Description |
|--------|--------|-------------|
| `FNodeCodeNodeIR` | Index, ClassName, Guid, Properties, SourceObject | A single node |
| `FNodeCodeLinkIR` | FromNodeIndex, FromOutputName, ToNodeIndex, ToInputName, bToGraphOutput | A connection |
| `FNodeCodeGraphIR` | Nodes, Links | A complete node graph |
| `FNodeCodeSectionIR` | Type, Name, Graph, Properties, RawText | A document section (graph, data, or raw text) |
| `FNodeCodeDocumentIR` | Sections | Multi-section document |
| `FNodeCodeDiffResult` | NodesAdded/Removed/Modified, LinksAdded/Removed | Write result |

## Architecture

### Handler Interface

```cpp
class INodeCodeSectionHandler
{
    virtual bool CanHandle(UObject* Asset, const FString& Type) const = 0;
    virtual TArray<FNodeCodeSectionIR> ListSections(UObject* Asset) = 0;
    virtual FNodeCodeSectionIR Read(UObject* Asset, const FString& Type, const FString& Name) = 0;
    virtual FNodeCodeDiffResult Write(UObject* Asset, const FNodeCodeSectionIR& Section) = 0;
    virtual bool CreateSection(UObject* Asset, const FString& Type, const FString& Name) = 0;
    virtual bool RemoveSection(UObject* Asset, const FString& Type, const FString& Name) = 0;
};
```

Implementations:
- `FBlueprintSectionHandler` — EventGraph / Function / Macro / Variables
- `FMaterialSectionHandler` — Material / Composite / Properties
- `FWidgetTreeSectionHandler` — WidgetTree

Handlers register to `FNodeCodeSectionHandlerRegistry`. The unified `UNodeCodeEditingLibrary` dispatches by asset type + section type.

### WriteGraph Flow

```
1. Parse GraphText → FNodeCodeDocumentIR
2. If Section param is non-empty, validate text matches that section
3. For each section:
   a. Find handler
   b. Section doesn't exist → handler.CreateSection()
   c. handler.Write() → internal incremental diff (BuildIR → MatchNodes → Delete/Create/Update/DiffLinks)
4. If GraphText is empty and Section is non-empty → handler.RemoveSection()
5. Entire operation wrapped in FScopedTransaction
```

### Node Matching Strategy

Three-pass matching (shared by Blueprint and Material):

1. **GUID match** — exact, most reliable
2. **ClassName + Properties fingerprint** — uses all serialized properties as auxiliary fingerprint
3. **ClassName alone** — last resort, pairs by order

**GUID is the only reliable identity.** Losing GUIDs on same-type multi-node scenarios causes unreliable matching.

### Blueprint Node Encoding

`IBlueprintNodeEncoder` registry (internal to Blueprint handler):

| Text Format | UE Node Type |
|-------------|-------------|
| `CallFunction:<Class>.<Func>` | `UK2Node_CallFunction` (external) |
| `CallFunction:<Func>` | `UK2Node_CallFunction` (self) |
| `VariableGet:<Var>` | `UK2Node_VariableGet` |
| `VariableSet:<Var>` | `UK2Node_VariableSet` |
| `CustomEvent:<Name>` | `UK2Node_CustomEvent` |
| `Event:<Name>` | `UK2Node_Event` |
| `FunctionEntry` | `UK2Node_FunctionEntry` (protected) |
| `FunctionResult` | `UK2Node_FunctionResult` (protected) |

Other node types use their raw UE class name (e.g. `K2Node_IfThenElse`).

### Class Name Resolution

All domains share a unified `FNodeCodeClassCache` singleton for class name resolution. Each domain registers its base class at startup:

```
FNodeCodeClassCache::Get().RegisterBaseClass(UEdGraphNode::StaticClass());
FNodeCodeClassCache::Get().RegisterBaseClass(UMaterialExpression::StaticClass());
FNodeCodeClassCache::Get().RegisterBaseClass(UWidget::StaticClass());
```

The cache uses `GetDerivedClasses` to discover all subclasses via reflection, then maps short names (e.g. `K2Node_IfThenElse`, `TextureSample`, `CanvasPanel`) to UClass pointers. No hardcoded class lists — new engine classes are automatically available.

### Material Expression Encoding

Material expressions use their UE class name directly via `FNodeCodeClassCache` (e.g. `TextureSample`, `ScalarParameter`, `Multiply`). No semantic encoding needed.

Special property handlers (`IMaterialPropertyHandler` registry) for:
- `UMaterialExpressionCustom` — `InputNames` array
- `UMaterialExpressionSwitch` — `SwitchInputNames` array
- `UMaterialExpressionSetMaterialAttributes` — `Attributes` GUIDs

## Supported Asset Types

### Blueprint

**Sections:** `[Variables]`, `[EventGraph]`, `[Function:Name]`, `[Macro:Name]`

- CreateSection/RemoveSection supported for Function and Macro
- Variables use `FEdGraphPinType` reflection serialization
- Pin defaults set via `Schema::TrySetDefaultValue` for correct DefaultObject/DefaultTextValue handling
- Auto-recompile after write

### Material

**Sections:** `[Properties]`, `[Material]`, `[Composite:Name]`

- `[Material]` = complete main graph (all non-composite nodes), single read/write
- `[Composite:Name]` = physically isolated subgraphs
- Output pins expressed as `> -> [BaseColor]` graph output connections
- Auto-recompile, relayout, and editor UI refresh after write

### Widget Blueprint

**Sections:** `[WidgetTree]` (plus all Blueprint sections: `[Variables]`, `[EventGraph]`, `[Function:Name]`, `[Macro:Name]`)

Widget Blueprints are Blueprints, so their graph sections are handled by `FBlueprintSectionHandler`. The `[WidgetTree]` section is handled by a separate `FWidgetTreeSectionHandler`.

The WidgetTree uses an **indentation-based tree format** (not node graph format):

```
CanvasPanel_0: {"Type":"CanvasPanel"}
  TextBlock_Title: {"Type":"TextBlock", "Text":"Hello World", "Slot":{"HorizontalAlignment":"HAlign_Center"}}
  Button_Submit: {"Type":"Button", "Slot":{"Padding":"(Left=0,Top=10,Right=0,Bottom=0)"}, "bIsVariable":true}
    TextBlock_BtnLabel: {"Type":"TextBlock", "Text":"Submit"}
```

- 2-space indentation per level represents parent-child relationships
- Widget name is the line key, JSON value contains Type, Slot, and widget properties
- Widget type names resolved via `FNodeCodeClassCache` (same as other domains)

## Adding Support for a New Graph Type

1. **Create a SectionHandler** implementing `INodeCodeSectionHandler`
2. **Register** it in `NodeCodeEditingLibrary.cpp`'s auto-register block
3. **Create a Skill** at `Skills/unreal-<domain>-editing/SKILL.md`

The handler must implement:
- `ListSections()` — enumerate available sections
- `Read()` — serialize a section to `FNodeCodeSectionIR`
- `Write()` — diff and apply changes from `FNodeCodeSectionIR`
- `CreateSection()` / `RemoveSection()` — structural operations

The text format, parsing, and diff infrastructure are shared.
