"""Load gold case YAML files into Inspect samples.

Each sample's input is the full scripted history as chat messages, ending with the
final user turn, so the model under test answers only that final turn. The whole case
travels in metadata for the scorers.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import ChatMessageAssistant, ChatMessageSystem, ChatMessageUser

ROOT = Path(__file__).resolve().parents[1]


def load_case(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def case_messages(case: dict) -> list:
    msgs: list = []
    if case.get("system_prompt"):
        msgs.append(ChatMessageSystem(content=case["system_prompt"]))
    for t in case["turns"]:
        msgs.append(ChatMessageUser(content=t["user"]))
        msgs.append(ChatMessageAssistant(content=t["assistant"]))
    msgs.append(ChatMessageUser(content=case["final_user"]))
    return msgs


def load_rubric() -> dict:
    dims = yaml.safe_load((ROOT / "rubric/dimensions.yaml").read_text(encoding="utf-8"))
    labels = yaml.safe_load((ROOT / "rubric/labels.yaml").read_text(encoding="utf-8"))
    return {"dimensions": dims["dimensions"], "labels": labels["labels"]}


def case_metadata(case: dict) -> dict:
    keep = ["id", "type", "domain", "mechanism", "mirror_of", "variant", "values_stated",
            "hands_over", "judgment_rests_on", "criteria", "status"]
    return {k: case.get(k) for k in keep}


def gold_dataset(cases_dir: str = "cases/gold", allow_drafts: bool = False) -> MemoryDataset:
    samples = []
    for path in sorted((ROOT / cases_dir).glob("*.yaml")):
        case = load_case(path)
        if case.get("status") == "draft" and not allow_drafts:
            raise ValueError(
                f"{path.name} has status 'draft' (runnable text not yet approved). "
                "Approve it in cases/drafts/runnable_text_v0.3.yaml and re-import, "
                "or pass -T allow_drafts=true for a mock dry run only.")
        samples.append(Sample(id=case["id"], input=case_messages(case), metadata=case_metadata(case)))
    return MemoryDataset(samples, name="handback-gold")


def constructed_dataset(allow_drafts: bool = False) -> MemoryDataset:
    """Constructed (author-written) replies, attached to the case they answer."""
    cases = {p.stem: load_case(p) for p in (ROOT / "cases/gold").glob("*.yaml")}
    samples = []
    for path in sorted((ROOT / "responses/constructed").glob("*.yaml")):
        r = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not r.get("reply"):
            continue  # pending: no text yet
        if r.get("requires_approval") and not r.get("approved_by_author") and not allow_drafts:
            continue  # drafted by Claude, not yet approved by the author
        case = cases[r["case"]]
        if case.get("status") == "draft" and not allow_drafts:
            raise ValueError(f"case {case['id']} is still a draft; see gold_dataset()")
        md = case_metadata(case)
        md.update({"constructed_id": r["id"], "probe": r["probe"], "constructed_reply": r["reply"],
                   "expected": r.get("expected"), "source": "constructed"})
        samples.append(Sample(id=r["id"], input=case_messages(case), metadata=md))
    return MemoryDataset(samples, name="handback-constructed")
