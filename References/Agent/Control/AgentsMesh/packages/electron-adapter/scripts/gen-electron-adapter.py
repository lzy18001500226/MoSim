#!/usr/bin/env python3
"""Convert tauri-adapter files to electron-adapter."""
import re
import shutil
from pathlib import Path

SRC = Path("packages/tauri-adapter/src")
DST = Path("packages/electron-adapter/src")

def snake_to_camel(s):
    parts = s.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])

def convert_invoke(text):
    """Convert invoke("cmd_name", { a, b }) → invoke("cmdName", a, b)."""
    # Pattern 1: invoke<T>("cmd", { args })
    def repl(m):
        generic = m.group(1) or ""
        cmd = m.group(2)
        args_block = m.group(3) or ""
        camel = snake_to_camel(cmd)
        # Parse arguments
        args_block = args_block.strip()
        if not args_block:
            return f'invoke{generic}("{camel}")'
        # Handle shorthand: { podKey, status }
        parts = []
        for p in args_block.split(","):
            p = p.strip()
            if ":" in p:
                name, val = p.split(":", 1)
                parts.append(val.strip())
            elif p:
                parts.append(p)
        if parts:
            return f'invoke{generic}("{camel}", {", ".join(parts)})'
        return f'invoke{generic}("{camel}")'

    text = re.sub(
        r'invoke(<[^>]+>)?\("([a-z_][\w]*)"(?:,\s*\{([^}]*)\})?\)',
        repl,
        text,
    )
    return text

def convert_file(src: Path, dst: Path):
    text = src.read_text()
    # Replace the invoke import
    text = text.replace(
        'import { invoke } from "@tauri-apps/api/core"',
        'import { invoke } from "./invoke"',
    )
    # Convert all invoke() calls
    text = convert_invoke(text)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text)

def main():
    DST.mkdir(parents=True, exist_ok=True)
    count = 0
    for src_file in SRC.glob("*.ts"):
        if src_file.name in ("provider.ts", "index.ts", "state_adapters.ts"):
            continue  # handle separately
        dst_file = DST / src_file.name
        convert_file(src_file, dst_file)
        count += 1
    print(f"Converted {count} adapter files")

if __name__ == "__main__":
    main()
