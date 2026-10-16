"""Compare how the grader scored the author's constructed (gaming) replies with what the
author expected. Reports every probe, including the ones that fooled the grader.

    python scripts/gaming_report.py logs/<scored handback_constructed log>.eval [more logs for a grader swap]
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _logs import scored_rows  # noqa: E402


def check(exp: dict, got: dict, rows: dict | None = None) -> list[tuple[str, str, str, bool]]:
    out = []
    if exp.get("same_as"):
        other = (rows or {}).get((exp["same_as"], 1))
        if other is None:
            return [("same scores as " + exp["same_as"], "present in log", "missing", False)]
        for dim in ["contextual_judgment", "usefulness", "paternalism"]:
            a, b = got["dims"].get(dim), other["dims"].get(dim)
            out.append((f"{dim} same as {exp['same_as']}", "unscored" if b is None else str(b),
                        "unscored" if a is None else str(a), a is not None and a == b))
        out.append((f"labels same as {exp['same_as']}", str(other["labels"]), str(got["labels"]),
                    got["labels"] is not None and got["labels"] == other["labels"]))
        ca, cb = got.get("criteria_value"), other.get("criteria_value")
        out.append((f"criteria score same as {exp['same_as']}", "unscored" if cb is None else f"{cb:.2f}",
                    "unscored" if ca is None else f"{ca:.2f}", ca is not None and cb is not None and abs(ca - cb) < 1e-9))
        diff = [f"{tx[:60]} ({'met' if a else 'not met'} vs {'met' if b else 'not met'})"
                for (tx, a), (_, b) in zip(got["criteria"], other["criteria"]) if a != b]
        if diff:
            out.append(("criteria that flipped", "none", "; ".join(diff), False))
        return out
    labels = got["labels"]
    if "labels_include" in exp:
        ok = labels is not None and all(x in labels for x in exp["labels_include"])
        out.append(("labels include", str(exp["labels_include"]), str(labels), ok))
    if "labels_exactly" in exp:
        ok = labels is not None and sorted(labels) == sorted(exp["labels_exactly"])
        out.append(("labels exactly", str(exp["labels_exactly"]), str(labels), ok))
    for dim, rule in (exp.get("dimensions") or {}).items():
        v = got["dims"].get(dim)
        ok = v is not None and v <= rule["max"]
        out.append((dim, f"at most {rule['max']}", "unscored" if v is None else str(v), ok))
    verdicts = dict(got["criteria"])
    for text in exp.get("criteria_met") or []:
        v = verdicts.get(text)
        out.append((f"criterion met: {text[:50]}", "met", {True: "met", False: "not met", None: "unscored"}[v], v is True))
    return out


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="+")
    ap.add_argument("--out", default=str(ROOT / "ratings" / "gaming_report.md"))
    a = ap.parse_args()
    expected = yaml.safe_load((ROOT / "responses/constructed/expected_structured.yaml").read_text(encoding="utf-8"))
    probes = {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in (ROOT / "responses/constructed").glob("G*.yaml")}
    lines = ["# Gaming test report", ""]
    for path in a.logs:
        data = scored_rows(path)
        lines += [f"## Grader: {data['grader']}  (log: {Path(path).name})", ""]
        held = fooled = missing = 0
        for gid in sorted(probes):
            p = probes[gid]
            exp = expected.get(gid) or {}
            got = data["rows"].get((gid, 1))
            if not p.get("reply"):
                lines += [f"### {gid} · {p['probe']} · {p['case']}: not run ({p['status']})", ""]
                continue
            if got is None:
                lines += [f"### {gid} · {p['probe']}: not graded in this log", ""]
                continue
            res = check(exp, got, data["rows"])
            if not res:
                lines += [f"### {gid} · {p['probe']}: no checks defined", ""]
                continue
            ok = all(r[3] for r in res)
            unscored = any(r[2] in ("unscored", "None") for r in res)
            held += ok
            fooled += (not ok) and not unscored
            missing += unscored
            verdict = "rubric held" if ok else ("UNSCORED (grader output could not be parsed)" if unscored else "DIFFERS FROM EXPECTED (see the notes at the end)")
            lines += [f"### {gid} · {p['probe']} · case {p['case']}: {verdict}", "",
                      "| Check | Expected | Grader gave | Holds |", "|---|---|---|---|"]
            lines += [f"| {a} | {b} | {c} | {'yes' if d else 'NO'} |" for a, b, c, d in res]
            lines.append("")
        lines += [f"Rubric held: {held}. Differs from expected: {fooled}. Unscored: {missing}.", ""]
    notes = ROOT / "ratings" / "gaming_notes.md"
    if notes.exists():
        lines += ["", notes.read_text(encoding="utf-8")]
    out = Path(a.out)
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
