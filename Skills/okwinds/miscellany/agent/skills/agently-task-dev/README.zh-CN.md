# agently-task-dev

Use only when the user explicitly wants to build with the Agently framework (mentions Agently/agently/OpenAICompatible/TriggerFlow/ToolExtension/ChromaCollection, or says “用 Agently 做/用 agently 做”). Deliver runnable code plus regression tests validating schema/ensure_keys and streaming (delta/instant/streaming_parse), with optional tools (Search/Browse/MCP), TriggerFlow orchestration, KB (ChromaDB), and serviceization (SSE/WS/HTTP). Do not use for generic streaming/testing questions that are not about Agently, or for prompt-only writing without tests/structure.

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
rm -rf "$SKILLS_DIR/agently-task-dev"
cp -R agent/skills/agently-task-dev "$SKILLS_DIR/agently-task-dev"
```

### 方式 B：软链接安装

在仓库根目录执行：

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/agently-task-dev"
ln -s "$(pwd)/agent/skills/agently-task-dev" "$SKILLS_DIR/agently-task-dev"
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

安装时选择 `agently-task-dev`（仓库内路径：`agent/skills/agently-task-dev`）。

验证/读取：

```bash
npx openskills list
npx openskills read agently-task-dev
```

### 方式 D：直接给工具一个 GitHub 链接

不少编码工具支持“从 GitHub/Git URL 安装/加载 skill”。如果你的工具支持，指向本仓库并选择/定位到 `agent/skills/agently-task-dev`。

### 安装完成后

不少工具需要重启/新开会话，才会重新扫描 skills。
