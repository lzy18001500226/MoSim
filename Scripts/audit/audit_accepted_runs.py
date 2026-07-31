# -*- coding: utf-8 -*-
"""审计：Results/ 下"已通过/已接受"的运行，是否有图、是否已在报告中引用。

只取显式合格状态，过滤掉大量历史调试目录：
  status in {passed, accepted, valid, completed} 或 accepted == True
输出未被引用、或无图的合格证据，作为"做了但没展示/没分析"的缺口清单。
只读，不修改任何结果文件。
"""
import os
import json

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS = os.path.join(BASE, "Results")
PASS_STATUS = {"passed", "accepted", "valid", "pass"}
SKIP_TOP = {"Cache", "tmp", "coagent_status", "logs"}


def read_docs():
    text = []
    for root in (os.path.join(BASE, "Docs", "报告"), os.path.join(BASE, "Docs", "Design")):
        for dirpath, _dn, filenames in os.walk(root):
            if "归档" in dirpath or "__pycache__" in dirpath:
                continue
            for name in filenames:
                if name.endswith(".md"):
                    try:
                        text.append(open(os.path.join(dirpath, name), encoding="utf-8", errors="ignore").read())
                    except OSError:
                        pass
    return "\n".join(text)


def is_pass(obj):
    if not isinstance(obj, dict):
        return False
    if obj.get("accepted") is True:
        return True
    st = obj.get("status")
    return isinstance(st, str) and st.strip().lower() in PASS_STATUS


def collect():
    """返回合格运行记录：{二级目录: {'files':[...], 'csv':n, 'fig':n}}"""
    runs = {}
    for dirpath, _dn, filenames in os.walk(RESULTS):
        rel = os.path.relpath(dirpath, RESULTS).replace("\\", "/")
        if rel == ".":
            continue
        parts = rel.split("/")
        if parts[0] in SKIP_TOP:
            continue
        key = "/".join(parts[:2]) if len(parts) >= 2 else parts[0]
        for name in filenames:
            if not name.endswith(".json"):
                continue
            path = os.path.join(dirpath, name)
            try:
                if os.path.getsize(path) > 6_000_000:
                    continue
                obj = json.load(open(path, encoding="utf-8"))
            except Exception:
                continue
            if is_pass(obj):
                runs.setdefault(key, {"files": [], "csv": 0, "fig": 0})["files"].append(
                    os.path.relpath(path, RESULTS).replace("\\", "/")
                )
    for key in runs:
        root = os.path.join(RESULTS, *key.split("/"))
        for dirpath, _dn, filenames in os.walk(root):
            runs[key]["csv"] += sum(1 for f in filenames if f.lower().endswith(".csv"))
            runs[key]["fig"] += sum(1 for f in filenames if f.lower().endswith((".svg", ".png")))
    return runs


def main():
    docs = read_docs()
    runs = collect()
    rows = []
    for key, info in runs.items():
        leaf = key.split("/")[-1]
        cited = leaf in docs
        rows.append((key, len(info["files"]), info["csv"], info["fig"], cited))
    rows.sort(key=lambda r: (r[4], -r[2], r[0]))

    total = len(rows)
    uncited = [r for r in rows if not r[4]]
    nofig = [r for r in rows if r[3] == 0]
    print("合格运行目录总数: %d" % total)
    print("  未被报告/设计文档引用: %d" % len(uncited))
    print("  目录内无任何图件:     %d" % len(nofig))
    print()
    print("%-58s %5s %5s %5s %s" % ("二级目录", "合格JSON", "CSV", "图", "引用"))
    for key, nj, nc, nf, cited in rows:
        print("%-58s %5d %5d %5d %s" % (key[:58], nj, nc, nf, "Y" if cited else "-"))

    out = os.path.join(BASE, "Results", "quality", "ACCEPTED_RUN_PRESENTATION_AUDIT.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(
        {
            "schema": "mosim.accepted_run_presentation_audit.v1",
            "accepted_dir_count": total,
            "uncited_count": len(uncited),
            "nofigure_count": len(nofig),
            "rows": [
                {"dir": k, "pass_json_count": nj, "csv_files": nc, "figure_files": nf, "cited_in_docs": bool(t)}
                for k, nj, nc, nf, t in rows
            ],
        },
        open(out, "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=2,
    )
    print("\n已写出: %s" % os.path.relpath(out, BASE))


if __name__ == "__main__":
    main()
