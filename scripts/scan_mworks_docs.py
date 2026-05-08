from pathlib import Path
import json
import csv
from collections import Counter, defaultdict

ROOT = Path("/mnt/c/Users/HP/Desktop/Quadrotor/MWORKS高校星火计划资料包")
OUT_DIR = Path("/mnt/c/Users/HP/Desktop/Quadrotor/docs/mworks/inventory")
INDEX_DIR = Path("/mnt/c/Users/HP/Desktop/Quadrotor/docs/index")

DOC_EXTS = {
    ".pdf", ".doc", ".docx", ".ppt", ".pptx",
    ".xls", ".xlsx", ".txt", ".md", ".html", ".htm",
    ".png", ".jpg", ".jpeg", ".bmp"
}

def classify(path: Path) -> str:
    s = str(path)
    if "安装" in s:
        return "installation"
    if "开放架构" in s or "MCP" in s or "API" in s:
        return "open_architecture_api"
    if "平台介绍" in s:
        return "platform_intro"
    if "MATLAB" in s or "功能对照" in s:
        return "matlab_mapping"
    if "培训" in s or "课程" in s:
        return "training"
    if "产品册" in s or "企业册" in s or "案例册" in s:
        return "brochure_cases"
    return "uncategorized"

def priority(path: Path, category: str) -> str:
    name = path.name.lower()
    ext = path.suffix.lower()

    if category in {"installation", "open_architecture_api", "matlab_mapping"}:
        return "high"

    if "sysplorer" in name or "syslab" in name or "sysblock" in name or "mcp" in name:
        return "high"

    if category == "training":
        return "medium"

    if category in {"platform_intro", "brochure_cases"}:
        return "low"

    if ext in {".pdf", ".docx", ".pptx"}:
        return "medium"

    return "low"

def main():
    if not ROOT.exists():
        raise SystemExit(f"Root not found: {ROOT}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    records = []
    for p in ROOT.rglob("*"):
        if p.is_file():
            ext = p.suffix.lower()
            cat = classify(p)
            rec = {
                "name": p.name,
                "path_wsl": str(p),
                "path_windows": str(p).replace("/mnt/c", "C:").replace("/", "\\"),
                "relative_path": str(p.relative_to(ROOT)),
                "suffix": ext,
                "size_bytes": p.stat().st_size,
                "category": cat,
                "priority": priority(p, cat),
                "convert_candidate": ext in DOC_EXTS,
            }
            records.append(rec)

    records.sort(key=lambda r: (r["category"], r["priority"], r["relative_path"]))

    json_path = OUT_DIR / "mworks_docs_inventory.json"
    csv_path = OUT_DIR / "mworks_docs_inventory.csv"
    md_path = INDEX_DIR / "mworks_source_inventory.md"

    json_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()) if records else [
            "name", "path_wsl", "path_windows", "relative_path", "suffix",
            "size_bytes", "category", "priority", "convert_candidate"
        ])
        writer.writeheader()
        writer.writerows(records)

    by_cat = defaultdict(list)
    for r in records:
        by_cat[r["category"]].append(r)

    lines = []
    lines.append("# MWORKS Source Document Inventory\n")
    lines.append(f"Source root: `{ROOT}`\n")
    lines.append(f"Total files: **{len(records)}**\n")

    suffix_counter = Counter(r["suffix"] or "<no suffix>" for r in records)
    lines.append("## File Type Summary\n")
    lines.append("| Suffix | Count |")
    lines.append("|---|---:|")
    for suffix, count in sorted(suffix_counter.items()):
        lines.append(f"| `{suffix}` | {count} |")

    lines.append("\n## Category Summary\n")
    lines.append("| Category | Count | High | Medium | Low |")
    lines.append("|---|---:|---:|---:|---:|")
    for cat, items in sorted(by_cat.items()):
        pc = Counter(r["priority"] for r in items)
        lines.append(f"| {cat} | {len(items)} | {pc['high']} | {pc['medium']} | {pc['low']} |")

    lines.append("\n## High Priority Conversion Candidates\n")
    lines.append("| Category | File | Type | Size | Path |")
    lines.append("|---|---|---|---:|---|")
    for r in records:
        if r["priority"] == "high" and r["convert_candidate"]:
            lines.append(
                f"| {r['category']} | {r['name']} | `{r['suffix']}` | {r['size_bytes']} | `{r['relative_path']}` |"
            )

    lines.append("\n## All Files\n")
    for cat, items in sorted(by_cat.items()):
        lines.append(f"\n### {cat}\n")
        lines.append("| Priority | File | Type | Size | Relative Path |")
        lines.append("|---|---|---|---:|---|")
        for r in items:
            lines.append(
                f"| {r['priority']} | {r['name']} | `{r['suffix']}` | {r['size_bytes']} | `{r['relative_path']}` |"
            )

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] scanned {len(records)} files")
    print(f"[OK] JSON: {json_path}")
    print(f"[OK] CSV : {csv_path}")
    print(f"[OK] MD  : {md_path}")

if __name__ == "__main__":
    main()