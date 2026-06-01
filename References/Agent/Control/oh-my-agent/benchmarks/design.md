# AI Harness Benchmark Design

Benchmark framework for comparing AI coding harness performance using a standardized creative prompt.

## Overview

Compare oh-my-agent against other Claude Code harnesses by running an identical prompt in isolated environments and scoring the results across code quality, feature completeness, UI/UX, and testing dimensions.

## Comparison Targets

| ID | Harness | Repository | Install Method |
|---|---|---|---|
| vanilla | Claude Code (no harness) | - | (none) |
| oma | oh-my-agent | first-fluke/oh-my-agent | `bunx oh-my-agent@latest` |
| omc | oh-my-claudecode | Yeachan-Heo/oh-my-claudecode | Plugin marketplace |
| ecc | everything-claude-code | affaan-m/everything-claude-code | `./install.sh --profile full` |
| superpowers | superpowers | obra/superpowers | Plugin marketplace |

## Control Variables

| Variable | Value |
|---|---|
| Prompt | `benchmarks/prompt.md` (identical raw prompt, no harness workflow) |
| Model | claude-opus-4-6 (1M context) |
| Effort | `--effort max` |
| Initial state | Empty directory + `git init` only |
| Isolation | `$HOME` override per harness |
| Execution mode | `claude -p` (non-interactive) |
| Permissions | `--dangerously-skip-permissions` (no human approval needed) |
| Budget cap | `--max-budget-usd 20` per run |
| Time limit | 60 minutes per run (`timeout 3600`) |
| Session persistence | `--no-session-persistence` |
| Human intervention | None (fully automated) |
| Runs | 1 per harness (reproducibility conditions documented) |

## Environment Isolation

Each harness runs with a separate `$HOME` to prevent global plugin contamination.

```bash
BASE=/tmp/oma-benchmark-$(date +%s)

for h in vanilla oma omc ecc superpowers; do
  mkdir -p $BASE/homes/$h $BASE/projects/$h
  git -C $BASE/projects/$h init
  git config --file $BASE/homes/$h/.gitconfig user.name "benchmark"
  git config --file $BASE/homes/$h/.gitconfig user.email "bench@test"
done
```

Execution per harness (fully unattended via `claude -p`):

```bash
HOME=$BASE/homes/{harness} \
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
OPENAI_API_KEY=${OPENAI_API_KEY:-} \
  timeout 3600 claude -p "$(cat $BASE/prompt.md)" \
    --dangerously-skip-permissions \
    --model claude-opus-4-6 \
    --effort max \
    --output-format json \
    --max-budget-usd 20 \
    --no-session-persistence \
    --add-dir $BASE/projects/{harness} \
    > $BASE/results/{harness}.json
```

`-p` (print) mode runs Claude Code non-interactively while still executing
multi-turn tool use. `--dangerously-skip-permissions` auto-approves all tool
invocations so no human approval is required. `--output-format json` returns
token usage and cost metadata for the meta-metrics report.

## Directory Structure

```
benchmarks/
├── run.sh                       # env setup + harness install + unattended exec
├── collect.sh                   # aggregate scores + generate report
├── prompt/
│   └── prompt.md
├── runs/                        # generated code per harness (excludes node_modules)
│   ├── vanilla/
│   ├── oma/
│   ├── omc/
│   ├── ecc/
│   └── superpowers/
├── scoring/
│   ├── checklist.json
│   ├── auto-score.sh            # build/test/lint/dependency checks
│   ├── visual-score.sh          # Chrome DevTools MCP screenshot + AI scoring
│   ├── score-prompt.md          # visual scoring prompt for Claude
│   └── manual-score.template.json
├── screenshots/                 # captured per harness via Chrome DevTools MCP
│   ├── vanilla/
│   ├── oma/
│   ├── omc/
│   ├── ecc/
│   └── superpowers/
└── results/
    ├── scores.json
    └── report.md
```

## Scoring: Feature Checklist

Total: 100 points across 8 categories.

### Project Setup (10pts)

| ID | Description | Auto |
|---|---|---|
| setup-nextjs | Next.js + TypeScript project configured | yes |
| setup-tailwind | Tailwind CSS configured | yes |
| setup-r3f | React Three Fiber + Drei dependencies | yes |
| setup-build | Build succeeds (`npm run build`) | yes |

### 3D World Builder (20pts)

| ID | Description | Auto |
|---|---|---|
| 3d-canvas | Three.js Canvas rendering | no |
| 3d-place | Object placement | no |
| 3d-move-rotate | Move / rotate / scale controls | no |
| 3d-color-texture | Color / texture modification | no |
| 3d-env-theme | Environment theme selection | no |
| 3d-animation | Simple animation / interaction | no |

### AI Creative Partner (15pts)

| ID | Description | Auto |
|---|---|---|
| ai-panel | AI sidebar / guide UI exists | no |
| ai-prompt | Idea prompting capability | no |
| ai-whatif | What-if question generation | no |
| ai-api | OpenAI API integration code | yes |

### Child Onboarding (10pts)

| ID | Description | Auto |
|---|---|---|
| onboard-flow | Onboarding screen / flow exists | no |
| onboard-simple | Startable within 1 minute UX | no |

### Play / Explore Mode (10pts)

| ID | Description | Auto |
|---|---|---|
| play-enter | Explore created world mode | no |
| play-interact | Object click reactions / animations | no |

### Save / Gallery (10pts)

| ID | Description | Auto |
|---|---|---|
| save-load | Project save / load | no |
| gallery-view | Gallery screen exists | no |

### UX Quality (15pts)

| ID | Description | Auto |
|---|---|---|
| ux-child | Child-friendly design (big buttons, minimal text) | no |
| ux-responsive | Desktop / tablet responsive | no |
| ux-no-clutter | Clean UI (no clutter) | no |
| ux-visual-guide | Visual guidance / icon-driven | no |

### Code Quality & Testing (10pts)

| ID | Description | Auto |
|---|---|---|
| test-exists | Test files exist (*.test.*, *.spec.*) | yes |
| test-pass | Tests pass (`npm test`) | yes |
| test-coverage | Coverage for key components | yes |
| test-meaningful | Meaningful tests (not just snapshots) | no |

## Auto Scoring

`auto-score.sh` checks:

| Check | Command |判定 |
|---|---|---|
| Next.js exists | `grep "next" package.json` | exists |
| TypeScript | `ls tsconfig.json` | exists |
| Tailwind | `grep "tailwindcss" package.json` | exists |
| R3F + Drei | `grep "@react-three" package.json` | exists |
| Build success | `npm install && npm run build` | exit code 0 |
| TSC errors | `npx tsc --noEmit 2>&1 \| grep "error" \| wc -l` | error count |
| Lint | `npx eslint . --format json` | error / warning count |
| OpenAI API | `grep -r "openai" src/` | exists |
| Test files | `find src -name "*.test.*" -o -name "*.spec.*" \| wc -l` | file count |
| Tests pass | `npm test -- --passWithNoTests` | exit code 0 |
| Coverage | `npm test -- --coverage` | % |
| File count / LOC | `tokei` or `cloc` | reference |

## Manual Scoring Template

```json
{
  "harness": "",
  "scorer": "",
  "date": "",
  "scores": {
    "3d-canvas":      { "score": 0, "max": 5, "note": "" },
    "3d-place":       { "score": 0, "max": 5, "note": "" },
    "ux-child":       { "score": 0, "max": 5, "note": "" }
  },
  "screenshots": [],
  "overall_impression": ""
}
```

## Run Protocol

The entire pipeline is automated by `benchmarks/run.sh` and `benchmarks/collect.sh`.
A single human review pass at the end is the only manual step.

### Phase 1: Environment Preparation (`run.sh`)

1. Verify `claude`, `jq`, `git`, `bun` in PATH
2. Verify `ANTHROPIC_API_KEY` is set
3. Create `BASE=/tmp/oma-benchmark-{timestamp}`
4. Create 5 isolated `homes/{harness}` and `projects/{harness}`
5. `git init` each project
6. Record `claude --version`
7. Copy `prompt.md` to `$BASE/prompt.md`

### Phase 2: Harness Installation (`run.sh`, sequential)

1. vanilla: skip
2. oma: `CI=true HOME=$HOMEDIR bunx oh-my-agent@latest install`
3. omc: `git clone --depth 1 https://github.com/Yeachan-Heo/oh-my-claudecode $BASE/plugins/omc` (no install — loaded via `--plugin-dir` at runtime)
4. ecc: clone + `bash install.sh --profile full`
5. superpowers: `git clone --depth 1 https://github.com/obra/superpowers $BASE/plugins/superpowers` (loaded via `--plugin-dir` at runtime)
6. Per-harness install status recorded in `{harness}.manifest.json`

### Phase 3: Benchmark Execution (`run.sh`, sequential)

1. Start timer
2. `claude -p` with all control flags (see Control Variables)
3. Capture stdout (JSON metadata) → `{harness}.json`
4. Capture stderr → `{harness}.stderr`
5. Stop timer, record duration + exit code in `{harness}.manifest.json`
6. Failure of one harness does NOT abort the rest

### Phase 4: Result Collection (`collect.sh`)

1. For each harness, invoke `auto-score.sh` → `{harness}.auto-score.json`
2. For each harness, invoke `visual-score.sh` → starts dev server, navigates Chrome via MCP, captures screenshots, AI-scores UX
3. Copy generated code to `benchmarks/runs/{harness}/` (excluding node_modules, .next, .git)
4. Copy screenshots to `benchmarks/screenshots/{harness}/`

### Phase 5: Scoring & Report (`collect.sh`)

1. Aggregate auto + visual scores per category using checklist.json weights
2. Compute total per harness, rank
3. Generate `results/scores.json` (machine-readable)
4. Generate `results/report.md` (human-readable, ready to publish)

### Phase 6: Human Review (manual, optional)

1. Inspect generated code and screenshots
2. Fill in `test-meaningful` manual score
3. Adjust report.md as needed

## Plugin Loading via `--plugin-dir`

`omc` and `superpowers` are Claude Code plugins. Instead of `claude plugin install`
(which has no `--yes`/`--non-interactive` flag and may hang), we use Claude Code's
`--plugin-dir <path>` flag to load plugins directly from a local directory for the
session only. This requires no install step and no `~/.claude/plugins/` mutation.

```bash
# Pre-clone (in run.sh setup)
git clone --depth 1 https://github.com/Yeachan-Heo/oh-my-claudecode $BASE/plugins/omc
git clone --depth 1 https://github.com/obra/superpowers $BASE/plugins/superpowers

# Per-session load (in claude -p invocation)
HOME=$BASE/homes/omc \
OMC_PLUGIN_ROOT=$BASE/plugins/omc \
  claude -p "$(cat prompt.md)" \
    --plugin-dir $BASE/plugins/omc \
    ...
```

For `omc`, `OMC_PLUGIN_ROOT` is also exported per the oh-my-claudecode REFERENCE.md
decision matrix for "local dev checkout, no OMC shim" mode. `omc setup` is NOT run
because in `--plugin-dir` mode the plugin provides skills/agents at runtime — `omc setup`
only installs the optional HUD/git-hooks/CLAUDE.md into `~/.claude/`, which we don't need
for a benchmark run.

## Intervention Policy

The benchmark is fully unattended via `claude -p --dangerously-skip-permissions`.
**No human interventions occur during execution.**

If a harness hangs or errors, the 60-minute `timeout` and `--max-budget-usd 20`
caps it. Whatever output exists at that point is what gets scored.

The only manual step is the optional Phase 6 review and `test-meaningful` scoring.

## Edge Case Handling

| Situation | Response |
|---|---|
| Harness install fails | Record `install_status: failed` in manifest, skip that harness's run, continue with the rest |
| Claude exceeds time limit | `timeout 3600` kills it, partial output gets scored |
| Claude exceeds budget | `--max-budget-usd 20` halts it, partial output gets scored |
| Build fails | Recorded as-is in `auto-score.json`, no human fix |
| npm install fails | Counted as build failure, score 0 for setup-build |
| Harness auto-detects workflow from CLAUDE.md | Allowed — auto-detection is a natural harness feature |
| Dev server cannot start | `visual-score.sh` records 0 across visual items + explanation |
| Dev server uses non-default port | `score-prompt.md` instructs Claude to detect the port from stdout |
| No test framework | `test-exists: 0`, `test-pass: 0`, `test-coverage: 0` |
| chrome-devtools-mcp not installed | First `npx -y chrome-devtools-mcp@latest` invocation auto-installs it |
| Plugin install hangs | `timeout 300` on install command, treated as install failure |

## Time Limits

| Phase | Limit | Mechanism |
|---|---|---|
| Harness installation | 5 minutes | `timeout 300` |
| Benchmark execution | 60 minutes | `timeout 3600` + `--max-budget-usd 20` |
| Build & test (auto-score) | 5 minutes per check | `timeout 300` |
| Visual scoring (Claude + Chrome MCP) | 5 minutes | `timeout 300` + `--max-budget-usd 5` |

## Budget Estimate

| Item | Cost |
|---|---|
| 5 harness runs × $20 max | $100 |
| 5 visual scoring sessions × $5 max | $25 |
| Dry run | $5 |
| **Total budget cap** | **~$130** |

Actual cost will likely be lower since most harnesses will not hit the cap.

## Meta Metrics (not scored, reference only)

| Metric | Description |
|---|---|
| Wall Clock Time | Total execution time |
| Total Tokens | Token usage during run |
| Human Interventions | Number of interventions |
| Retry Count | Error retry count |
| Files Generated | Total generated file count |
| Lines of Code | LOC via tokei/cloc |

## Report Format

Final report (`results/report.md`) includes:

1. Summary table (score, build, tests, time, tokens per harness)
2. Screenshot comparison grid (Landing, World Builder, AI Panel, Gallery)
3. Category breakdown tables
4. Meta metrics comparison
5. Methodology section for reproducibility
