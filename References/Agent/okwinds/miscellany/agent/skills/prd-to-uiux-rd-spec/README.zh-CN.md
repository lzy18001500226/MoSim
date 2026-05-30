# prd-to-uiux-rd-spec

从产品 PRD 产出“复刻级可落地”的 UI/UX 研发规格文档包（目录同构骨架、公共基座、组件/页面契约、覆盖映射、索引与 worklog）。适用于需要把 PRD 转成前端可复刻实现的规格文档、UI/UX 研发规格、界面契约与验收标准的场景；避免用于只要视觉灵感/纯 UI 赏析或直接写代码实现的请求。

## 包含内容

- `SKILL.md`：工作流与输出契约
- `references/`：模板与检查清单
- `examples/`：最小示例
- `tests/`：eval prompts（自测用）
- `CHANGELOG.md`

## 安装

> 安装 skill 的本质是：让你的编码工具 / Agent 运行器能发现这个目录里的 `SKILL.md`（通常是放进某个 `skills/` 目录，或使用工具内置的“从 Git 安装”能力）。

### 方式 A：复制安装

在仓库根目录执行：

把 `SKILLS_DIR` 改成你的工具会扫描的 skills 目录（示例：`~/.codex/skills`、`~/.claude/skills`、`~/.config/opencode/skills` 等）：

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/prd-to-uiux-rd-spec"
cp -R agent/skills/prd-to-uiux-rd-spec "$SKILLS_DIR/prd-to-uiux-rd-spec"
```

### 方式 B：软链接安装

在仓库根目录执行：

```bash
SKILLS_DIR=~/.codex/skills
mkdir -p "$SKILLS_DIR"
rm -rf "$SKILLS_DIR/prd-to-uiux-rd-spec"
ln -s "$(pwd)/agent/skills/prd-to-uiux-rd-spec" "$SKILLS_DIR/prd-to-uiux-rd-spec"
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

安装时选择 `prd-to-uiux-rd-spec`（仓库内路径：`agent/skills/prd-to-uiux-rd-spec`）。

验证/读取：

```bash
npx openskills list
npx openskills read prd-to-uiux-rd-spec
```

### 方式 D：直接给工具一个 GitHub 链接

不少编码工具支持“从 GitHub/Git URL 安装/加载 skill”。如果你的工具支持，指向本仓库并选择/定位到 `agent/skills/prd-to-uiux-rd-spec`。

### 安装完成后

不少工具需要重启/新开会话，才会重新扫描 skills。
