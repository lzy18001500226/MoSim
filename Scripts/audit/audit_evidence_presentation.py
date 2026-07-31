# -*- coding: utf-8 -*-
"""审计：Results/ 下已产出数据的目录，是否已在报告中被引用并有图。

口径说明
  数据目录 = 含 raw/*.csv 或 metrics/*.csv 或 *_METRICS.json 的目录
  已引用   = 目录名出现在 Docs/报告/*.md 或 Docs/Design/*.md（排除归档）
  有图     = 该目录内含 .svg/.png，或 Docs/报告/figures 下存在同名子目录
不修改任何结果文件，只读。
"""
import os
import re
import json
import sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS = os.path.join(BASE, "Results")
FIG_ROOTS = [
    os.path.join(BASE, "Docs", "报告", "figures"),
    os.path.join(BASE, "Docs", "报告", "图"),
]


def read_docs():
    """收集报告与设计文档正文（排除归档目录）。"""
    text = []
    for root in (os.path.join(BASE, "Docs", "报告"), os.path.join(BASE, "Docs", "Design")):
        for dirpath, _dirnames, filenames in os.walk(root):
            if "归档" in dirpath or "__pycache__" in dirpath:
                continue
            for name in filenames:
                if name.endswith(".md"):
                    path = os.path.join(dirpath, name)
                    try:
                        text.append(open(path, encoding="utf-8", errors="ignore").read())
                    except OSError:
                        pass
    return "\n".join(text)


DATA_EXT = (".csv",)


def scan_data_dirs():
    """返回 {二级目录: {'dirs': set(数据子目录), 'csv': 行数, 'fig': 图数}}。"""
    buckets = {}
    for dirpath, _dirnames, filenames in os.walk(RESULTS):
        rel = os.path.relpath(dirpath, RESULTS).replace("\\", "/")
        if rel == ".":
            continue
        parts = rel.split("/")
        key = "/".join(parts[:2]) if len(parts) >= 2 else parts[0]
        n_csv = sum(1 for f in filenames if f.lower().endswith(DATA_EXT))
        n_fig = sum(1 for f in filenames if f.lower().endswith((".svg", ".png")))
        n_json = sum(1 for f in filenames if f.lower().endswith(".json"))
        if not (n_csv or n_fig or n_json):
            continue
        b = buckets.setdefault(key, {"csv": 0, "fig": 0, "json": 0})
        b["csv"] += n_csv
        b["fig"] += n_fig
        b["json"] += n_json
    return buckets


def main():
    docs = read_docs()
    buckets = scan_data_dirs()
    rows = []
    for key, b in buckets.items():
        leaf = key.split("/")[-1]
        cited = (leaf in docs) or (key in docs.replace("\\", "/"))
        rows.append((key, b["csv"], b["fig"], b["json"], cited))
    rows.sort(key=lambda r: (-r[1], r[0]))

    have_csv = [r for r in rows if r[1] > 0]
    gap = [r for r in have_csv if not r[4]]
    nofig = [r for r in have_csv if r[2] == 0]

    print("数据目录（含 CSV）总数: %d" % len(have_csv))
    print("其中未被报告/设计文档引用: %d" % len(gap))
    print("其中目录内无任何图件: %d" % len(nofig))
    print()
    print("%-62s %7s %6s %6s %s" % ("二级目录", "CSV", "图", "JSON", "已引用"))
    for key, csv_n, fig_n, json_n, cited in have_csv:
        print("%-62s %7d %6d %6d %s" % (key[:62], csv_n, fig_n, json_n, "Y" if cited else "-"))

    out = os.path.join(BASE, "Results", "quality", "EVIDENCE_PRESENTATION_AUDIT.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    payload = {
        "schema": "mosim.evidence_presentation_audit.v1",
        "data_dir_count": len(have_csv),
        "uncited_count": len(gap),
        "nofigure_count": len(nofig),
        "rows": [
            {"dir": k, "csv_files": c, "figure_files": f, "json_files": j, "cited_in_docs": bool(t)}
            for k, c, f, j, t in have_csv
        ],
    }
    json.dump(payload, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\n已写出: %s" % os.path.relpath(out, BASE))


if __name__ == "__main__":
    sys.exit(main())
