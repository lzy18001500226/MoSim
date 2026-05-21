#!/usr/bin/env python3
"""
Loopback Manager - Manages the iteration loop for Codex CLI

This script handles the core loopback logic:
1. Reading and updating the state file
2. Checking completion conditions
3. Managing iteration counting
4. Providing status information

Usage:
    python loopback-manager.py check          # Check current state
    python loopback-manager.py advance        # Advance iteration after a run (optionally checks output file for promise)
    python loopback-manager.py next           # Increment iteration (manual)
    python loopback-manager.py complete       # Mark as complete and exit
    python loopback-manager.py status         # Show full status
    python loopback-manager.py info --json    # Print machine-readable state
    python loopback-manager.py set-session    # Store the Codex session id for resume mode
"""

import os
import sys
import re
import json
import argparse
import yaml
from datetime import datetime
from pathlib import Path

STATE_FILE = Path(".codex/loopback.local.md")

def parse_state_file():
    """Parse the state file and return frontmatter and content."""
    if not STATE_FILE.exists():
        return None, None

    content = STATE_FILE.read_text()

    # Split frontmatter from content
    match = re.match(r'^---\n(.*?)\n---\n\n(.*)$', content, re.DOTALL)
    if not match:
        return None, content

    try:
        frontmatter = yaml.safe_load(match.group(1))
        body = match.group(2)
        return frontmatter, body
    except yaml.YAMLError:
        return None, content

def save_state_file(frontmatter, body):
    """Save frontmatter and content to state file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    yaml_content = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
    content = f"---\n{yaml_content}---\n\n{body}"
    STATE_FILE.write_text(content)

def _utc_now_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def _detect_promise(text, promise):
    if not promise:
        return False
    # Match literal promise between <promise>...</promise>, allowing surrounding whitespace.
    pattern = r"<promise>\s*" + re.escape(str(promise)) + r"\s*</promise>"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None

def check_command():
    """Check if loop should continue or stop."""
    frontmatter, body = parse_state_file()

    if not frontmatter:
        print("No active loopback found.", file=sys.stderr)
        sys.exit(1)

    if not frontmatter.get('active', False):
        print("STOP: Loopback is not active.")
        print(f"PROMPT: {body.strip() if body else 'No prompt found'}")
        sys.exit(0)

    iteration = frontmatter.get('iteration', 1)
    max_iterations = frontmatter.get('max_iterations', 0)

    # IMPORTANT: iteration is the iteration that is ABOUT TO RUN.
    # So we only stop if iteration is strictly greater than max_iterations.
    if max_iterations > 0 and iteration > max_iterations:
        print(f"STOP: Maximum iterations ({max_iterations}) reached.")
        print(f"PROMPT: {body.strip() if body else 'No prompt found'}")
        sys.exit(0)

    # If we get here, continue the loop
    print(f"CONTINUE: Iteration {iteration}")
    print(f"PROMPT: {body.strip() if body else 'No prompt found'}")
    sys.exit(0)

def advance_command(output_file=None):
    """
    Advance the loop after a completed iteration:
    - Detect completion promise in the output (if configured)
    - Enforce max_iterations after running the current iteration
    - Increment iteration only if continuing

    Semantics:
      frontmatter.iteration = current iteration number being run (1-indexed)
      After an iteration finishes, we either stop (active=false, keep iteration as final),
      or set iteration += 1 for the next run.
    """
    frontmatter, body = parse_state_file()

    if not frontmatter:
        print("No active loopback found.", file=sys.stderr)
        sys.exit(1)

    if not frontmatter.get("active", False):
        result = {"stop": True, "reason": "inactive", "iteration": frontmatter.get("iteration", 1)}
        print(json.dumps(result, ensure_ascii=False))
        return

    iteration = int(frontmatter.get("iteration", 1) or 1)
    max_iterations = int(frontmatter.get("max_iterations", 0) or 0)
    completion_promise = frontmatter.get("completion_promise")

    output_text = ""
    if output_file:
        try:
            output_text = Path(output_file).read_text(errors="replace")
            frontmatter["last_output_file"] = str(output_file)
        except FileNotFoundError:
            output_text = ""

    promise_found = False
    if completion_promise and completion_promise != "null":
        promise_found = _detect_promise(output_text, completion_promise)

    should_stop = False
    stop_reason = None

    if promise_found:
        should_stop = True
        stop_reason = f"completion_promise_detected:{completion_promise}"
        frontmatter["completion_detected"] = True
        frontmatter["completion_detected_at_iteration"] = iteration
    elif max_iterations > 0 and iteration >= max_iterations:
        should_stop = True
        stop_reason = f"max_iterations_reached:{max_iterations}"

    frontmatter["last_updated"] = _utc_now_iso()

    if should_stop:
        frontmatter["active"] = False
        frontmatter["completed_at"] = _utc_now_iso()
        frontmatter["final_iteration"] = iteration
        frontmatter["stop_reason"] = stop_reason
        save_state_file(frontmatter, body)
        result = {"stop": True, "reason": stop_reason, "iteration": iteration, "max_iterations": max_iterations}
        print(json.dumps(result, ensure_ascii=False))
        return

    # Continue: increment iteration
    frontmatter["iteration"] = iteration + 1
    save_state_file(frontmatter, body)
    result = {"stop": False, "iteration": frontmatter["iteration"], "max_iterations": max_iterations}
    print(json.dumps(result, ensure_ascii=False))

def next_command():
    """Increment iteration and return the prompt for next iteration."""
    frontmatter, body = parse_state_file()

    if not frontmatter:
        print("No active loopback found.", file=sys.stderr)
        sys.exit(1)

    # Increment iteration
    frontmatter['iteration'] = frontmatter.get('iteration', 1) + 1

    # Update timestamp
    frontmatter['last_updated'] = datetime.utcnow().isoformat() + 'Z'

    save_state_file(frontmatter, body)

    iteration = frontmatter['iteration']
    print(f"🔄 Loopback iteration {iteration}")
    print(f"Max iterations: {frontmatter.get('max_iterations', 0) or 'unlimited'}")
    print(f"Completion promise: {frontmatter.get('completion_promise') or 'none'}")
    print("")
    print("Prompt:")
    print(body.strip() if body else 'No prompt found')

def complete_command():
    """Mark the loopback as complete."""
    frontmatter, body = parse_state_file()

    if not frontmatter:
        print("No active loopback found.", file=sys.stderr)
        sys.exit(1)

    frontmatter['active'] = False
    frontmatter['completed_at'] = _utc_now_iso()
    frontmatter['final_iteration'] = frontmatter.get('iteration', 1)

    save_state_file(frontmatter, body)

    print("✅ Loopback completed!")
    print(f"Total iterations: {frontmatter['final_iteration']}")
    print(f"Completed at: {frontmatter['completed_at']}")

def status_command():
    """Show full status of the loopback."""
    frontmatter, body = parse_state_file()

    if not frontmatter:
        print("No active loopback found.")
        sys.exit(1)

    print("📊 Loopback Status")
    print("═══════════════════════════════════════════════════════════")
    print(f"Active: {frontmatter.get('active', False)}")
    print(f"Current Iteration: {frontmatter.get('iteration', 1)}")
    print(f"Max Iterations: {frontmatter.get('max_iterations', 0) or 'unlimited'}")
    print(f"Completion Promise: {frontmatter.get('completion_promise') or 'none'}")
    print(f"Reuse Session: {frontmatter.get('reuse_session', True)}")
    print(f"Session ID: {frontmatter.get('session_id') or 'none'}")
    print(f"Started At: {frontmatter.get('started_at', 'unknown')}")
    if 'last_updated' in frontmatter:
        print(f"Last Updated: {frontmatter['last_updated']}")
    if 'completed_at' in frontmatter:
        print(f"Completed At: {frontmatter['completed_at']}")
    if 'final_iteration' in frontmatter:
        print(f"Final Iteration: {frontmatter['final_iteration']}")
    if 'stop_reason' in frontmatter:
        print(f"Stop Reason: {frontmatter['stop_reason']}")
    print("═══════════════════════════════════════════════════════════")
    print("")
    print("📝 Current Prompt:")
    print(body.strip() if body else 'No prompt found')

def info_command(as_json=False):
    frontmatter, body = parse_state_file()
    if not frontmatter:
        payload = {"active": False, "stop": True, "reason": "no_state_file"}
        print(json.dumps(payload, ensure_ascii=False) if as_json else "No active loopback found.")
        return

    active = bool(frontmatter.get("active", False))
    iteration = int(frontmatter.get("iteration", 1) or 1)
    max_iterations = int(frontmatter.get("max_iterations", 0) or 0)
    completion_promise = frontmatter.get("completion_promise")
    session_id = frontmatter.get("session_id")
    reuse_session = frontmatter.get("reuse_session")

    stop = False
    reason = None
    if not active:
        stop = True
        reason = frontmatter.get("stop_reason") or "inactive"
    elif max_iterations > 0 and iteration > max_iterations:
        stop = True
        reason = f"max_iterations_reached:{max_iterations}"

    payload = {
        "active": active,
        "iteration": iteration,
        "max_iterations": max_iterations,
        "completion_promise": completion_promise,
        "session_id": session_id,
        "reuse_session": reuse_session,
        "prompt": (body.strip() if body else ""),
        "stop": stop,
        "reason": reason,
    }

    if as_json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(payload)

def main():
    parser = argparse.ArgumentParser(prog="loopback-manager.py", add_help=True)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check")
    sub.add_parser("next")
    sub.add_parser("complete")
    sub.add_parser("status")

    info_p = sub.add_parser("info")
    info_p.add_argument("--json", action="store_true")

    adv_p = sub.add_parser("advance")
    adv_p.add_argument("--output-file", default=None)

    set_sess = sub.add_parser("set-session")
    set_sess.add_argument("--session-id", required=True)
    set_sess.add_argument("--reuse-session", choices=["true", "false"], default=None)

    args = parser.parse_args()

    if args.command == "check":
        check_command()
    elif args.command == "next":
        next_command()
    elif args.command == "advance":
        advance_command(output_file=args.output_file)
    elif args.command == "complete":
        complete_command()
    elif args.command == "status":
        status_command()
    elif args.command == "info":
        info_command(as_json=bool(args.json))
    elif args.command == "set-session":
        frontmatter, body = parse_state_file()
        if not frontmatter:
            print("No active loopback found.", file=sys.stderr)
            sys.exit(1)
        frontmatter["session_id"] = args.session_id
        if args.reuse_session is not None:
            frontmatter["reuse_session"] = (args.reuse_session == "true")
        frontmatter["last_updated"] = _utc_now_iso()
        save_state_file(frontmatter, body)
        print("OK")
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
