# MWORKS 与 MATLAB 对照资料整理记录

> Source folder: `references/MWORKS高校星火计划资料包/MWORKS与MATLAB功能对照/`

## Source Files

| File | Size | Handling |
|---|---:|---|
| `01-MWORKS与其他科学计算软件对比.pdf` | about 25 MB | Converted by MinerU into `docs/mworks/converted/matlab_compat/MWORKS与其他科学计算软件对比.md` |
| `02-MWORKS简介及与MATLAB的对比V2.0.pdf` | about 5 MB | Converted by MinerU into `docs/mworks/converted/matlab_compat/MWORKS简介及与MATLAB的对比.md` |
| `03-MWORKS与MATLAB差异对照表（在线表格），可复制链接在线查看.txt` | small | Consolidated into `docs/mworks/converted/matlab_compat/MWORKS与MATLAB在线链接.md` |
| `04-与MATLAB的显著差异（用户手册链接），可直接复制在浏览器打开.txt` | small | Consolidated into `docs/mworks/converted/matlab_compat/MWORKS与MATLAB在线链接.md` |

## Why This Matters

Yes. This is one of the highest-value references for this project because many AI agents know MATLAB/Simulink patterns better than MWORKS/Syslab/Sysplorer. The conversion should make those patterns usable without guessing.

The project-local output is:

```text
docs/mworks/converted/matlab_compat/
  MWORKS与其他科学计算软件对比.md
  MWORKS与其他科学计算软件对比_images/
  MWORKS简介及与MATLAB的对比.md
  MWORKS简介及与MATLAB的对比_images/
  MWORKS与MATLAB在线链接.md
```

## What to Extract

1. MATLAB function or toolbox name.
2. MWORKS/Syslab/Sysplorer equivalent.
3. Known syntax or behavior difference.
4. Whether the equivalent can be verified through MCP.
5. Project usage: metrics, plotting, control design, model simulation, parameter estimation, or documentation.

## What Not to Extract

1. Long marketing descriptions.
2. Full screenshots or unindexed images.
3. Unverified MATLAB-only examples that do not map to MWORKS.
4. Large raw conversion outputs.

## Agent Rule

When a task sounds like MATLAB or Simulink:

```text
MathWorks pattern
  -> check MWORKS comparison docs
  -> check converted MWORKS docs
  -> verify with syslab/sysplorer MCP
  -> implement in project structure
  -> save evidence
```

Do not directly write MATLAB or Simulink commands into project workflows unless the task is explicitly about MATLAB reference material.

## Conversion Method Used

The two PDFs were converted with the MinerU precise API on `2026-05-09`. The two txt files contain URLs only, so they were merged manually into a link index.

Keep `docs/mworks/tmp/` as disposable conversion cache only. The agent-facing knowledge base is `docs/mworks/converted/matlab_compat/`.
