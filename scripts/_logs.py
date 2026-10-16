"""Shared helpers for reading scored Inspect logs."""
from __future__ import annotations

from inspect_ai.log import read_eval_log

DIMS = ["contextual_judgment", "usefulness", "paternalism"]


def scored_rows(log_path: str) -> dict:
    """Return {(sample_id, epoch): {...}} with dimension levels, labels and criteria verdicts."""
    log = read_eval_log(log_path)
    grader = None
    roles = getattr(log.eval, "model_roles", None) or {}
    if "grader" in roles:
        g = roles["grader"]
        grader = getattr(g, "model", None) or str(g)
    rows = {}
    for s in log.samples or []:
        sc = s.scores or {}
        d0 = sc.get("dimension_scorer")
        if d0 and (d0.metadata or {}).get("grader_model"):
            grader = d0.metadata["grader_model"]
        d = sc.get("dimension_scorer")
        l = sc.get("label_scorer")
        c = sc.get("criteria_scorer")
        rows[(str(s.id), s.epoch)] = {
            "dims": dict(d.value) if d and isinstance(d.value, dict) else {},
            "dim_detail": (d.metadata or {}).get("detail", {}) if d else {},
            "labels": sorted(int(k.split("_")[1]) for k, v in (l.value or {}).items() if v) if l and isinstance(l.value, dict) and l.value else None,
            "criteria": [(v["text"], v.get("met")) for v in (c.metadata or {}).get("verdicts", [])] if c else [],
            "criteria_value": (c.value or {}).get("criteria") if c and isinstance(c.value, dict) else None,
            "reply": s.output.completion if s.output else "",
        }
    return {"model": log.eval.model, "grader": grader, "rows": rows}
