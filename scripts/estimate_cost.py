"""Estimate calls and tokens before any paid run. Prints counts only; it does not know prices.

    python scripts/estimate_cost.py --epochs 2

Token counts are rough (characters divided by 4). Multiply by the current per-token prices
of the models you choose, from the provider's pricing page, to get a cost.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evals.dataset import load_rubric  # noqa: E402
from evals.scorers import anchors_text, labels_text  # noqa: E402

REPLY_TOKENS = 600      # assumed length of one reply from the model under test
GRADER_OUT = 250        # assumed length of one grader answer


def tok(s: str) -> int:
    return len(s) // 4


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=2)
    a = ap.parse_args()
    rubric = load_rubric()
    tmpl = {n: (ROOT / "rubric" / n).read_text() for n in ["grader_dimensions.md", "grader_labels.md", "grader_criterion.md"]}
    cases = [yaml.safe_load(p.read_text()) for p in sorted((ROOT / "cases/gold").glob("*.yaml"))]
    constructed = [yaml.safe_load(p.read_text()) for p in sorted((ROOT / "responses/constructed").glob("G*.yaml"))]
    constructed = [c for c in constructed if c.get("reply")]
    bycase = {c["id"]: c for c in cases}

    gen_calls = gen_in = gen_out = 0
    gr_calls = gr_in = gr_out = 0

    def grading(c: dict, reply_tokens: int):
        nonlocal gr_calls, gr_in, gr_out
        hist = sum(tok(t["user"]) + tok(t["assistant"]) for t in c["turns"]) + tok(c["final_user"])
        calls = [tok(tmpl["grader_dimensions.md"]) + tok(anchors_text(rubric)) + 300,
                 tok(tmpl["grader_labels.md"]) + tok(labels_text(rubric))]
        calls += [tok(tmpl["grader_criterion.md"]) + 30 for _ in c["criteria"]]
        for base in calls:
            gr_calls += 1
            gr_in += base + hist + reply_tokens
            gr_out += GRADER_OUT

    for c in cases:
        hist = sum(tok(t["user"]) + tok(t["assistant"]) for t in c["turns"]) + tok(c["final_user"])
        for _ in range(a.epochs):
            gen_calls += 1
            gen_in += hist
            gen_out += REPLY_TOKENS
            grading(c, REPLY_TOKENS)
    gen_replies = gen_calls
    g_main_calls, g_main_in, g_main_out = gr_calls, gr_in, gr_out
    for r in constructed:
        grading(bycase[r["case"]], tok(r["reply"]))

    print(f"Step 1, generation (model under test): {gen_calls} calls, about {gen_in:,} input and {gen_out:,} output tokens")
    print(f"Step 3, grading the {gen_replies} replies: {g_main_calls} grader calls, about {g_main_in:,} input and {g_main_out:,} output tokens")
    print(f"Step 4, grading {len(constructed)} constructed replies: {gr_calls - g_main_calls} grader calls, "
          f"about {gr_in - g_main_in:,} input and {gr_out - g_main_out:,} output tokens")
    print(f"Total: {gen_calls + gr_calls} calls, about {gen_in + gr_in:,} input and {gen_out + gr_out:,} output tokens.")
    print("A grader swap repeats steps 3 and 4 with the second grader.")
    print("Rough counts (characters / 4, assumed reply and grader lengths). Check prices on the provider's pricing page.")


if __name__ == "__main__":
    main()
