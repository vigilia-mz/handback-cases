"""Compare the author's blind scores with the grader's (and with a second rater, if any).

    python scripts/agreement.py --rater ratings/rater1_scoring.xlsx --key ratings/rater1_key.json \
        --grader logs/<scored log>.eval [--grader logs/<second grader>.eval] \
        [--rater2 ratings/rater2_scoring.xlsx --key2 ratings/rater2_key.json]

Reports, per dimension, exact agreement and agreement within one level, with counts.
No kappa or alpha below 20 items, and the report says why. Writes ratings/agreement_report.md,
including a row-by-row comparison table and the rows that differ by two or more levels.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _logs import DIMS, scored_rows  # noqa: E402

MIN_N_FOR_KAPPA = 20


def read_rater(xlsx: str, key_path: str) -> dict:
    key = {r["row"]: (r["sample_id"], r["epoch"]) for r in json.loads(Path(key_path).read_text())["rows"]}
    ws = load_workbook(xlsx, data_only=True)["Score"]
    head = [c.value for c in ws[1]]
    col = {h: i for i, h in enumerate(head)}
    out = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]:
            continue
        sid = key[row[0]]

        def lvl(name):
            v = row[col[name]]
            return int(v) if v not in (None, "") else None

        dims = {"contextual_judgment": lvl("Contextual judgment (0-3)"), "usefulness": lvl("Usefulness (0-3)"),
                "paternalism": lvl("Paternalism (0-3, 3 = none)")}
        label_cols = {i: next(v for k, v in col.items() if str(k).startswith(f"L{i} ")) for i in range(1, 6)}
        labels = [i for i, ci in label_cols.items() if str(row[ci] or "").strip().upper() == "Y"]
        crit = []
        for i in range(1, 8):
            v = row[col[f"C{i} met (Y/N)"]]
            if v in ("Y", "N"):
                crit.append(v == "Y")
            elif v != "n/a":
                crit.append(None)
        out[sid] = {"row": row[0], "dims": {k: v for k, v in dims.items() if v is not None}, "labels": labels,
                    "criteria": crit, "reason": row[col["Reason (quote the reply)"]],
                    "notes": row[col["Notes (write ANCHOR? if an anchor did not fit)"]]}
    return out


def compare(a: dict, b: dict, name_a: str, name_b: str) -> list[str]:
    keys = sorted(set(a) & set(b))
    lines = [f"### {name_a} against {name_b} ({len(keys)} replies in common)", "",
             "| Dimension | Exact agreement | Within one level | Items |", "|---|---|---|---|"]
    for d in DIMS:
        pairs = [(a[k]["dims"].get(d), b[k]["dims"].get(d)) for k in keys]
        pairs = [(x, y) for x, y in pairs if x is not None and y is not None]
        n = len(pairs)
        ex = sum(x == y for x, y in pairs)
        w1 = sum(abs(x - y) <= 1 for x, y in pairs)
        lines.append(f"| {d} | {ex}/{n} | {w1}/{n} | {n} |")
    lab_pairs = [(set(a[k]["labels"] or []), set(b[k]["labels"] or [])) for k in keys
                 if a[k]["labels"] is not None and b[k]["labels"] is not None]
    if lab_pairs:
        lines.append("")
        lines.append("| Label | Agreement (applied or not) |")
        lines.append("|---|---|")
        for i in range(1, 6):
            agree = sum((i in x) == (i in y) for x, y in lab_pairs)
            lines.append(f"| L{i} | {agree}/{len(lab_pairs)} |")
    crit_pairs = []
    for k in keys:
        ca = [v if not isinstance(v, tuple) else v[1] for v in a[k]["criteria"]]
        cb = [v if not isinstance(v, tuple) else v[1] for v in b[k]["criteria"]]
        crit_pairs += [(x, y) for x, y in zip(ca, cb) if x is not None and y is not None]
    if crit_pairs:
        lines.append("")
        lines.append(f"Criteria verdicts (met or not): {sum(x == y for x, y in crit_pairs)}/{len(crit_pairs)} agree.")
    n_items = len(keys)
    lines.append("")
    if n_items < MIN_N_FOR_KAPPA:
        lines.append(f"No kappa or alpha: {n_items} items is below {MIN_N_FOR_KAPPA}, where those statistics are too unstable to report.")
    lines.append("")
    return lines


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rater", required=True)
    ap.add_argument("--key", required=True)
    ap.add_argument("--grader", action="append", default=[])
    ap.add_argument("--rater2")
    ap.add_argument("--key2")
    ap.add_argument("--out", default=str(ROOT / "ratings" / "agreement_report.md"))
    a = ap.parse_args()

    r1 = read_rater(a.rater, a.key)
    sources = {"Author": r1}
    if a.rater2:
        sources["Second rater"] = read_rater(a.rater2, a.key2)
    graders = []
    for g in a.grader:
        data = scored_rows(g)
        rows = {(sid, ep): {"dims": v["dims"], "labels": v["labels"], "criteria": [m for _, m in v["criteria"]]}
                for (sid, ep), v in data["rows"].items()}
        graders.append((f"Grader {data['grader']}", rows, data))
        sources[f"Grader {data['grader']}"] = rows

    lines = ["# Agreement report", "", "Each dimension is reported separately. There is no total score.", ""]
    names = list(sources)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            lines += compare(sources[names[i]], sources[names[j]], names[i], names[j])

    if graders:
        gname, grows, gdata = graders[0]
        lines += ["## Row by row: author against " + gname, "",
                  "| Row | Case | Author CJ/U/P | Grader CJ/U/P | Author labels | Grader labels | Largest gap |",
                  "|---|---|---|---|---|---|---|"]
        flagged = []
        for sid in sorted(r1, key=lambda k: r1[k]["row"]):
            au, gr = r1[sid], grows.get(sid)
            if gr is None:
                continue
            fa = "/".join(str(au["dims"].get(d, "-")) for d in DIMS)
            fg = "/".join(str(gr["dims"].get(d, "-")) for d in DIMS)
            gaps = [abs(au["dims"][d] - gr["dims"][d]) for d in DIMS if d in au["dims"] and d in gr["dims"]]
            gap = max(gaps) if gaps else "-"
            lines.append(f"| {au['row']} | {sid[0]} (epoch {sid[1]}) | {fa} | {fg} | {au['labels']} | {gr['labels']} | {gap} |")
            if (isinstance(gap, int) and gap >= 2) or sorted(au["labels"]) != sorted(gr["labels"] or []):
                flagged.append((au, sid, gdata["rows"][sid]))
        lines += ["", "## Rows to discuss (a gap of two or more levels, or different labels)", ""]
        for au, sid, g in flagged:
            lines += [f"### {au['row']} · {sid[0]} epoch {sid[1]}",
                      f"- Author's reason: {au['reason']}", f"- Author's notes: {au['notes']}"]
            for d in DIMS:
                det = g["dim_detail"].get(d) or {}
                lines.append(f"- Grader on {d}: level {g['dims'].get(d, 'unscored')}; quote: {det.get('quote')}; reason: {det.get('reason')}")
            lines.append("")
        if not flagged:
            lines.append("None.")
    out = Path(a.out)
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
