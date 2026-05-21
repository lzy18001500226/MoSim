#!/bin/bash

# Loopback Setup Script
# Creates state file for in-session Loopback iteration loop

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse arguments
PROMPT_PARTS=()
MAX_ITERATIONS=0
COMPLETION_PROMISE="null"
DRY_RUN=false
RUN_DRIVER=true
REUSE_SESSION=true
ALLOW_INFINITE=false
WIZARD_MODE=true
FORCE_NON_INTERACTIVE=false
AUTO_YES=false

REUSE_SESSION_EXPLICIT=false
FRESH_SESSION_EXPLICIT=false

is_tty() {
  [[ -t 0 && -t 1 ]]
}

die() {
  echo "❌ Error: $*" >&2
  exit 1
}

print_wizard_overview() {
  cat <<'OVERVIEW_EOF'
🧭 Loopback 向导（共 6 步）
====================
Step 1 — 确认工作目录（Why：减少噪声，提升收敛）
Step 2 — 确认/编辑 PROMPT（Why：同一句 prompt 会反复执行）
Step 3 — 设定停止契约（Why：避免无限循环；promise 与 max-iterations 二选一即可）
Step 4 — 设定会话策略（Why：reuse 更像 Ralph Loop）
Step 5 — 选择运行方式（Why：dry-run 预演 / no-run 仅写状态）
Step 6 — 汇总确认（Why：可见即所得，避免参数误配）
OVERVIEW_EOF
}

validate_contract_non_interactive() {
  # Mutual exclusivity: user can't specify both explicitly.
  if [[ "${REUSE_SESSION_EXPLICIT}" == "true" && "${FRESH_SESSION_EXPLICIT}" == "true" ]]; then
    die "Flags --reuse-session and --fresh-session are mutually exclusive."
  fi

  # Stop contract (best practice): require one stop condition unless explicitly allowed.
  local has_promise="false"
  local has_max="false"

  if [[ -n "${COMPLETION_PROMISE}" && "${COMPLETION_PROMISE}" != "null" ]]; then
    has_promise="true"
  fi
  if [[ "${MAX_ITERATIONS}" -gt 0 ]]; then
    has_max="true"
  fi

  if [[ "${ALLOW_INFINITE}" != "true" && "${has_promise}" != "true" && "${has_max}" != "true" ]]; then
    echo "❌ Error: stop contract is required (non-interactive mode)." >&2
    echo "" >&2
    echo "Provide ONE of:" >&2
    echo "  - --completion-promise 'DONE'    (then only output: <promise>DONE</promise> when true)" >&2
    echo "  - --max-iterations 10            (hard stop to prevent runaway)" >&2
    echo "" >&2
    echo "If you truly want an infinite loop, pass: --allow-infinite" >&2
    echo "" >&2
    echo "Tip: run '/loopback --guide' to see the full parameter guide." >&2
    exit 1
  fi
}

wizard_interactive() {
  print_wizard_overview
  echo ""
  echo "（交互式向导）按 Enter 接受默认值；输入 'q' 退出。"
  echo ""

  if [[ "${AUTO_YES}" == "true" ]]; then
    # Fast path: apply safe defaults without prompting (still prints overview and summary).
    if [[ -z "${PROMPT}" ]]; then
      die "--yes requires a PROMPT (non-empty)."
    fi

    if [[ "${COMPLETION_PROMISE}" == "null" && "${MAX_ITERATIONS}" -le 0 && "${ALLOW_INFINITE}" != "true" ]]; then
      COMPLETION_PROMISE="DONE"
      MAX_ITERATIONS=10
    fi
    REUSE_SESSION=true
    DRY_RUN=false
    # Respect explicit --no-run / --dry-run if user provided them.
    if [[ "${DRY_RUN}" == "true" ]]; then
      RUN_DRIVER=false
    fi
    return 0
  fi

  # Step 1: working directory confirmation (optional)
  echo "Step 1/6 — 工作目录"
  echo "Current: $(pwd)"
  echo "建议：在目标仓库根目录运行（更收敛）。"
  local ans
  read -r -p "继续？[Y/n] " ans || exit 130
  if [[ "${ans}" == "q" ]]; then exit 1; fi
  if [[ -n "${ans}" && "${ans}" != "Y" && "${ans}" != "y" ]]; then
    die "Aborted by user."
  fi
  echo ""

  # Step 2: prompt (required)
  echo "Step 2/6 — PROMPT（必选）"
  if [[ -n "${PROMPT}" ]]; then
    echo "当前 PROMPT: ${PROMPT}"
    read -r -p "修改 PROMPT？[y/N] " ans || exit 130
    if [[ "${ans}" == "q" ]]; then exit 1; fi
    if [[ "${ans}" == "y" || "${ans}" == "Y" ]]; then
      PROMPT=""
    fi
  fi
  while [[ -z "${PROMPT}" ]]; do
    read -r -p "请输入 PROMPT: " PROMPT || exit 130
    if [[ "${PROMPT}" == "q" ]]; then exit 1; fi
  done
  echo ""

  # Step 3: stop contract (required unless allow infinite)
  while true; do
    echo "Step 3/6 — 停止契约（必选：promise / max-iterations 二选一；推荐都设）"
    echo "当前 completion promise: $(if [[ "${COMPLETION_PROMISE}" != "null" ]]; then echo "${COMPLETION_PROMISE}"; else echo "none"; fi)"
    echo "当前 max iterations: $(if [[ "${MAX_ITERATIONS}" -gt 0 ]]; then echo "${MAX_ITERATIONS}"; else echo "unlimited"; fi)"
    echo ""
    echo "选择停止方式："
    echo "  1) completion promise（推荐）"
    echo "  2) max iterations（推荐）"
    echo "  3) 两者都设置（最推荐）"
    echo "  4) 允许无限循环（不推荐，需要明确确认）"
    read -r -p "选择 [1-4]（默认 3）: " ans || exit 130
    if [[ "${ans}" == "q" ]]; then exit 1; fi
    if [[ -z "${ans}" ]]; then ans="3"; fi

    case "${ans}" in
      1)
        MAX_ITERATIONS=0
        ;;
      2)
        COMPLETION_PROMISE="null"
        ;;
      3)
        ;;
      4)
        ALLOW_INFINITE=true
        MAX_ITERATIONS=0
        COMPLETION_PROMISE="null"
        read -r -p "确认允许无限循环？输入 'I UNDERSTAND' 确认: " ans || exit 130
        if [[ "${ans}" != "I UNDERSTAND" ]]; then
          echo "未确认无限循环，返回停止契约设置。" >&2
          ALLOW_INFINITE=false
          continue
        fi
        ;;
      *)
        echo "无效选择，请重试。" >&2
        continue
        ;;
    esac

    if [[ "${ALLOW_INFINITE}" != "true" ]]; then
      if [[ "${COMPLETION_PROMISE}" == "null" ]]; then
        read -r -p "设置 completion promise（例如 DONE，留空跳过）: " ans || exit 130
        if [[ "${ans}" == "q" ]]; then exit 1; fi
        if [[ -n "${ans}" ]]; then
          COMPLETION_PROMISE="${ans}"
        fi
      fi
      if [[ "${MAX_ITERATIONS}" -le 0 ]]; then
        read -r -p "设置 max iterations（例如 10，留空跳过）: " ans || exit 130
        if [[ "${ans}" == "q" ]]; then exit 1; fi
        if [[ -n "${ans}" ]]; then
          if ! [[ "${ans}" =~ ^[0-9]+$ ]]; then
            echo "max iterations 必须是整数，请重试。" >&2
            continue
          fi
          if [[ "${ans}" -le 0 ]]; then
            echo "max iterations 必须 >= 1（或选择允许无限循环）。" >&2
            continue
          fi
          MAX_ITERATIONS="${ans}"
        fi
      fi

      if [[ "${COMPLETION_PROMISE}" == "null" && "${MAX_ITERATIONS}" -le 0 ]]; then
        read -r -p "你没有设置任何停止条件。要重新设置吗？[Y/n] " ans || exit 130
        if [[ "${ans}" == "q" ]]; then exit 1; fi
        if [[ -n "${ans}" && "${ans}" != "Y" && "${ans}" != "y" ]]; then
          die "Stop contract missing."
        fi
        continue
      fi
    fi

    break
  done
  echo ""

  # Step 4: session strategy (optional, default reuse)
  echo "Step 4/6 — 会话策略"
  echo "  1) --reuse-session（默认，推荐）"
  echo "  2) --fresh-session"
  read -r -p "选择 [1-2]（默认 1）: " ans || exit 130
  if [[ "${ans}" == "q" ]]; then exit 1; fi
  if [[ "${ans}" == "2" ]]; then
    REUSE_SESSION=false
  else
    REUSE_SESSION=true
  fi
  echo ""

  # Step 5: run mode (optional)
  echo "Step 5/6 — 运行方式"
  read -r -p "先 dry-run 预演（不写状态、不启动）？[y/N] " ans || exit 130
  if [[ "${ans}" == "q" ]]; then exit 1; fi
  if [[ "${ans}" == "y" || "${ans}" == "Y" ]]; then
    DRY_RUN=true
    RUN_DRIVER=false
  else
    read -r -p "仅创建状态（--no-run，不启动 driver）？[y/N] " ans || exit 130
    if [[ "${ans}" == "q" ]]; then exit 1; fi
    if [[ "${ans}" == "y" || "${ans}" == "Y" ]]; then
      RUN_DRIVER=false
    fi
  fi
  echo ""

  # Step 6: summary + confirm
  echo "Step 6/6 — 汇总确认"
  echo "PROMPT: ${PROMPT}"
  echo "completion promise: $(if [[ "${COMPLETION_PROMISE}" != "null" ]]; then echo "${COMPLETION_PROMISE}"; else echo "none"; fi)"
  echo "max iterations: $(if [[ "${MAX_ITERATIONS}" -gt 0 ]]; then echo "${MAX_ITERATIONS}"; else echo "unlimited"; fi)"
  echo "reuse session: $(if [[ "${REUSE_SESSION}" == true ]]; then echo "yes"; else echo "no"; fi)"
  echo "dry-run: $(if [[ "${DRY_RUN}" == true ]]; then echo "yes"; else echo "no"; fi)"
  echo "start driver: $(if [[ "${RUN_DRIVER}" == true ]]; then echo "yes"; else echo "no"; fi)"
  echo ""
  read -r -p "确认继续？[Y/n] " ans || exit 130
  if [[ "${ans}" == "q" ]]; then exit 1; fi
  if [[ -n "${ans}" && "${ans}" != "Y" && "${ans}" != "y" ]]; then
    die "Aborted by user."
  fi
}

# Parse options and positional arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --guide)
      cat << 'GUIDE_EOF'
Loopback 参数向导（共 6 步）
=====================

这不是交互式表单；它只是一个“轻量向导”，帮助你更容易把关键契约（stop conditions / promise）用参数表达清楚。

Step 1 — 选择工作目录（Why）
  Why: Loopback 每轮都依赖“文件系统 + git 历史 + 上轮输出”来自引用迭代。
  建议：进入目标仓库根目录再运行（比在 ~/Documents/GitHub 这种“仓库集合目录”更稳定、更省 token）。

Step 2 — 写清 PROMPT（Why）
  Why: Loopback 会把“同一句 PROMPT”反复喂给 Codex；PROMPT 越清晰，每轮越收敛。
  建议：在 PROMPT 里写验收条件（例如“所有测试通过/某命令输出为 X/某文件包含 Y”）。

Step 3 — 设置停止契约（Why）
  Why: 如果没有停止条件，Loopback 可能会无限运行。
  推荐二选一（或同时设置）：
    A) completion promise（强烈推荐）
       --completion-promise 'DONE'
       结束信号必须在输出中出现：<promise>DONE</promise>
    B) 最大迭代次数（防止跑飞）
       --max-iterations 10

Step 4 — 选择会话策略（Why）
  Why: 会话复用影响“像同一对话继续”还是“每轮重开”。
    --reuse-session  (默认) 更像 Ralph Loop：同一 thread 续跑，收敛更好
    --fresh-session           每轮新会话：更隔离，但自引用更弱

Step 5 — 先预演，再启动（Why）
  Why: 预演可以提前发现参数/契约没写清，避免跑起来才发现要重来。
    预演（不创建 state、不启动 driver）：
      /loopback <PROMPT> --dry-run [其他参数...]
    正式启动：
      /loopback <PROMPT> [其他参数...]

Step 6 — 不想用向导/想无限循环（Why）
  Why: 有些场景你可能在自动化脚本里跑，或者确实需要无限循环。
    跳过向导：
      /loopback <PROMPT> --no-wizard [其他参数...]
    允许无限循环（不推荐，必须显式声明）：
      /loopback <PROMPT> --allow-infinite [其他参数...]

常用模板
--------
  /loopback "修复 X。通过 `pytest -q`。完成后输出 <promise>DONE</promise>。" \
    --completion-promise 'DONE' \
    --max-iterations 10 \
    --reuse-session

提示
----
  - completion promise 是“契约”，只能在完全真实时输出，不能为了停循环而虚假承诺。
  - 如果你不确定怎么传参，先运行：/loopback --help
GUIDE_EOF
      exit 0
      ;;
    --wizard)
      # The wizard is enabled by default; this flag is a no-op for explicitness.
      WIZARD_MODE=true
      shift
      ;;
    --no-wizard)
      WIZARD_MODE=false
      shift
      ;;
    --non-interactive)
      FORCE_NON_INTERACTIVE=true
      shift
      ;;
    --yes)
      AUTO_YES=true
      shift
      ;;
    --allow-infinite)
      ALLOW_INFINITE=true
      shift
      ;;
    -h|--help)
      cat << 'HELP_EOF'
Loopback - Iterative development loop for Codex CLI

USAGE:
  /loopback [PROMPT...] [OPTIONS]

ARGUMENTS:
  PROMPT...    Initial prompt to start the loop (can be multiple words without quotes)

OPTIONS:
  --max-iterations <n>           Maximum iterations before auto-stop (default: unlimited)
  --completion-promise '<text>'  Promise phrase (USE QUOTES for multi-word)
  --guide                        Show a lightweight parameter guide (does not start Loopback)
  --wizard                       Start the wizard flow (default)
  --no-wizard                    Disable the default wizard and use raw arguments
  --non-interactive              Do not prompt; validate and fail fast if contract is missing
  --allow-infinite               Allow missing stop contract (dangerous; may run forever)
  --yes                          Auto-accept wizard defaults (interactive only)
  --dry-run                      Only show plan, don't execute
  --no-run                       Only create state file, don't launch the driver
  --fresh-session                Do not reuse Codex session across iterations
  --reuse-session                Reuse the SAME Codex session across iterations (default)
  -h, --help                     Show this help message

DESCRIPTION:
  Starts a Loopback iteration in your CURRENT session. Each iteration
  feeds the same prompt back to Codex, allowing you to see previous work
  and iteratively improve until completion or iteration limit.

  To signal completion, you must output: <promise>YOUR_PHRASE</promise>

  Note: If you're not in a git repository, the Loopback driver will automatically
  add `--skip-git-repo-check` when invoking `codex exec`.

  Use this for:
  - Interactive iteration where you want to see progress
  - Tasks requiring self-correction and refinement
  - Learning how Loopback works

EXAMPLES:
  /loopback Build a todo API --completion-promise 'DONE' --max-iterations 20
  /loopback --max-iterations 10 Fix the auth bug
  /loopback Refactor cache layer  (runs forever)
  /loopback --completion-promise 'TASK COMPLETE' Create a REST API
  /loopback --guide
  /loopback --wizard "Fix the auth bug" --completion-promise 'DONE' --max-iterations 10
  /loopback --allow-infinite "Explore ideas"   (not recommended)

STOPPING:
  Only by reaching --max-iterations or detecting --completion-promise
  Or cancel by deleting the state file (use /cancel-loop)
  Best practice: provide at least one stop condition (promise or max-iterations).
  If you truly want an infinite loop, pass --allow-infinite (not recommended).

MONITORING:
  # View current iteration:
  grep '^iteration:' .codex/loopback.local.md

  # View full state:
  head -10 .codex/loopback.local.md
HELP_EOF
      exit 0
      ;;
    --max-iterations)
      if [[ -z "${2:-}" ]]; then
        echo "❌ Error: --max-iterations requires a number argument" >&2
        echo "" >&2
        echo "   Valid examples:" >&2
        echo "     --max-iterations 10" >&2
        echo "     --max-iterations 50" >&2
        echo "     --max-iterations 0  (unlimited)" >&2
        echo "" >&2
        echo "   You provided: --max-iterations (with no number)" >&2
        exit 1
      fi
      if ! [[ "$2" =~ ^[0-9]+$ ]]; then
        echo "❌ Error: --max-iterations must be a positive integer or 0, got: $2" >&2
        echo "" >&2
        echo "   Valid examples:" >&2
        echo "     --max-iterations 10" >&2
        echo "     --max-iterations 50" >&2
        echo "     --max-iterations 0  (unlimited)" >&2
        echo "" >&2
        echo "   Invalid: decimals (10.5), negative numbers (-5), text" >&2
        exit 1
      fi
      MAX_ITERATIONS="$2"
      shift 2
      ;;
    --completion-promise)
      if [[ -z "${2:-}" ]]; then
        echo "❌ Error: --completion-promise requires a text argument" >&2
        echo "" >&2
        echo "   Valid examples:" >&2
        echo "     --completion-promise 'DONE'" >&2
        echo "     --completion-promise 'TASK COMPLETE'" >&2
        echo "     --completion-promise 'All tests passing'" >&2
        echo "" >&2
        echo "   You provided: --completion-promise (with no text)" >&2
        echo "" >&2
        echo "   Note: Multi-word promises must be quoted!" >&2
        exit 1
      fi
      COMPLETION_PROMISE="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --no-run)
      RUN_DRIVER=false
      shift
      ;;
    --fresh-session)
      FRESH_SESSION_EXPLICIT=true
      REUSE_SESSION=false
      shift
      ;;
    --reuse-session)
      REUSE_SESSION_EXPLICIT=true
      REUSE_SESSION=true
      shift
      ;;
    *)
      # Non-option argument - collect all as prompt parts
      PROMPT_PARTS+=("$1")
      shift
      ;;
  esac
done

# Join all prompt parts with spaces
PROMPT="${PROMPT_PARTS[*]}"

# Default wizard behavior:
# - Always show a guided, contract-first flow when a TTY is available
# - In non-interactive contexts, validate required contracts and fail fast (best practice)
if [[ "${WIZARD_MODE}" == "true" ]]; then
  if is_tty && [[ "${FORCE_NON_INTERACTIVE}" != "true" ]]; then
    wizard_interactive
  else
    # Non-interactive: still guide, but do not prompt.
    print_wizard_overview >&2
    echo "" >&2
    echo "（非交互模式）使用已提供参数；缺少关键契约将直接失败。" >&2
    echo "" >&2
    validate_contract_non_interactive
  fi
fi

# Validate prompt is non-empty (wizard_interactive may have populated it)
if [[ -z "$PROMPT" ]]; then
  echo "❌ Error: No prompt provided" >&2
  echo "" >&2
  echo "   Loopback needs a task description to work on." >&2
  echo "" >&2
  echo "   Examples:" >&2
  echo "     /loopback Build a REST API for todos" >&2
  echo "     /loopback Fix the auth bug --max-iterations 20" >&2
  echo "     /loopback --completion-promise 'DONE' Refactor code" >&2
  echo "" >&2
  echo "   For all options: /loopback --help" >&2
  exit 1
fi

# Guard against common confusion: trying to cancel by passing "/cancel-loop" as the prompt.
case "${PROMPT}" in
  "/cancel-loop"|"cancel-loop"|"cancel_loop"|"/cancel_loop")
    echo "❌ Error: '${PROMPT}' 是取消命令，不是 loopback 的任务提示词。" >&2
    echo "" >&2
    echo "   正确用法：" >&2
    echo "     /cancel-loop" >&2
    echo "" >&2
    echo "   或者直接删除状态文件：" >&2
    echo "     rm .codex/loopback.local.md" >&2
    exit 1
    ;;
esac

# Show dry-run plan if requested
if [[ "$DRY_RUN" == true ]]; then
  echo "📝 Loopback Plan (Dry Run)"
  echo "═══════════════════════════════════════════════════════════"
  echo ""
  echo "Prompt: $PROMPT"
  echo ""
  echo "Max Iterations: $(if [[ $MAX_ITERATIONS -gt 0 ]]; then echo $MAX_ITERATIONS; else echo "unlimited"; fi)"
  echo "Completion Promise: $(if [[ "$COMPLETION_PROMISE" != "null" ]]; then echo "$COMPLETION_PROMISE"; else echo "none"; fi)"
  echo "Reuse Codex Session: $(if [[ "$REUSE_SESSION" == true ]]; then echo "yes"; else echo "no"; fi)"
  echo ""
  echo "State file: .codex/loopback.local.md"
  echo ""
  echo "To actually start the loop, run without --dry-run"
  echo "═══════════════════════════════════════════════════════════"
  exit 0
fi

# Create state file for iteration tracking (markdown with YAML frontmatter)
mkdir -p .codex

# Quote completion promise for YAML if it contains special chars or is not null
if [[ -n "$COMPLETION_PROMISE" ]] && [[ "$COMPLETION_PROMISE" != "null" ]]; then
  # Escape backslashes and double quotes for YAML double-quoted string
  esc="${COMPLETION_PROMISE//\\/\\\\}"
  esc="${esc//\"/\\\"}"
  COMPLETION_PROMISE_YAML="\"$esc\""
else
  COMPLETION_PROMISE_YAML="null"
fi

cat > .codex/loopback.local.md <<EOF
---
active: true
iteration: 1
max_iterations: $MAX_ITERATIONS
completion_promise: $COMPLETION_PROMISE_YAML
reuse_session: $(if [[ "$REUSE_SESSION" == true ]]; then echo "true"; else echo "false"; fi)
session_id: null
started_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
---

$PROMPT
EOF

# Output setup message
cat <<EOF
🔄 Loopback iteration loop activated in this session!

Iteration: 1
Max iterations: $(if [[ $MAX_ITERATIONS -gt 0 ]]; then echo $MAX_ITERATIONS; else echo "unlimited"; fi)
Completion promise: $(if [[ "$COMPLETION_PROMISE" != "null" ]]; then echo "${COMPLETION_PROMISE//\"/} (ONLY output when TRUE - do not lie!)"; else echo "none (runs forever)"; fi)
Reuse session: $(if [[ "$REUSE_SESSION" == true ]]; then echo "yes"; else echo "no"; fi)

The Loopback state file is now active. A Loopback driver can re-run the SAME PROMPT
across iterations, allowing you to see previous work in files and iteratively improve.

To monitor: head -10 .codex/loopback.local.md

To cancel: /cancel-loop (removes the state file)

🔄
EOF

# Output the initial prompt if provided
if [[ -n "$PROMPT" ]]; then
  echo ""
  echo "$PROMPT"
fi

if [[ "$RUN_DRIVER" == true ]]; then
  echo ""
  echo "▶️  Starting Loopback driver: ${SCRIPT_DIR}/codex-loopback-wrapper.sh"
  echo ""
  "${SCRIPT_DIR}/codex-loopback-wrapper.sh"
fi

# Display completion promise requirements if set
if [[ "$COMPLETION_PROMISE" != "null" ]]; then
  echo ""
  echo "═══════════════════════════════════════════════════════════"
  echo "CRITICAL - Loopback Completion Promise"
  echo "═══════════════════════════════════════════════════════════"
  echo ""
  echo "To complete this loop, output this EXACT text:"
  echo "  <promise>$COMPLETION_PROMISE</promise>"
  echo ""
  echo "STRICT REQUIREMENTS (DO NOT VIOLATE):"
  echo "  ✓ Use <promise> XML tags EXACTLY as shown above"
  echo "  ✓ The statement MUST be completely and unequivocally TRUE"
  echo "  ✓ Do NOT output false statements to exit the loop"
  echo "  ✓ Do NOT lie even if you think you should exit"
  echo ""
  echo "IMPORTANT - Do not circumvent the loop:"
  echo "  Even if you believe you're stuck, the task is impossible,"
  echo "  or you've been running too long - you MUST NOT output a"
  echo "  false promise statement. The loop is designed to continue"
  echo "  until the promise is GENUINELY TRUE. Trust the process."
  echo ""
  echo "  If the loop should stop, the promise statement will become"
  echo "  true naturally. Do not force it by lying."
  echo "═══════════════════════════════════════════════════════════"
fi
