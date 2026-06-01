#!/usr/bin/python3
"""Generate or edit images via the Antigravity Gemini image model (through the local gateway).

Usage examples:
  # Text-to-image (default 4K, 16:9)
  mkdir -p ~/.openclaw/workspace/tmp
  /usr/bin/python3 {baseDir}/scripts/generate_gemini_image.py \
    --prompt "A cute yellow chick" \
    --out ~/.openclaw/workspace/tmp/chick.jpg

  # Image edit (img+prompt)
  /usr/bin/python3 {baseDir}/scripts/generate_gemini_image.py \
    --prompt "Add a red scarf" \
    --image /path/to/input.jpg \
    --out ~/.openclaw/workspace/tmp/chick_edit.jpg

Notes:
- Uses Gemini REST via gateway:
  POST {BASE_URL}/v1beta/models/gemini-3.1-flash-image:generateContent
- Auth header: x-goog-api-key: <key>

Env loading:
- If --env-file is provided: load only that file.
- Otherwise try, in order (first wins; does not override existing env):
  1) $OPENCLAW_WORKSPACE/.env (if OPENCLAW_WORKSPACE is set)
  2) ~/.openclaw/workspace/.env
  3) /workspace/.env (if present; sandbox)
- If env vars are still missing on macOS, read from Keychain service `openclaw-local-160`
  (accounts: base-url, api-key).
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Iterable, List, Optional

DEFAULT_MODEL = "gemini-3.1-flash-image"


def load_env(path: str) -> bool:
    """Load KEY=VALUE lines from a .env file into os.environ (setdefault only)."""
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

    paths.append(os.path.expanduser("~/.openclaw/workspace/.env"))

    if os.path.exists("/workspace/.env"):
        paths.append("/workspace/.env")

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
    p = argparse.ArgumentParser(description="Generate/edit images via Gemini (antigravity)")

    p.add_argument(
        "--env-file",
        help=(
            "Optional .env file path. If set, only this file is loaded; otherwise defaults are tried "
            "($OPENCLAW_WORKSPACE/.env, ~/.openclaw/workspace/.env, /workspace/.env if present)."
        ),
    )

    p.add_argument("--prompt", required=True, help="Text prompt")
    p.add_argument("--image", help="Optional input image path for editing")
    p.add_argument("--out", required=True, help="Output image path (jpg/png)")

    default_model = os.getenv("GEMINI_IMAGE_MODEL", DEFAULT_MODEL)
    default_base_url = get_config("LOCAL_160_BASE_URL", "base-url", "https://proxy.example.com")
    default_api_key = get_config("LOCAL_160_API_KEY", "api-key")
    raw_timeout = os.getenv("GEMINI_IMAGE_TIMEOUT") or os.getenv("LOCAL_160_TIMEOUT") or "1200"
    try:
        default_timeout = int(raw_timeout)
    except ValueError:
        default_timeout = 1200

    p.add_argument("--model", default=default_model)
    p.add_argument("--base-url", default=default_base_url)
    p.add_argument("--api-key", default=default_api_key)
    p.add_argument("--timeout", type=int, default=default_timeout, help="HTTP timeout seconds")

    p.add_argument("--temperature", type=float, default=0.3)
    p.add_argument("--size", default=os.getenv("GEMINI_IMAGE_SIZE", "4K"), help="Image size (e.g., 4K)")
    p.add_argument("--ratio", default=os.getenv("GEMINI_IMAGE_RATIO", "16:9"), help="Aspect ratio (e.g., 16:9)")

    return p.parse_args()


def build_parts(prompt: str, image_path: Optional[str]):
    parts = [{"text": prompt}]
    if image_path:
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        mime = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"
        parts.append({"inline_data": {"mime_type": mime, "data": data}})
    return parts


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

    if args.image and not os.path.exists(args.image):
        print(f"ERROR: input image not found: {args.image}", file=sys.stderr)
        sys.exit(2)

    out_path = os.path.expanduser(args.out)
    out_dir = os.path.dirname(os.path.abspath(out_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    payload = {
        "contents": [
            {"role": "user", "parts": build_parts(args.prompt, args.image)},
        ],
        "generationConfig": {
            "temperature": args.temperature,
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "imageSize": args.size,
                "aspectRatio": args.ratio,
            },
        },
    }

    url = f"{args.base_url}/v1beta/models/{args.model}:generateContent"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": args.api_key},
    )

    try:
        # 4K generations can take longer; allow a longer client timeout.
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read()[:800]
        print(f"HTTPError {e.code}: {body}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    parts = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [])
    )

    img_b64 = None
    for p in parts:
        if not isinstance(p, dict):
            continue
        if "inline_data" in p:
            img_b64 = p["inline_data"].get("data")
            break
        if "inlineData" in p:
            img_b64 = p["inlineData"].get("data")
            break

    if not img_b64:
        print("ERROR: no image data in response")
        print(json.dumps(data)[:1200])
        sys.exit(3)

    with open(out_path, "wb") as f:
        f.write(base64.b64decode(img_b64))

    print(out_path)


if __name__ == "__main__":
    main()
