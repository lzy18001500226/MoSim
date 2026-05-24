---
name: unreal-widget-editing
description: Edit UMG Widget Blueprint UI layouts via text (ReadGraph/WriteGraph). Use when the user asks to add, remove, or rearrange UI widgets, change widget properties, or modify the visual hierarchy of a Widget Blueprint.
---

# Widget Editing

Edit UMG Widget Blueprint UI layouts via a text-based tree representation. The widget tree (visual hierarchy) uses the `[WidgetTree]` section. For editing the **event graph** and **functions** of a Widget Blueprint, use the `unreal-blueprint-editing` skill — Widget Blueprints are Blueprints, so EventGraph/Function/Variables sections work identically.

**Prerequisite**: UE editor running with UCP plugin enabled.

## API

CDO: `/Script/UnrealClientProtocolEditor.Default__NodeCodeEditingLibrary`

| Function | Params | Description |
|----------|--------|-------------|
| `Outline` | `AssetPath` | Returns all sections: `[WidgetTree]`, `[Variables]`, `[EventGraph]`, `[Function:Name]`, etc. |
| `ReadGraph` | `AssetPath`, `Section` | Returns text. Use `"WidgetTree"` for the UI layout. |
| `WriteGraph` | `AssetPath`, `Section`, `GraphText` | Overwrite the widget tree. |

## Section Types for Widget Blueprints

A Widget Blueprint's Outline returns both widget tree and graph sections:

| Section | Handler | Description |
|---------|---------|-------------|
| `WidgetTree` | WidgetTreeSectionHandler | UI widget hierarchy |
| `Variables` | BlueprintSectionHandler | Blueprint variables |
| `EventGraph` | BlueprintSectionHandler | Event graph logic |
| `Function:<Name>` | BlueprintSectionHandler | Blueprint functions |

## WidgetTree Text Format

The widget tree uses **indentation-based** text format where depth represents parent-child relationships:

```
[WidgetTree]
CanvasPanel_0: {"Type":"CanvasPanel"}
  Image_BG: {"Type":"Image", "Slot":{"Anchors":"(Minimum=(X=0,Y=0),Maximum=(X=1,Y=1))", "Offsets":"(Left=0,Top=0,Right=0,Bottom=0)"}}
  VerticalBox_Main: {"Type":"VerticalBox", "Slot":{"Anchors":"(Minimum=(X=0.5,Y=0.5),Maximum=(X=0.5,Y=0.5))"}}
    TextBlock_Title: {"Type":"TextBlock", "Text":"Hello World", "Slot":{"HorizontalAlignment":"HAlign_Center"}}
    Button_Submit: {"Type":"Button", "Slot":{"Padding":"(Left=0,Top=10,Right=0,Bottom=0)"}, "bIsVariable":true}
      TextBlock_BtnLabel: {"Type":"TextBlock", "Text":"Submit"}
```

### Format Rules

- **Indentation = hierarchy**: 2 spaces per level. Root widget has no indentation.
- **Widget name is the key**: `TextBlock_Title`, `Button_Submit`, etc. These are the widget's `GetName()`.
- **`Type`**: Widget class name (e.g., `CanvasPanel`, `TextBlock`, `Button`, `Image`). Resolved via reflection.
- **`Slot`**: Layout properties from the parent panel's slot type, as a nested JSON object.
- **`bIsVariable`**: If `true`, the widget is accessible from the Blueprint graph (e.g., for binding events or setting properties at runtime). Only serialized when `true`.
- **Other properties**: Non-default widget properties, serialized via UE reflection.

### Slot Properties by Panel Type

Different panel types use different slot types with different layout properties:

**CanvasPanelSlot** (parent is CanvasPanel):
- `LayoutData.Anchors`: `(Minimum=(X=0,Y=0),Maximum=(X=1,Y=1))` — anchor presets
- `LayoutData.Offsets`: `(Left=0,Top=0,Right=0,Bottom=0)` — position/size offsets
- `LayoutData.Alignment`: `(X=0.5,Y=0.5)` — pivot alignment
- `bAutoSize`: `true/false`
- `ZOrder`: integer

**VerticalBoxSlot / HorizontalBoxSlot** (parent is VerticalBox/HorizontalBox):
- `Padding`: `(Left=0,Top=10,Right=0,Bottom=0)`
- `Size`: `(SizeRule=Fill,Value=1.0)` or `(SizeRule=Auto,Value=1.0)`
- `HorizontalAlignment`: `HAlign_Fill`, `HAlign_Left`, `HAlign_Center`, `HAlign_Right`
- `VerticalAlignment`: `VAlign_Fill`, `VAlign_Top`, `VAlign_Center`, `VAlign_Bottom`

**OverlaySlot** (parent is Overlay):
- `Padding`: `(Left=0,Top=0,Right=0,Bottom=0)`
- `HorizontalAlignment`: same as above
- `VerticalAlignment`: same as above

**GridSlot** (parent is GridPanel):
- `Row`, `Column`: integer
- `RowSpan`, `ColumnSpan`: integer

### Common Widget Types

| Type | Description | Key Properties |
|------|-------------|----------------|
| `CanvasPanel` | Free-form positioning container | (none typical) |
| `VerticalBox` | Stack children vertically | (none typical) |
| `HorizontalBox` | Stack children horizontally | (none typical) |
| `Overlay` | Stack children on top of each other | (none typical) |
| `GridPanel` | Grid layout | (none typical) |
| `ScrollBox` | Scrollable container | `Orientation` |
| `SizeBox` | Constrain child size | `WidthOverride`, `HeightOverride` |
| `Border` | Single child with background | `Background` |
| `TextBlock` | Display text | `Text`, `Font`, `ColorAndOpacity` |
| `RichTextBlock` | Rich text display | `Text` |
| `Image` | Display image/texture | `Brush` |
| `Button` | Clickable button | `WidgetStyle` |
| `CheckBox` | Toggle checkbox | `IsChecked` |
| `Slider` | Value slider | `Value`, `MinValue`, `MaxValue` |
| `ProgressBar` | Progress indicator | `Percent` |
| `EditableText` | Single-line text input | `Text`, `HintText` |
| `EditableTextBox` | Single-line text input with box | `Text`, `HintText` |
| `MultiLineEditableText` | Multi-line text input | `Text` |
| `ComboBoxString` | Dropdown selection | `DefaultOptions` |
| `SpinBox` | Numeric input | `Value`, `MinValue`, `MaxValue` |
| `Spacer` | Empty spacing widget | `Size` |
| `WidgetSwitcher` | Show one child at a time | `ActiveWidgetIndex` |

## Workflow

1. **Outline** — see available sections (WidgetTree + graph sections)
2. **ReadGraph("WidgetTree")** — get the UI hierarchy
3. **Understand the tree** — indentation shows parent-child relationships
4. **Modify** — add/remove/rearrange widgets, change properties
5. **WriteGraph("WidgetTree", text)** — apply changes

For logic changes (event bindings, property updates at runtime):
1. **ReadGraph("EventGraph")** — use the `unreal-blueprint-editing` skill
2. Reference widgets by name (widgets with `bIsVariable:true` are accessible in graphs)

## Key Rules

1. **Indentation matters**: 2 spaces per level. Incorrect indentation will create wrong parent-child relationships.
2. **Widget names must be unique** within the tree.
3. **Root widget** (depth 0) must be a panel widget (CanvasPanel, VerticalBox, etc.).
4. **Only panel widgets** can have children. Don't indent a child under a non-panel widget like TextBlock.
5. **Set `bIsVariable:true`** on any widget you need to reference from the Blueprint graph.
6. **ReadGraph before WriteGraph** — always read first to understand the current structure.
7. **Slot properties** depend on the parent panel type. A widget under VerticalBox uses VerticalBoxSlot properties, not CanvasPanelSlot.
8. All operations support **Undo** (Ctrl+Z).

## Error Handling

- Unknown widget class: `"Unknown widget class: ..."`.
- Failed to create widget: `"Failed to create widget: ..."`.
- Check `diff` object in response for `nodes_added`, `nodes_removed`.
