# Orchestration Map: Cortex PM Chief-of-Staff Agent

> Module 3 · Orchestration & Subagents, ★ Deliverable 3
>
> ✅ **What this validates:** nothing advances unchecked, by the end you'll have proven a justified topology, a roster, and a validator with a defined fail action.
>
> Builds on your M2 Loop Spec. Only split one agent into a team when there's a real reason, coordination has a cost.

## 1. Why split? (or why not)

Keep one primary Cortex agent and one independent validator. Construction and validation have a conflict of interest: the validator should be objective and should not draft the report. Additional collection agents are not needed for our current sources and data volume, and one LLM can hold the context in this limited case.

| Reason | Applies? | Why / why not |
|---|---|---|
| Separation of concerns | Yes | Construction and validation have a conflict of interest, so they should remain separate. |
| Parallelism | No | One agent can handle collection. Splitting might help with larger volumes or particular sources, but is not needed here. |
| Independent validator | Yes | The validator should be objective and should not draft the report. |
| Context-window pressure | No | In this limited case, one LLM can hold the context. |

## 2. Topology

**Pattern:** single + subagents — one Cortex agent and one independent critic.

```
[Weekly scheduled task]
        ↓
[Cortex: collect data, select stories, draft report]
        ↓
[Independent critic]
   ├─ Pass → [PM review checkpoint: queued for approval]
   └─ Fail → [Cortex revises using existing evidence]
                 ↓
             [Critic reviews again]
                 ↓
          Still fails after 3 revisions → [PM escalation]
```

## 3. Roster

| Agent / subagent | Responsibility | Runs which Loop Spec |
|---|---|---|
| Chief-of-staff (Cortex) | Collect project context, select two stories, explain selections and omissions, draft the leadership report, and revise from critic feedback. Enforce the revision cap and escalation. | M2 reporting loop: [loop-spec.md](../02-loop-design/loop-spec.md). |
| Critic / Validator | Independently check facts, story-selection output, and risk reporting; return a pass or failed checks with reasons. | Review each submitted output against the checks in §5. |

## 4. Communication & hand-offs

- **Cortex → critic:** The task brief, source evidence used, draft report, selected stories and other viable stories considered, with selection and omission reasons.
- **Critic → Cortex:** Pass or fail, with the failed checks and actionable reasons when revisions are needed.
- **After a pass:** Advance the output to the PM review checkpoint, queued for approval.
- **After 3 unsuccessful revisions:** Hand the latest output and unresolved issues to the PM.

Use direct calls within the existing program. MCP and A2A are optional and are not needed for this hand-off.

## 5. The validator

- **What the critic checks:**
  1. Correct project and facts: project names, ticket IDs, numbers, and progress claims match the source evidence.
  2. Story-selection output: exactly two stories are selected, with reasons, and other viable stories considered are listed with reasons for leaving them out.
  3. Honest risk reporting: known blockers and serious incidents are acknowledged, and the reported status matches the evidence.
- **Fail action:** Return the output to Cortex with the failed checks and reasons. Cortex revises using the evidence already collected.
- **Revision cap:** Up to 3 revisions after the initial draft. If the output still fails, stop and escalate to the PM.
- **Pass action:** Advance to the PM review checkpoint, queued for approval. Nothing is sent or published.

These checks define the critic's focus; Cortex's existing safety rules remain in place.

## 6. State: shared vs isolated

Both Cortex and the critic see the task, source evidence, current output, and review rules. The critic also sees the previous output when needed to compare revisions.

Keep their conversations separate: the critic receives evidence and outputs without inheriting Cortex's drafting conversation. Cortex receives the critic's verdict and actionable reasons.

## 7. Cost & latency budget

The validator adds one critic call when the initial draft passes. With up to 3 revisions, the review cycle can require 4 critic calls and 3 additional drafter calls.

The provisional budget for the complete reporting run is **$0.02 and 60 seconds**, including collection, drafting, critic calls, and revisions. The Module 3 exercise took 30.20 seconds and approximately $0.0094; this is an observed result, not a guaranteed maximum.

These limits will be enforced in Module 5: [bounds-and-evals.md](../05-bounds-evals/bounds-and-evals.md).
