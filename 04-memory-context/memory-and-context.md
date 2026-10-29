# Context Engineering & Memory: Cortex PM Chief-of-Staff Agent

> Module 4 · Context Engineering & Memory
>
> ✅ **What this validates:** the agent reasons on the right, safe inputs, by the end you'll have proven a context budget, per-source retrieve-vs-long-context decisions, and a memory map with risk mitigations.
>
> 🗂️ **How the lab maps to this file:** In **Part A** (before the lecture) you don't edit this file, you rough-draft on scratch, focused on the per-source calls in **section 2** plus a quick remember/forget + "how it rots" sketch. In **Part B** (after the lecture) you complete **all five sections**; the Lab Guide's guided builder writes this file for you to copy in and commit.

## 1. Context budget

Each loop iteration receives the full task brief and roadmap, relevant team rules, recent activity, and recent or still-applicable historical records, as defined below.

Mandatory rules always remain in context, including confidentiality restrictions and required human checkpoints. If the inputs become too large, trim them in this order:

1. Roadmap.
2. Other team guidance; preserve mandatory rules.
3. Past updates and decisions.
4. Task brief.
5. Recent activity, preserved longest.

## 2. Retrieve vs. long-context: per source

For each data source, decide: **retrieve** (narrow a large/changing corpus to the relevant slice) or **long-context** (just include a bounded set you can reason over).

| Source | Size / volatility | Decision | Why |
|---|---|---|---|
| Roadmap (`get_roadmap`) | Small enough to include in full | Long-context | The full roadmap is small enough, and stories or updates may affect other areas. |
| GitHub/Jira activity (`get_activity`) | Plentiful; updates regularly | Retrieve new or updated items since the previous pull | Recency: use the changes since the previous pull rather than the full activity history. |
| Past updates and decisions (`search_past_updates`) | History grows over time; some older items still apply | Retrieve recent records plus older items flagged as still applicable | Recency and relevance: keep the full history available, but exclude outdated items from the current context. |
| This week's task brief (`get_task`) | Small enough to include in full | Long-context | The brief is small enough, and updates may affect other areas. |
| Team norms / playbook (`get_norms`) | Fairly large; contains material beyond this task | Retrieve relevant sections | Size and relevance: unrelated guidance would create noise. Mandatory rules remain in context. |

## 3. Retrieval quality plan

| Retrieved source | Routing | Document grading | Reranking | Self-verification | Caching |
|---|---|---|---|---|---|
| Recent activity | Use the correct sources. | Not selected. | Not selected. | Not selected. | Retain what was previously pulled to identify new or updated items on the next pull. |
| Past updates and decisions | Use the correct source. | Not selected. | Prioritize the changes that matter. | Not selected. | Track what was used previously. |
| Team norms / playbook | Check the authoritative playbook for updates so cached rules stay current. | Not selected. | Not selected. | Not selected. | Preserve mandatory rules. |

## 4. Memory map (your PM brain)

| Memory type | What Cortex stores | Scope / TTL |
|---|---|---|
| **Working** (in-loop) | Collected evidence, candidate stories, current draft, and critic feedback. | Current run only. Each run starts with clean context and collects relevant context from persistent memory mechanisms. |
| **Episodic** (past runs) | Per-project and overall reporting history: stories considered, selected, omitted, and escalated, including selection and change reasons. | One year, approximately 52 weekly reporting runs. |
| **Semantic** (durable facts/prefs) | Standing facts and rules, including team norms, roadmap facts, and decisions that still apply. | Retain until replaced or explicitly marked outdated. |
| **Shared** (across agents) | Task, source evidence, current and previous drafts, review rules, and feedback exchanged between Cortex and the independent critic. | Current reporting run only. Keep agent conversations separate; the critic can see the previous draft to compare revisions, consistent with Module 3. |

## 5. Memory risks & mitigations

| Risk | Mitigation |
|---|---|
| Drift | Refresh stored facts from authoritative sources on every run. |
| Poisoning | Validate information against an authoritative source and retain its citation before saving it to persistent memory. |
| Staleness | Exclude anything marked outdated or superseded from the current context. Monthly, ask the PM to review items that appear old and unused or conflict with newer signals. |
| Confidential / retention | Preserve the source's access scope and confidentiality flags in saved memory. Keep working and shared context for the current run only, episodic history for one year, and semantic memory until replaced or explicitly marked outdated. |
