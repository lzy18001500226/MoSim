> **在 Skill 包中的位置**：`ty-sysplorer-modeling-rules` / `references/modelica_diagram_connect_semantics.md`，与 `modelica_style_guide.md` Part 3、「七门闸」`seven_gates_workflow.md` Gate 6 及 **`smart_layout` / `graph_json`** 管线配合使用。**范围**：原理图上的 **`connect` 方程语义**、**`Placement`**、**`connect` 上的 `Line`**；非 Modelica 全语言语法说明。

下文只说明**与原理图上“组件在哪儿、与谁怎么连”相关的语法语义**：实例在图解中的定位，以及 `connect` 如何生成连接方程。类级 `Icon` / `Diagram` 里大量 `Rectangle`、`Text`、`Bitmap` 等图元仅决定外观，与方程无关，此处不展开。

---

## 1. `connect`：连接方程语义（建模层）

```modelica
connect(a, b);
```

`connect` 的语义由连接器类型决定，工具据此生成方程，**不是**“画一条线”本身。

- 对 **`flow` 变量**：生成守恒类方程（例如 `a.i + b.i = 0`）。
- 对 **势变量**（非 `flow`）：生成相等约束（例如 `a.v = b.v`）。
- 复合连接器按成员递归展开。

修改 `connect` 的两端或连接器类型会改变模型；修改仅用于画线的折点不会改变上述方程。

---

## 2. `Placement`：组件在图解中的显示位置

实例上的 `Placement` 告诉工具该组件在 **diagram** 视图中的位置与朝向，用于对齐端口、作为连线锚点参考。

```modelica
Modelica.Blocks.Sources.Step step(
  annotation(Placement(transformation(extent={{-80,-10},{-60,10}}))));
```

常见字段含义要点：

- **`transformation(extent=...)`**：图解中占用的矩形范围（位置与尺度）。
- **`rotation`**、**`origin`**：旋转与参考原点。
- **`iconTransformation`**：与图标层对应的变换（影响端口在图标上的几何关系）。

删除或改写 `Placement` 一般**不改变**方程，只改变编辑器中的摆放与走线参考；若工具用布局推断连线，可能影响自动路由，但不替代 `connect` 的数学含义。

---

## 3. 连接语句上的 `Line`：仅图解走线（显示层）

`connect` 可带 `annotation(Line(...))`，用于指定该连接在图上的折线路径等，供工具渲染。

```modelica
connect(sensor.out, controller.u)
  annotation(Line(points={{10,0},{20,0},{30,0}}));
```

- **`points`**：折线顶点序列；怎么走线**不改变** `connect` 生成的方程。
- 文档中若需区分层次：**`connect` = 结构/方程**；**`Line` = 可选的图解几何提示**。

不同工具对额外图形属性的支持不一；与方程无关的线色、线型等属于纯显示，需要时查工具手册即可，此处不列为建模语义。

---

## 4. 层次对照（便于与 `graph_json` / 布局管线对齐）

| 构造 | 作用层次 |
|------|----------|
| `connect(...)` | 定义连接关系并生成连接方程 |
| `Placement(...)` | 定义实例在原理图中的位置与变换 |
| `connect` 上的 `Line(...)` | 仅定义该连接在图上的折线路径 |

删除 `Line` 注解：模型通常仍可求解，仅图上缺省走线或需重算路由。删除或改错 `connect`：模型语义改变。

---

## 5. 综合示例（组件位置 + 连接方程 + 可选走线）

```modelica
model Example
  Modelica.Blocks.Sources.Step step
    annotation(Placement(transformation(extent={{-80,-10},{-60,10}})));

  Modelica.Blocks.Math.Gain gain(k=2)
    annotation(Placement(transformation(extent={{-20,-10},{0,10}})));

  Modelica.Blocks.Sinks.RealOutput y
    annotation(Placement(transformation(extent={{40,-10},{60,10}})));

equation
  connect(step.y, gain.u)
    annotation(Line(points={{-59,0},{-20,0}}));

  connect(gain.y, y)
    annotation(Line(points={{1,0},{40,0}}));
end Example;
```

- **`Placement`**：各块在图中的占位。
- **`connect`**：`step.y`↔`gain.u`、`gain.y`↔`y` 的方程生成。
- **`Line`**：上述两条连接在图上的折点。

---

## 6. 一句话概括

**`connect` 决定连什么、方程怎么来；`Placement` 决定组件在图上放哪儿；`Line` 只决定这条连接在图上怎么画。**
