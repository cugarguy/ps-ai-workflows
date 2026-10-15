"""M2 run state: deterministic limits around model-reported decisions."""

import json
import signal
from contextlib import contextmanager


class RunStopped(Exception):
    pass


@contextmanager
def deadline(seconds):
    """Interrupt even an in-flight SDK call at the run's wall-clock limit (Unix CLI)."""
    def expired(*_):
        raise RunStopped(f"time limit ({seconds:g} seconds) reached")
    previous = signal.signal(signal.SIGALRM, expired)
    previous_timer = signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, *previous_timer)
        signal.signal(signal.SIGALRM, previous)


def parse_output(text):
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("output must be an object")
    if value.get("status") not in ("draft", "compare", "escalate"):
        raise ValueError("invalid status")
    for field in ("reason", "change_reason", "draft"):
        if not isinstance(value.get(field), str):
            raise ValueError(f"missing text field: {field}")
    if type(value.get("needs_new_data")) is not bool:
        raise ValueError("needs_new_data must be boolean")
    candidates = value.get("candidates")
    if not isinstance(candidates, list) or any(
        not isinstance(c, dict) or any(not isinstance(c.get(k), str) or not c[k].strip()
                                     for k in ("id", "title", "evidence", "reason"))
        for c in candidates
    ):
        raise ValueError("invalid candidate records")
    ids = [c["id"] for c in candidates]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate candidate IDs")
    selected = value.get("selected")
    if (not isinstance(selected, list) or any(not isinstance(i, str) for i in selected)
            or len(set(selected)) != len(selected) or not set(selected) <= set(ids)):
        raise ValueError("invalid selected IDs")
    if value["status"] == "draft" and (len(selected) != 2 or not value["draft"].strip()):
        raise ValueError("a draft requires exactly two selected stories and a leadership update")
    comparisons = value.get("comparisons")
    if not isinstance(comparisons, list):
        raise ValueError("comparisons must be a list")
    for c in comparisons:
        if (not isinstance(c, dict) or not isinstance(c.get("options"), list)
                or len(c["options"]) < 2 or any(i not in ids for i in c["options"])
                or not isinstance(c.get("result"), str) or not c["result"].strip()):
            raise ValueError("invalid comparison record")
    if value["status"] in ("compare", "escalate") and not value["reason"].strip():
        raise ValueError("comparison or escalation needs a reason")
    return value


class SelectionHistory:
    def __init__(self):
        self.entries = []
        self.comparisons = []
        self.changes = 0

    def observe(self, output):
        comparisons = output["comparisons"]
        if comparisons[:len(self.comparisons)] != self.comparisons:
            raise RunStopped("comparison history was changed or removed")
        if len(comparisons) > len(self.comparisons) + 1:
            raise RunStopped("more than one comparison reported in one response")
        self.comparisons = comparisons
        selected = output["selected"]
        if selected:
            changed = bool(self.entries and set(selected) != set(self.entries[-1]["selected"]))
            if changed and not output["change_reason"].strip():
                raise RunStopped("selected stories changed without an explanation")
            if not self.entries or changed:
                if changed:
                    self.changes += 1
                self.entries.append({"selected": selected,
                                     "reason": output["change_reason"] if changed else "Initial selection",
                                     "stories": [c for c in output["candidates"] if c["id"] in selected],
                                     "held": self.changes > 2})
                if self.changes > 2:
                    raise RunStopped("third selection change requested; replacement held for human review")
        if output["status"] == "compare" and len(comparisons) >= 2:
            raise RunStopped("story selection unresolved after 2 comparisons")


def render_output(output, history):
    if not output:
        return ""
    lines = [output["draft"], "\n## Selected stories"]
    for c in output["candidates"]:
        if c["id"] in output["selected"]:
            lines.append(f"- {c['id']}: {c['title']} — {c['reason']} (Source: {c['evidence']})")
    lines.append("\n## Other viable stories considered")
    for c in output["candidates"]:
        if c["id"] not in output["selected"]:
            lines.append(f"- {c['id']}: {c['title']} — {c['reason']} (Source: {c['evidence']})")
    lines.append("\n## Selection history")
    for index, entry in enumerate(history.entries):
        label = "Initial selection" if index == 0 else f"Change {index}"
        if entry["held"]:
            label += " (held; exceeds limit)"
        lines.append(f"- {label}: {', '.join(entry['selected'])}. {entry['reason']}")
        for story in entry["stories"]:
            lines.append(f"  - {story['title']}: {story['reason']}")
    if history.comparisons:
        lines.append("\n## Selection comparisons")
        for comparison in history.comparisons:
            lines.append(f"- {', '.join(comparison['options'])}: {comparison['result']}")
    if output["reason"]:
        lines.append(f"\nIssue for review: {output['reason']}")
    return "\n".join(lines).strip()
