# Loop Spec: Cortex PM Chief-of-Staff Agent

> Module 2 · Loop Engineering, ★ Deliverable 2
>
> ✅ **What this validates:** the agent knows when to run and when to stop, by the end you'll have proven a one-page Loop Spec with a trigger, a definition of "done," and explicit stop conditions.
>
> Your one-page blueprint for how the work you handed to the agent (M1) actually *runs*.
> An agent is just a prompt that fires itself, this spec says when it fires, what "done" means, and what it needs to do the job. Living document; refine as the course progresses.

## 1. Trigger & loop type

**Chosen type:** cron — weekly before the leadership meeting.

Leadership meetings are scheduled. Periodic reporting gives teams time to act because downstream work changes more slowly; frequent updates could cause chaos for the teams.

Hooks respond to events rather than the meeting schedule. Heartbeats check more often than needed. A goal loop does not match the scheduled reporting need; unnecessary continued work could add cost.

**Duplicate prevention:** Identify each report by project and reporting week. If the scheduled job fires twice, avoid producing a second report.

## 2. Goal / definition of done

Cortex considers all viable stories using the current criteria, selects two, and produces a draft leadership update that includes them. It also provides a separate list of the other viable stories considered and the reasons for its selections. The current criteria remain in place for now; refining them comes later.

The outputs must pass the critic and remain queued for human review. Nothing is published or committed as actual work.

## 3. Stop conditions

| Condition | What it looks like | What happens |
|---|---|---|
| **Success** | The draft includes the two selected stories, the separate list of other viable stories and selection reasons is ready, and the outputs pass the critic. | Stop at the human-review checkpoint. |
| **Stuck / give up** | The run reaches 5 minutes or exhausts 3 revisions after the initial draft; makes 2 consecutive wording-only revisions; or needs a third change to the selected pair. | Stop and return the latest draft, selected and unselected stories, the initial selection and each replacement selection with reasons for each change, and the reason the run stopped. |
| **Escalate to human** | Story selection remains unresolved after 2 comparisons; required data is missing; there is an open Sev-1 or launch hold; an update requires an unconfirmed delivery date; a request is outside team rules; a story batch exceeds the cap; or prompt injection is detected. | Stop and present the issue for human judgment. For selection uncertainty, include the competing stories and why the choice remains unresolved. |

The 5-minute limit is provisional until typical run times are known. Allow up to 2 changes to the selected pair; capture why each story was selected and why each change was made.

Collect evidence once before drafting. A revision means incorporating critic feedback into the existing output using that same evidence, not retrieving more data or restarting the process. Allow the initial draft plus up to 3 revisions. If feedback requires new evidence, stop and hand the issue to a human.

## 4. State

Within a run, retain the gathered evidence, candidate stories, selection history and reasons, current draft, and stop-limit counters.

Between weekly runs, retain history for each project and for the overall report: previous reports, stories considered, selected or left out, escalation decisions, reasons, changes over time, and human review feedback. Use the project and reporting week to prevent duplicate reports.

Preserve enough source evidence to reconstruct what was available for each report, including stories that were available but never surfaced. Stable story IDs and source references should support tracing a story over time. Load only relevant history into each new run; retaining history does not mean loading it all. Storage and retrieval details will be addressed in Module 4.

## 5. The five things a loop can lean on

_`state` is always-on. `connectors` only if you already have one wired (e.g. a Jira key or Google MCP), otherwise just note it as a plan. `skills`, `subagents`, `work tree` scale with autonomy; "not needed yet, because…" is a valid answer._

| Component | For Cortex |
|---|---|
| **Work tree** (isolated workspace per run, a git worktree) | Not needed yet; Cortex reads source data and saves draft outputs without changing project code. |
| **Skills** (reusable capabilities) | Not needed yet; the current prompts and tools cover this reporting workflow. Revisit as the course progresses. |
| **Plugins / connectors** (tools & access, optional if you don't have one yet) | Keep the local mock tools for this lab. A live project-data connector is a future plan. |
| **Subagents** (independent check when the loop can't grade itself) | Retain the existing separate critic. Additional agent roles will be addressed in M3 orchestration-map.md. |
| **State tracking** | Retain run state and project and overall reporting history as described in §4. Retrieve only relevant history for each run; storage and retrieval details come in M4. |

> Context plan (M4) and the hand-off to bounds & evals (M5) come in later modules, you'll add them to their own deliverables then, not here.

## Link to live loop

[Cortex agent](../00-build/agent.py), with operator instructions in [prompts.py](../00-build/prompts.py) and stop tracking in [loop_state.py](../00-build/loop_state.py).
