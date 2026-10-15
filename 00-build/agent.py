"""Cortex, a minimal, explicit agent loop you (and your coding agent) can read end
to end. This is the agent you ship: your PM chief-of-staff. You build it by
directing your coding agent (Claude Code / Cursor / Codex) to shape this file. You
never have to hand-write it.

Every bound the course talks about is visible right here in code, not buried in a
framework: the max-iteration counter, the cost cap, the revision cap, the
stop/escalate conditions, the auto-queue cap, and the absence of any publish tool.

Usage (ask your coding agent to run these for you, or run them yourself):
    python agent.py                # runs the happy-path task (weekly status update)
    python agent.py missing-data   # the stuck/escalate case
    python agent.py jailbreak       # the prompt-injection refusal case

Every CLI run saves its full trace to a timestamped file in run-output/ and prints
only the result and file paths. The trace includes a FINAL STATUS UPDATE block
(or LAST DRAFT, held, if a bound trips). The draft is also saved separately. That file is
always a draft held for a human, it is never posted, there is no publish tool.

Requires OPENAI_API_KEY in your environment (see .env.example). Model and bounds
are read from env so you can tune them, that tuning is your M5 deliverable.

The loop is deliberately transparent (hand-written tool-calling on the openai
client) so a grader can see the machinery. Keep the bounds explicit if you rework it.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import traceback
import time
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

import tools
from critic import review
from prompts import CORTEX_SYSTEM, DRAFT_FORMAT
from loop_state import RunStopped, SelectionHistory, deadline, parse_output, render_output
from model_trace import complete, LOGGER

try:  # load .env if python-dotenv is installed; harmless if it isn't
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# --- Bounds (your M5 deliverable: tune these and justify them) ----------------
MODEL = os.environ.get("CORTEX_MODEL", "gpt-4o-mini")
# The validator needs reliable rule following independently of the drafter.
CRITIC_MODEL = os.environ.get("CORTEX_CRITIC_MODEL", "gpt-4.1-mini")
MAX_ITERATIONS = int(os.environ.get("CORTEX_MAX_ITERATIONS", "8"))
# The approved M2 policy supersedes the older .env revision setting.
MAX_REVISIONS = 3
MAX_RUN_SECONDS = 300
COST_CAP_USD = float(os.environ.get("CORTEX_COST_CAP_USD", "0.50"))
MAX_QUEUE_ITEMS = int(os.environ.get("CORTEX_MAX_QUEUE_ITEMS", "10"))
# Rough $ per 1M tokens for your chosen model, set to match its pricing.
PRICE_IN = float(os.environ.get("CORTEX_PRICE_IN_PER_M", "0.15"))
PRICE_OUT = float(os.environ.get("CORTEX_PRICE_OUT_PER_M", "0.60"))
CRITIC_PRICE_IN = float(os.environ.get("CORTEX_CRITIC_PRICE_IN_PER_M", "0.40"))
CRITIC_PRICE_OUT = float(os.environ.get("CORTEX_CRITIC_PRICE_OUT_PER_M", "1.60"))

TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "get_project", "description": "Look up a project by its ID (status, flags, linked PRD).",
        "parameters": {"type": "object", "properties": {
            "project_id": {"type": "string"}}, "required": ["project_id"]}}},
    {"type": "function", "function": {
        "name": "get_activity",
        "description": "Pull recent engineering activity for a project (merged PRs, open issues, Sev-1s).",
        "parameters": {"type": "object", "properties": {
            "project_id": {"type": "string"}}, "required": ["project_id"]}}},
    {"type": "function", "function": {
        "name": "search_past_updates",
        "description": "Search previous status updates and decisions for tone and precedent.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {
        "name": "get_roadmap",
        "description": "Return the roadmap. Some items are flagged confidential/embargoed.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {
        "name": "get_norms", "description": "Return the team norms / PM playbook the agent must follow.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {
        "name": "propose_stories",
        "description": "Queue a set of backlog stories for human approval (creates nothing; rejected above the item cap).",
        "parameters": {"type": "object", "properties": {
            "project_id": {"type": "string"},
            "stories": {"type": "array", "items": {"type": "string"}},
            "reason": {"type": "string"}}, "required": ["project_id", "stories"]}}},
]


class Bounds:
    """Tracks spend and trips the cost cap. This is enforced OUTSIDE the model."""

    def __init__(self):
        self.cost = 0.0

    def add(self, usage) -> None:
        self.cost += (usage.prompt_tokens * PRICE_IN
                      + usage.completion_tokens * PRICE_OUT) / 1_000_000

    def over_cap(self) -> bool:
        return self.cost >= COST_CAP_USD


OUTPUT_DIR = Path(__file__).parent / "run-output"


def banner(text: str) -> None:
    print(f"\n{'=' * 64}\n{text}\n{'=' * 64}")


def emit_deliverable(which: str, draft: str, *, accepted: bool,
                     reason: str, cost: float) -> None:
    """Surface AND persist Cortex's drafted status update so it can't get lost in
    the scroll-back. This is still a DRAFT held for human review, never a post,
    there is no publish tool, and an escalated run is held on purpose.

    Runs on every exit: an accepted pass prints the FINAL update; a bound trip or
    escalation prints the LAST draft it managed to write plus why it was held.
    """
    banner("FINAL STATUS UPDATE (draft, validator-approved, NOT posted)" if accepted
           else "LAST DRAFT (held, NOT posted, escalated to a human)")
    if draft.strip():
        print(draft.rstrip())
    else:
        print("(Cortex stopped before it produced a draft, nothing to show.)")
    if not accepted:
        print(f"\nWhy it was held: {reason}")

    if draft.strip():
        OUTPUT_DIR.mkdir(exist_ok=True)
        out = OUTPUT_DIR / f"status-update-{which}.md"
        state = "accepted by validator" if accepted else "HELD, escalated"
        out.write_text(
            f"<!-- Cortex draft, {state}; NOT posted. Run cost ~ ${cost:.4f}. -->\n"
            f"<!-- {reason} -->\n\n{draft.rstrip()}\n", encoding="utf-8")
        print(f"\nSaved draft -> {out.relative_to(Path(__file__).parent)}  "
              f"(for your review, nothing was posted)")


def run(which: str = "happy") -> None:
    # No SDK retries: a retry must not silently extend the overall deadline.
    client = OpenAI(max_retries=0)
    bounds = Bounds()
    started = time.monotonic()
    history = SelectionHistory()
    output = None
    previous_output = ""
    latest_text = ""
    wording_only_count = 0
    accepted = False
    reason = "run did not complete"

    def check_bounds():
        if time.monotonic() - started >= MAX_RUN_SECONDS:
            raise RunStopped(f"time limit ({MAX_RUN_SECONDS} seconds) reached")
        if bounds.over_cap():
            raise RunStopped(f"cost cap ${COST_CAP_USD} reached at ${bounds.cost:.4f}")

    def draft_call(**request):
        check_bounds()
        remaining = MAX_RUN_SECONDS - (time.monotonic() - started)
        response = complete(client.with_options(timeout=remaining), role="drafter", **request)
        bounds.add(response.usage)
        check_bounds()
        return response.choices[0].message

    try:
        with deadline(MAX_RUN_SECONDS):
            task = tools.get_task(which)
            if "error" in task:
                raise RunStopped(task["error"])
            print(task["body"])
            messages = [
                {"role": "system", "content": CORTEX_SYSTEM + "\n" + DRAFT_FORMAT},
                {"role": "user", "content": f"PM task brief:\n{task['body']}"},
            ]
            source_log = [task["body"]]
            project_id = ""
            # Original tool-driven flow: Cortex retrieves context as needed and
            # produces its initial output in the same conversation.
            read_schemas = [s for s in TOOL_SCHEMAS if s["function"]["name"] != "propose_stories"]
            read_names = {s["function"]["name"] for s in read_schemas}
            print("PHASE: retrieve context and produce initial output")
            for turn in range(MAX_ITERATIONS):
                msg = draft_call(model=MODEL, messages=messages, tools=read_schemas,
                                 response_format={"type": "json_object"})
                if not msg.tool_calls:
                    break
                messages.append(msg)
                for call in msg.tool_calls:
                    check_bounds()
                    fn = call.function.name
                    if fn not in read_names:
                        raise RunStopped(f"tool {fn} is not allowed during evidence collection")
                    args = json.loads(call.function.arguments or "{}")
                    result = tools.TOOLS[fn](**args)
                    print(f"TOOL {fn}({args})\n{json.dumps(result, indent=2)}")
                    source_log.append(f"{fn}({args}) -> {json.dumps(result)}")
                    messages.append({"role": "tool", "tool_call_id": call.id,
                                     "content": json.dumps(result)})
                    if fn == "get_project" and not result.get("error"):
                        project_id = result["project_id"]
                    if result.get("error"):
                        raise RunStopped(f"required data unavailable: {fn}: {result['error']}")
                    # These source flags cannot be overridden by a draft or critic.
                    if fn == "get_project" and "launch_hold" in result.get("flags", []):
                        raise RunStopped("requested project has a launch hold")
                    if fn == "get_activity" and any(
                        item.get("severity") == "sev-1" for item in result.get("activity", [])
                    ):
                        raise RunStopped("requested project has an open Sev-1")
            else:
                raise RunStopped(f"data-collection safety cap ({MAX_ITERATIONS} calls) reached")

            evidence = "\n".join(source_log)
            print("PHASE: initial output ready; revisions use existing evidence only")
            revisions = 0
            comparison_followups = 0
            initial_message = msg
            while True:
                if initial_message is not None:
                    msg = initial_message
                    initial_message = None
                else:
                    msg = draft_call(model=MODEL, messages=messages,
                                     response_format={"type": "json_object"})
                latest_text = msg.content or ""
                print(f"DRAFT RESPONSE (revision {revisions}/{MAX_REVISIONS}):\n{latest_text}")
                try:
                    candidate = parse_output(latest_text)
                except (ValueError, TypeError) as error:
                    # An invalid envelope never reaches success or selection tracking.
                    raise RunStopped(f"invalid draft structure: {error}") from error
                output = candidate
                history.observe(output)
                if output["needs_new_data"]:
                    raise RunStopped("new evidence required: " + output["reason"])
                if output["status"] == "escalate":
                    # Critic still checks an escalation for confidentiality before release.
                    pass
                elif output["status"] == "compare":
                    if not history.comparisons or comparison_followups >= 1:
                        raise RunStopped("selection unresolved after 2 comparison opportunities")
                    comparison_followups += 1
                    messages.extend([
                        {"role": "assistant", "content": latest_text},
                        {"role": "user", "content": "Make the second comparison using frozen evidence. "
                         "Resolve selection or escalate. Do not retrieve new data."},
                    ])
                    continue

                check_bounds()
                verdict = review(client.with_options(timeout=MAX_RUN_SECONDS - (time.monotonic() - started)),
                                 CRITIC_MODEL, latest_text, evidence, previous_output)
                bounds.cost += (verdict["_usage"]["prompt"] * CRITIC_PRICE_IN
                                + verdict["_usage"]["completion"] * CRITIC_PRICE_OUT) / 1_000_000
                print("CRITIC: " + json.dumps({k: v for k, v in verdict.items() if k != "_usage"}))
                check_bounds()
                if previous_output:
                    wording_only_count = wording_only_count + 1 if verdict["wording_only"] else 0
                if wording_only_count >= 2:
                    raise RunStopped("2 consecutive wording-only revisions")
                if output["status"] == "escalate":
                    if verdict["verdict"] != "pass":
                        raise RunStopped("critic held escalation: " + "; ".join(verdict["reasons"]))
                    raise RunStopped(output["reason"])
                if verdict["verdict"] == "pass":
                    check_bounds()
                    if not project_id:
                        raise RunStopped("requested project record was not collected")
                    result = tools.propose_stories(
                        project_id=project_id,
                        stories=[c["title"] for c in output["candidates"] if c["id"] in output["selected"]])
                    print("STORY PROPOSAL: " + json.dumps(result))
                    if result.get("status") != "queued_for_approval":
                        raise RunStopped("story proposal rejected: " + json.dumps(result))
                    accepted = True
                    reason = "critic passed; output queued for human review"
                    break
                if revisions >= MAX_REVISIONS:
                    raise RunStopped("3 revisions exhausted; critic still rejects output")
                previous_output = latest_text
                revisions += 1
                messages.extend([
                    {"role": "assistant", "content": latest_text},
                    {"role": "user", "content": "Revise this output using ONLY frozen evidence. "
                     "No retrieval or restarting. Critic feedback: " + json.dumps(verdict["reasons"])},
                ])
    except RunStopped as stop:
        accepted = False
        reason = str(stop)
    except Exception as error:
        accepted = False
        reason = (f"time limit ({MAX_RUN_SECONDS} seconds) reached"
                  if time.monotonic() - started >= MAX_RUN_SECONDS
                  else f"run error: {type(error).__name__}: {error}")
        traceback.print_exc()
    finally:
        print(f"STOP: {reason}; elapsed {time.monotonic() - started:.2f}s; estimated cost ${bounds.cost:.6f}")
        emit_deliverable(which, render_output(output, history), accepted=accepted,
                         reason=reason, cost=bounds.cost)


def run_to_file(which: str = "happy") -> int:
    """Keep each CLI run's trace, including errors, out of terminal scrollback."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    trace_path = OUTPUT_DIR / f"trace-{stamp}.log"
    failed = False
    with trace_path.open("x", encoding="utf-8") as trace:
        handler = logging.StreamHandler(trace)
        old_level = LOGGER.level
        old_propagate = LOGGER.propagate
        LOGGER.setLevel(logging.INFO)
        LOGGER.propagate = False
        LOGGER.addHandler(handler)
        try:
            with redirect_stdout(trace), redirect_stderr(trace):
                print(f"Cortex trace (UTC): {stamp}; fixture: {which}")
                print(f"Drafter: {MODEL}; critic: {CRITIC_MODEL}")
                print(f"Bounds: collection calls={MAX_ITERATIONS}, revisions={MAX_REVISIONS}, "
                      f"seconds={MAX_RUN_SECONDS}, "
                      f"cost=${COST_CAP_USD}, queue={MAX_QUEUE_ITEMS}")
                print("Records observable API payloads, tool results and checks; "
                      "not private model reasoning. Client credentials are not logged.")
                try:
                    run(which)
                except Exception:
                    failed = True
                    traceback.print_exc()
        finally:
            LOGGER.removeHandler(handler)
            LOGGER.setLevel(old_level)
            LOGGER.propagate = old_propagate
    print(f"{'Run failed; see trace' if failed else 'Run finished; see trace'}: {trace_path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run_to_file(sys.argv[1] if len(sys.argv) > 1 else "happy"))
