# Agent Line Map: Cortex PM Chief-of-Staff Agent

> Module 1 · The Agent Line
>
> ✅ **What this validates:** every risky action has a clear owner, by the end you'll have proven an above/below-the-line map with HITL checkpoints, scored on reversibility, blast radius, and measurability.

## The workflow, decision by decision

List every discrete decision or action in your agent's workflow, then score each one and place it **above** the line (a human owns it) or **below** (the agent owns it). Borderline calls get an HITL checkpoint.

Scores and reasoning below are my Step 2 decisions, with final placements confirmed in Step 3.

| Decision / action | Reversibility (H/M/L) | Blast radius (H/M/L) | Measurability (H/M/L) | Above / Below | HITL? | My reasoning |
|---|---|---|---|---|---|---|
| Pull project state + recent engineering activity | H | L | H | Below | No separate approval for retrieval | We do not need to act, share, or publish the tickets. We can see the tickets that are the sources for information and validate. There is little risk of any damage. |
| Decide which context is relevant | H | L | M | Below | No separate approval for selection | It is sorting through context, and context is subjective. Not shared or published, easily reversed or improved. |
| Draft the update | H | L | H | Below | No approval to create the draft; publication requires approval | Not shared or published, easily reversed or improved. |
| Decide tone and commitment level | H | L | H | Below | No separate approval for draft wording | Not shared or published, easily reversed or improved. |
| Flag risks or a need for escalation | H | L | H | Below | No approval to flag an issue | Not shared or published, easily reversed or improved. |
| Choose what to escalate | H | L | M | Below | No separate approval for escalation selection | Not shared or published, easily reversed or improved; medium is due to subjectivity. |
| Propose a capped story batch | H | L | H | Below | No approval to prepare or queue proposals; human approval for actual work | Not shared or published, easily reversed. |
| Post an update or approve a company-wide update | M | M | M | Above | Required before publication; human owns release | You can take the post down, but you cannot reverse what anyone already saw. Blast radius can be medium or high, depending on company size. Since this is just the company, we can measure fairly well, but are still estimating. |

### Step 3 exceptions and approval boundaries

I kept context selection and escalation selection below the line despite Medium measurability. These are deliberate exceptions to the lab's default HITL treatment of borderline scores: the results are not shared or published and can be easily reversed or improved.

Cortex may prepare and queue capped story proposals, but I approve the actual work. A human owns the release decision; nothing is published without human approval.

## Agent anatomy (sketch)

- **Model:** `gpt-4o-mini` for drafting and `gpt-4.1-mini` for the independent critic. Keep both at the Mini level for now. No automatic frontier-model escalation: stop and bring unresolved cases to me.
- **Tools:** Read project state and engineering activity; search past updates and decisions; read the roadmap and team norms; propose a capped story batch for human approval. No tools to publish updates, create or modify tickets, merge PRs, or commit delivery dates. This tool set fits my agent line.
- **Memory:** Use the current build's default for now: source files and saved drafts persist between runs. Conversation context starts fresh each run; Cortex does not automatically update its persistent knowledge. Detailed memory design remains for Module 4.
- **Loop:** _placeholder, defined in M2 loop-spec.md_
- **Bounds:** _placeholder, defined in M5 bounds-and-evals.md_
- **Evals:** _placeholder, defined in M5 bounds-and-evals.md_

## The golden rule, applied

1. Pulling project state and recent activity sits below the line because a wrong retrieval is easy to recover from, has little potential for damage, and can be checked against the source tickets; the deciding factor is high measurability.
2. Context selection sits below the line because its results are easy to revise and remain internal, limiting the blast radius; although relevance is subjective and measurability is medium, the deciding factor is low blast radius.
3. Drafting the update sits below the line because the draft can be reversed or improved, remains unpublished, and can be reviewed before release; the deciding factor is low blast radius.
4. Choosing the draft's tone and commitment wording sits below the line because the wording can be revised, remains unpublished, and can be checked against the standards I teach the agent; the deciding factor is high reversibility.
5. Flagging risks sits below the line because the flags can be revised, remain internal, and can be checked against defined criteria; the deciding factor is high measurability.
6. Choosing what to escalate sits below the line because the selection can be revised and remains internal; although the choice is subjective and measurability is medium, the deciding factor is low blast radius.
7. Proposing a capped story batch sits below the line because the proposals are easily reversed, remain queued for approval, and can be reviewed before any work is authorized; the deciding factor is low blast radius.
8. Publication sits above the line because removing a post cannot undo what people have already seen, its blast radius grows with company size, and its impact can only be estimated; the deciding factor is limited reversibility.

## Hardest call

My hardest call was deciding tone because it can be subjective, even for LLMs. Reversibility settled it for me: the draft can be revised before publication, and I can iterate on the agent to bring its tone into line with a standard. I therefore kept tone selection below the line.
