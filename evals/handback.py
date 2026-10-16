"""Inspect tasks for the handback cases.

    handback               the model under test answers the final turn of each gold case
    handback_constructed   author-written replies (the gaming probes) scored by the same scorers

Recommended run, in two steps so the author's scores stay blind:

    # 1. generate only (no grader)
    inspect eval evals/handback.py@handback --model anthropic/<model> --epochs 2 --no-score
    # 2. author scores the exported workbook; only then:
    inspect score logs/<that log>.eval --model-role grader=anthropic/<grader> \
        --output-file logs/scored_grader1.eval
"""
from __future__ import annotations

import sys
from pathlib import Path

# Inspect loads this file by path, so make the repository root importable.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from inspect_ai import Task, task  # noqa: E402
from inspect_ai.model import ChatMessageAssistant, ModelOutput  # noqa: E402
from inspect_ai.solver import Generate, TaskState, generate, solver  # noqa: E402

from evals.dataset import constructed_dataset, gold_dataset  # noqa: E402
from evals.scorers import criteria_scorer, dimension_scorer, label_scorer  # noqa: E402


def _bool(v) -> bool:
    return v if isinstance(v, bool) else str(v).lower() in {"1", "true", "yes"}


@task
def handback(allow_drafts: bool = False) -> Task:
    return Task(
        dataset=gold_dataset(allow_drafts=_bool(allow_drafts)),
        solver=generate(),
        scorer=[dimension_scorer(), label_scorer(), criteria_scorer()],
    )


@solver
def use_constructed_reply():
    """Put the author's constructed reply in place of a model reply. No model is called."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        text = state.metadata["constructed_reply"]
        state.output = ModelOutput.from_content(model="constructed-by-author", content=text)
        state.messages.append(ChatMessageAssistant(content=text))
        return state

    return solve


@task
def handback_constructed(allow_drafts: bool = False) -> Task:
    return Task(
        dataset=constructed_dataset(allow_drafts=_bool(allow_drafts)),
        solver=use_constructed_reply(),
        scorer=[dimension_scorer(), label_scorer(), criteria_scorer()],
    )
