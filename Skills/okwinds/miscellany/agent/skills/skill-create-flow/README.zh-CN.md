# skill-create-flow

Create new high-quality agent skills with a standalone, repeatable workflow (no dependency on other skills). Use when you want to go from a vague skill idea → narrow scope → extract expert frameworks → write SKILL.md + examples/evals/index/changelog artifacts → self-validate with test prompts.

## 适合创建的技能类型

这个技能最适合创建**基于流程的 Agent 技能**，其核心价值来自于遵循结构化的方法论，而非简单的知识检索。适合的技能类型包括：

- **方法论型技能**：如调试流程、代码审查、规格编写、系统化问题解决等需要遵循既定步骤的技能
- **决策型技能**：需要专业判断的领域，如架构决策、UX 设计、商业策略等
- **多步骤工作流**：需要按顺序执行多个操作且产出明确的技能
- **质量导向型技能**：输出质量有"优秀 vs 一般"的明显区分，且过程质量很重要的技能

不太适合：
- 纯参考/查询型技能（使用知识检索更合适）
- 简单的一次性命令（直接调用工具即可）
- 依赖外部资源的技能（此流程产出的是独立技能）

## 包含内容

- `SKILL.md`
- `scripts/`（可选）
- `references/`（可选）
- `assets/`（可选）

## 安装

> 安装 skill 的本质是：让你的编码工具 / Agent 运行器能发现这个目录里的 `SKILL.md`（通常是放进某个 `skills/` 目录，或使用工具内置的“从 Git 安装”能力）。

### 方式 A：复制安装

在仓库根目录执行：

把 `SKILLS_DIR` 改成你的工具会扫描的 skills 目录（示例：`~/.codex/skills`、`~/.claude/skills`、`~/.config/opencode/skills` 等）：

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/skill-create-flow"
cp -R agent/skills/skill-create-flow "$SKILLS_DIR/skill-create-flow"
```

### 方式 B：软链接安装

在仓库根目录执行：

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/skill-create-flow"
ln -s "$(pwd)/agent/skills/skill-create-flow" "$SKILLS_DIR/skill-create-flow"
```

### 方式 C：用 openskills 从 GitHub/Git 安装

先准备 openskills：

- 需要 Node.js（建议 18+）。
- 不想安装：直接用 `npx openskills ...`（会自动下载并运行）。
- 想全局安装：`npm i -g openskills`（或 `pnpm add -g openskills`）。

从**可 clone 的仓库 URL** 安装（不要用 GitHub 的 `.../tree/...` 子目录链接）：

```bash
npx openskills install https://github.com/okwinds/miscellany
```

安装时选择 `skill-create-flow`（仓库内路径：`agent/skills/skill-create-flow`）。

验证/读取：

```bash
npx openskills list
npx openskills read skill-create-flow
```

### 方式 D：直接给工具一个 GitHub 链接

不少编码工具支持“从 GitHub/Git URL 安装/加载 skill”。如果你的工具支持，指向本仓库并选择/定位到 `agent/skills/skill-create-flow`。

### 安装完成后

不少工具需要重启/新开会话，才会重新扫描 skills。
