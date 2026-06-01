#!/usr/bin/python3
"""Local web search via a local Responses API endpoint with the `web_search` tool.

Usage:
  /usr/bin/python3 {baseDir}/scripts/local_web_search.py --query "OpenAI Codex CLI" --mode live
  /usr/bin/python3 {baseDir}/scripts/local_web_search.py --query "OpenAI Codex CLI" --mode cached
  /usr/bin/python3 {baseDir}/scripts/local_web_search.py --env-file ~/.openclaw/workspace/.env --query "OpenAI Codex CLI"

Notes:
- Uses POST {BASE_URL}/v1/responses with tools=[{"type":"web_search","external_web_access":true|false}]
- mode=live   => external_web_access=true  (real-time)
- mode=cached => external_web_access=false (cached/indexed)
- mode=disabled => omit the web_search tool

Env loading:
- If --env-file is provided: load only that file.
- Otherwise try, in order (first wins; does not override existing env):
  1) $OPENCLAW_WORKSPACE/.env (if OPENCLAW_WORKSPACE is set)
  2) /workspace/.env (sandbox)
  3) ~/.openclaw/workspace/.env
- If env vars are still missing on macOS, read from Keychain service `openclaw-local-160`
  (accounts: base-url, api-key, model).
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Iterable, List, Optional


def load_env(path: str) -> bool:
    """Load KEY=VALUE lines from a .env file into os.environ (setdefault only).

    Returns True if the file existed and was loaded.
    """
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


def get_config(env_name: str, account: str, default: Optional[str] = None) -> Optional[str]:
    val = os.getenv(env_name)
    if val:
        return val
    kc = keychain_get("openclaw-local-160", account)
    return kc if kc else default


def parse_env_file_arg(argv: Optional[List[str]] = None) -> Optional[str]:
    """Pre-parse --env-file so we can load it before reading other defaults."""
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


def parse_args():
    p = argparse.ArgumentParser(description="Local web search via local Responses API")

    p.add_argument(
        "--env-file",
        help=(
            "Optional .env file path. If set, only this file is loaded; otherwise defaults are tried "
            "($OPENCLAW_WORKSPACE/.env, /workspace/.env, ~/.openclaw/workspace/.env)."
        ),
    )

    p.add_argument("--query", required=True, help="Search query")
    p.add_argument(
        "--mode",
        choices=["live", "cached", "disabled"],
        default=os.getenv("LOCAL_160_WEB_SEARCH_MODE", "live"),
        help="web_search mode: live (external), cached (no external), disabled (omit tool)",
    )
    default_model = get_config("LOCAL_160_MODEL", "model", "gpt-5.2-codex")
    default_base_url = get_config("LOCAL_160_BASE_URL", "base-url", "https://proxy.example.com")
    default_api_key = get_config("LOCAL_160_API_KEY", "api-key")
    try:
        default_timeout = int(os.getenv("LOCAL_160_TIMEOUT", "1200"))
    except ValueError:
        default_timeout = 1200

    p.add_argument("--model", default=default_model)
    p.add_argument("--base-url", default=default_base_url)
    p.add_argument("--api-key", default=default_api_key)
    p.add_argument("--timeout", type=int, default=default_timeout, help="HTTP timeout seconds")
    p.add_argument("--json", action="store_true", help="Output raw JSON")

    return p.parse_args()


def request_search(base_url: str, api_key: str, model: str, query: str, mode: str, timeout: int):
    tools = []
    if mode != "disabled":
        tool = {"type": "web_search"}
        if mode == "live":
            tool["external_web_access"] = True
        elif mode == "cached":
            tool["external_web_access"] = False
        tools.append(tool)

    payload = {
        "model": model,
        "input": query,
        "tools": tools,
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    req = urllib.request.Request(f"{base_url}/v1/responses", data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
        return json.loads(body)


def extract_summary(resp_json):
    text = None
    citations = []

    for item in resp_json.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    text = c.get("text")
                    for ann in c.get("annotations", []):
                        if ann.get("type") == "url_citation":
                            url = ann.get("url")
                            if url and url not in citations:
                                citations.append(url)

    return text, citations


def main():
    try:
        env_file = parse_env_file_arg()
        load_env_auto(env_file)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    args = parse_args()

    if not args.api_key:
        print("ERROR: missing api key. Set LOCAL_160_API_KEY, pass --api-key, or set --env-file.", file=sys.stderr)
        sys.exit(2)

    try:
        resp = request_search(args.base_url, args.api_key, args.model, args.query, args.mode, args.timeout)
    except urllib.error.HTTPError as e:
        print(f"HTTPError {e.code}")
        print(e.read()[:400])
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    if args.json:
        print(json.dumps(resp, ensure_ascii=False))
        return

    text, citations = extract_summary(resp)
    if text:
        print(text)
    if citations:
        print("\nSources:")
        for u in citations[:5]:
            print(u)


if __name__ == "__main__":
    main()
