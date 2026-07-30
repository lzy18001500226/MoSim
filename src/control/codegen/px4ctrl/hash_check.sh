#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
manifest_path="${1:-${script_dir}/codegen_manifest.json}"

python3 - "${script_dir}" "${manifest_path}" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
manifest = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
entries = [("modelica_source", manifest["modelica_source"])]
for section in ("generated_files", "delivery_files", "binary_evidence"):
    entries.extend((section, entry) for entry in manifest.get(section, []))

failed = False
for section, entry in entries:
    path = (root / entry["path"]).resolve()
    if not path.is_file():
        print(f"{section} missing: {entry['path']}", file=sys.stderr)
        failed = True
        continue
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    expected = entry["sha256"]
    if actual != expected:
        print(
            f"{section} hash mismatch: {entry['path']} expected {expected} actual {actual}",
            file=sys.stderr,
        )
        failed = True
    else:
        print(f"OK {section} {entry['path']}")

if failed:
    raise SystemExit(1)
print("All manifest hashes match.")
PY
