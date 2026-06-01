#!/usr/bin/python3
"""Grok search with fallback + internal context review (no internal search tools).

- Primary: grok-4.20-beta
- Fallback: grok-4.1-thinking
- Prompt only says "search and cite sources"
- Optional context recall via tools.grok_search.context
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

SYSTEM_PROMPT = """你必须主动搜索网络并返回证据。
要求：
1) 至少给出 2 条来源（含 URL、发布时间、原文摘录）
2) 不得编造来源；找不到就写“未找到”
3) 先列证据，再写结论
输出 JSON：
{
  "sources":[{"title":"","url":"","published_at":"","quote":""}],
  "claims":[{"statement":"","source_index":[0]}],
  "answer":"……",
  "unknowns":["..."],
  "confidence":0-1
}
"""


# -------- env + keychain helpers --------

def load_env(path: str) -> bool:
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
        return True
    except FileNotFoundError:
        return False


def iter_default_env_files() -> Iterable[str]:
    paths: List[str] = []

    ws = os.getenv("OPENCLAW_WORKSPACE")
    if ws:
        paths.append(os.path.join(ws, ".env"))

    # Sandbox workspace path
    paths.append("/workspace/.env")

    # User workspace (macOS/Linux)
    paths.append(os.path.expanduser("~/.openclaw/workspace/.env"))

    seen = set()
    for p in paths:
        p = os.path.expanduser(p)
        if p in seen:
            continue
        seen.add(p)
        yield p


def keychain_get(service: str, account: str) -> Optional[str]:
    if sys.platform != "darwin":
        return None
    if not os.path.exists("/usr/bin/security"):
        return None
    try:
        out = subprocess.check_output(
            ["/usr/bin/security", "find-generic-password", "-s", service, "-a", account, "-w"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode("utf-8").strip()
    except Exception:
        return None


def get_config(env_names: List[str], account: str, default: Optional[str] = None) -> Optional[str]:
    for name in env_names:
        val = os.getenv(name)
        if val:
            return val
    kc = keychain_get("openclaw-grok", account)
    return kc if kc else default


def parse_env_file_arg(argv: Optional[List[str]] = None) -> Optional[str]:
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--env-file", help="Path to .env file")
    ns, _ = p.parse_known_args(argv)
    return ns.env_file


def load_env_auto(env_file: Optional[str]) -> None:
    if env_file:
        env_path = os.path.expanduser(env_file)
        if not os.path.exists(env_path):
            raise FileNotFoundError(f"env file not found: {env_path}")
        load_env(env_path)
        return

    for p in iter_default_env_files():
        load_env(p)


# -------- grok call helpers --------

def request_chat_completion(
    base_url: str,
    api_key: str,
    model: str,
    messages: List[Dict[str, Any]],
    timeout: int,
    temperature: float = 0.2,
) -> Dict[str, Any]:
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "temperature": temperature,
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(f"{base_url}/v1/chat/completions", data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
        return json.loads(body)


def extract_content(resp_json: Dict[str, Any]) -> str:
    if "choices" in resp_json and resp_json["choices"]:
        msg = resp_json["choices"][0].get("message", {})
        return msg.get("content", "")
    # Fallback: OpenAI Responses-style
    if "output" in resp_json:
        for item in resp_json.get("output", []):
            if item.get("type") == "message":
                for c in item.get("content", []):
                    if c.get("type") == "output_text":
                        return c.get("text", "")
    return ""


def strip_code_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        # drop first and last fence
        if len(lines) >= 2 and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t


def extract_json(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    cleaned = strip_code_fences(text)
    # try direct JSON
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    # try substring between first { and last }
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = cleaned[start : end + 1]
        try:
            return json.loads(snippet)
        except Exception:
            return None
    return None


def is_valid_result(result: Dict[str, Any]) -> bool:
    if not isinstance(result, dict):
        return False
    sources = result.get("sources")
    if not isinstance(sources, list) or len(sources) < 2:
        return False
    for s in sources:
        if not isinstance(s, dict):
            return False
        if not s.get("url") or not s.get("published_at") or not s.get("quote"):
            return False
    if not result.get("answer"):
        return False
    return True


def call_with_validation(
    base_url: str,
    api_key: str,
    model: str,
    messages: List[Dict[str, Any]],
    timeout: int,
) -> Tuple[Optional[Dict[str, Any]], str, str]:
    """Returns (result_json, raw_text, error_reason)."""
    try:
        resp_json = request_chat_completion(base_url, api_key, model, messages, timeout)
    except urllib.error.HTTPError as e:
        return None, "", f"http_error:{e.code}"
    except Exception as e:
        return None, "", f"error:{type(e).__name__}"

    raw_text = extract_content(resp_json)
    result_json = extract_json(raw_text)
    if not result_json:
        return None, raw_text, "invalid_json"

    if not is_valid_result(result_json):
        return None, raw_text, "invalid_sources"

    return result_json, raw_text, ""


# -------- context review module --------

def maybe_build_context_messages(
    thread_id: Optional[str],
    task_id: Optional[str],
    mode: str,
    need_context_hint: Optional[bool],
    db_path: str,
    user_text: str,
) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
    if not thread_id:
        return [], None

    # dynamic import to avoid hard dependency when unused
    root = Path(__file__).resolve().parents[3]
    sys.path.append(str(root))
    from tools.grok_search.context import ContextRouter, ContextStore  # type: ignore

    store = ContextStore(db_path)
    router = ContextRouter(store)
    decision = router.route(
        thread_id=thread_id,
        user_text=user_text,
        task_id=task_id,
        mode=mode,
        need_context_hint=need_context_hint,
    )
    messages = router.build_context_messages(decision.snapshot)
    meta = {
        "thread_id": decision.thread_id,
        "task_id": decision.task_id,
        "include_context": decision.include_context,
        "reason": decision.reason,
    }
    return messages, meta


def record_turn_if_needed(
    thread_id: Optional[str],
    task_id: Optional[str],
    db_path: str,
    user_text: str,
    assistant_text: str,
    meta: Dict[str, Any],
) -> None:
    if not thread_id or not task_id:
        return

    root = Path(__file__).resolve().parents[3]
    sys.path.append(str(root))
    from tools.grok_search.context import ContextRouter, ContextStore  # type: ignore

    store = ContextStore(db_path)
    router = ContextRouter(store)
    router.record_turn(
        thread_id=thread_id,
        task_id=task_id,
        user_text=user_text,
        assistant_text=assistant_text,
        meta=meta,
    )


# -------- CLI --------

def parse_args():
    p = argparse.ArgumentParser(description="Grok search with fallback + context review")

    p.add_argument("--env-file", help="Optional .env path (if set, only this file is loaded)")
    p.add_argument("--query", required=True, help="User question")
    p.add_argument("--system-prompt", default=SYSTEM_PROMPT, help="System prompt (JSON rules)")

    p.add_argument("--thread-id", help="Context thread_id (for recall)")
    p.add_argument("--task-id", help="Context task_id (optional)")
    p.add_argument("--mode", choices=["auto", "stateless", "always"], default="auto")
    p.add_argument("--need-context-hint", choices=["true", "false"], help="Force context include hint")
    p.add_argument("--db", default=os.getenv("CONTEXT_DB_PATH", "./data/context.db"))

    default_model = get_config(["GROK_MODEL"], "model", "grok-4.20-beta")
    default_base_url = get_config(
        ["GROK_BASE_URL", "GAPI_CUSTOM_BASE_URL"],
        "base-url",
        "https://api.example.com",
    )
    default_api_key = get_config(["GROK_API_KEY", "GAPI_CUSTOM_API_KEY"], "api-key")
    try:
        default_timeout = int(os.getenv("GROK_TIMEOUT", "1200"))
    except ValueError:
        default_timeout = 1200

    p.add_argument("--model", default=default_model)
    p.add_argument("--fallback-model", default=os.getenv("GROK_FALLBACK_MODEL", "grok-4.1-thinking"))
    p.add_argument("--base-url", default=default_base_url)
    p.add_argument("--api-key", default=default_api_key)
    p.add_argument("--timeout", type=int, default=default_timeout)
    p.add_argument("--with-meta", action="store_true", help="Include meta wrapper in output")

    return p.parse_args()


def main():
    try:
        env_file = parse_env_file_arg()
        load_env_auto(env_file)
    except Exception as e:
        print(f"env load error: {e}", file=sys.stderr)
        sys.exit(2)

    args = parse_args()

    if not args.api_key or not args.base_url:
        print("missing api-key or base-url", file=sys.stderr)
        sys.exit(2)

    base_url = args.base_url.rstrip("/")

    need_context_hint = None
    if args.need_context_hint == "true":
        need_context_hint = True
    elif args.need_context_hint == "false":
        need_context_hint = False

    context_messages, ctx_meta = maybe_build_context_messages(
        thread_id=args.thread_id,
        task_id=args.task_id,
        mode=args.mode,
        need_context_hint=need_context_hint,
        db_path=args.db,
        user_text=args.query,
    )

    messages = [{"role": "system", "content": args.system_prompt}, *context_messages, {"role": "user", "content": args.query}]

    started = time.time()
    result, raw, err = call_with_validation(base_url, args.api_key, args.model, messages, args.timeout)
    used_model = args.model
    fallback_reason = ""

    if not result:
        fallback_reason = err or "invalid_primary"
        result, raw, err = call_with_validation(base_url, args.api_key, args.fallback_model, messages, args.timeout)
        used_model = args.fallback_model

    elapsed_ms = int((time.time() - started) * 1000)

    if not result:
        meta = {
            "model": used_model,
            "fallback_reason": fallback_reason or err,
            "latency_ms": elapsed_ms,
            "raw_text": raw,
        }
        print(json.dumps({"error": meta}, ensure_ascii=False, indent=2))
        sys.exit(1)

    meta = {
        "model": used_model,
        "fallback_reason": fallback_reason,
        "latency_ms": elapsed_ms,
        "context": ctx_meta or {},
    }

    assistant_text = json.dumps(result, ensure_ascii=False)
    record_turn_if_needed(
        thread_id=(ctx_meta or {}).get("thread_id"),
        task_id=(ctx_meta or {}).get("task_id"),
        db_path=args.db,
        user_text=args.query,
        assistant_text=assistant_text,
        meta={"model": used_model, "fallback_reason": fallback_reason},
    )

    if args.with_meta:
        print(json.dumps({"meta": meta, "result": result}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
