# Codebase Spec Extractor（`codebase-spec-extractor`）

从既有代码库中提炼**可复刻**的工程规格文档。目标是产出“实现级”的说明：即使换技术栈，也能仅凭 spec 复现同等行为（无需看到原始代码）。

## 包含内容

- `SKILL.md`
- `scripts/`
- `references/`

## 安装

> 安装 skill 的本质是：让你的编码工具 / Agent 运行器能发现这个目录里的 `SKILL.md`（通常是放进某个 `skills/` 目录，或使用工具内置的“从 Git 安装”能力）。

### 方式 A：复制安装

在仓库根目录执行：

把 `SKILLS_DIR` 改成你的工具会扫描的 skills 目录（示例：`~/.codex/skills`、`~/.claude/skills`、`~/.config/opencode/skills` 等）：

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/codebase-spec-extractor"
cp -R agent/skills/codebase-spec-extractor "$SKILLS_DIR/codebase-spec-extractor"
```

### 方式 B：软链接安装

在仓库根目录执行：

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/codebase-spec-extractor"
ln -s "$(pwd)/agent/skills/codebase-spec-extractor" "$SKILLS_DIR/codebase-spec-extractor"
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

安装时选择 `codebase-spec-extractor`（仓库内路径：`agent/skills/codebase-spec-extractor`）。

验证/读取：

```bash
npx openskills list
npx openskills read codebase-spec-extractor
```

### 方式 D：直接给工具一个 GitHub 链接

不少编码工具支持“从 GitHub/Git URL 安装/加载 skill”。如果你的工具支持，指向本仓库并选择/定位到 `agent/skills/codebase-spec-extractor`。

### 安装完成后

不少工具需要重启/新开会话，才会重新扫描 skills。

## 用法

注意：本技能附带的脚本主要用于**辅助发现问题/缺口**（heuristic checks），不能作为“规格已完整/行为已等价”的证明。

在技能目录下执行：

```bash
# 1) 快速扫描项目类型/技术栈/结构
bash scripts/discover_project.sh <project_root> > discovery.md

# 2) 生成待文档化元素清单（便于逐项写 spec）
bash scripts/inventory_elements.sh <project_root> > inventory.md

# 3) 生成 spec/ 文档骨架目录
bash scripts/generate_skeleton.sh spec

# 4) Code → Spec：启发式缺口扫描
bash scripts/verify_coverage.sh <project_root> spec > coverage.md

# 5) Spec → Code：校验 Source 锚点是否能映射回代码（推荐）
# 需要你先在 spec markdown 里加类似：`Source: path/to/file.ext`
bash scripts/verify_implementation.sh spec <project_root> > spec_to_code.md
```
