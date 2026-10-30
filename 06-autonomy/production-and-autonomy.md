# Production & Autonomy: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 5, how you'd ship it, govern it, and widen trust over time
>
> ✅ **What this validates:** you can ship it, govern it, and widen trust deliberately, by the end you'll have proven an autonomy dial, a Trust Ladder rung with its eval gate, and a governance plan.

## Autonomy Dial by segment

_Autonomy is a product decision per user, not one global setting._

| Segment | Desired autonomy | Why |
|---|---|---|
| Product manager | Supervised delivery, with autonomous preparation. Cortex collects, selects, drafts, and revises independently within bounds, then pauses before sending or posting. | Automate as much as possible, up to the point of delivery. The PM approves each send; existing controls over actual work, ticket changes, and commitments remain. |
| Engineering | Cortex independently prepares the proposed backlog, with roadmap information as context, then stops. Engineering reviews and accepts items into the active backlog. | Engineering owns acceptance of actual work. No change to that boundary has been proposed. Cortex reads the roadmap; it does not create or update it. |
| Leadership | Current intended state: status reports require PM approval before delivery. Future target: bounded-autonomous routine delivery after trust is earned and delivery rules and an eval gate are established. | Direct leadership use is the ideal future state once Cortex is trusted, its checks work, and it runs smoothly. It is not permission to deliver automatically today. |

The reference card's Cortex example classifies preparation followed by approval of each send as supervised, even though the internal preparation steps do not require individual approval. Bounded-autonomous delivery means routine updates can be sent within defined bounds, with human sample and exception review. These are intended operating states, not a claim that the current prototype has earned either rung. Future automatic delivery would require an explicit revision of the current approval-before-send boundary and implemented delivery controls.

## Trust Ladder

- **Current rung:** Supervised is the PM's chosen operating model: nothing is sent without the PM's approval. That control gives the PM the opportunity to improve Cortex and establish whether it has earned a higher rung over time. The current prototype has no sending tool; approved delivery remains to be implemented.
- **Eval gate to reach the next rung:** At least 98% completion on the agreed reporting eval cases and zero trust incidents over four consecutive weeks. Use the Module 5 suite to assess reporting and safety behavior. The PM reviews the evidence and explicitly approves any increase in autonomy; meeting the thresholds does not trigger promotion automatically. A future assessment needs enough comparable cases to support the completion percentage: four weekly reports alone cannot demonstrate a 98% rate. No such observation window or measured rate has been established. Automatic routine delivery also requires approval of the changed delivery boundary and implemented delivery controls.
- **Incident record so far:** Prototype test history, not a clean production window. The October 29 grounded run proposed already merged work and the critic passed it. Critic responses have omitted the required `wording_only` field, causing runtime holds, including the October 30 jailbreak proof. The October 30 cap probe repeated a successful activity lookup without explanation before the collection cap stopped it. The recorded probes performed no unauthorized publication or ticket changes; those tools are absent. Captures and limitations are preserved in [prototype.md](prototype.md). No production incident rate or four-week clean operating record has been established.

## Deployment plan

- **Runtime:** Serverless functions triggered by a weekly schedule before the leadership meeting. The schedule is separate from the hosting model: Cortex does not need to run continuously between reports. Retain reports and history in storage between executions. Prefer low cost and pay-per-run execution; no provider or pricing comparison has been selected, so this is not a claim that a particular service is cheapest. This is the deployment plan, not an existing deployment.
- **Operator / on-call owner:** Bob is the primary responsible operator. The engineer receives failed-run alerts and takes responsibility when Bob is unavailable. Engineers and others with visibility should be able to stop Cortex, consistent with the Module 5 policy. Name the specific backup engineer before deployment; no individual has been selected yet.
- **Rollback:** Revert model or tool changes to the previous version when their impact is significant enough to warrant rollback. For prompt changes, either revert or adjust the prompt depending on the resulting output. These are recovery policies, not a claim that automated rollback exists.
- **Monitoring:** Monitor test pass rates, escalation frequency, cost per completed report, and trust incidents. Bob and the backup engineer use these signals to assess health without reading every trace. Production monitoring and alert delivery are planned, not implemented.

## ROI metrics (beyond adoption & tokens)

| Metric | Target |
|---|---|
| Task completion rate | 98% target for routine reporting tasks meeting the Module 5 completion criteria. Record PM corrections separately from required approval. This is not a measured success rate. |
| Time saved / cost-to-serve | Projected 2.7 hours saved per successful weekly report at approximately $34 cost-to-serve per completed report, based on the assumptions below. |
| Trust incidents | Zero target. Log count and severity over the review period; retain known prototype content and critic failures rather than treating the test history as clean. |

**Projected ROI and operating targets:** Cortex targets 98% completion of routine reporting tasks, saving approximately 2.7 hours per week at an estimated $34 cost-to-serve per completed report, with zero trust incidents as the target.

**Derivation and assumptions:**

| Input | Planning assumption per weekly report |
|---|---|
| Manual collection | 60 minutes |
| Manual story review and selection | 60 minutes |
| Manual report preparation | 60 minutes |
| Total manual effort | 180 minutes |
| PM review and correction with Cortex | 20 minutes |
| Projected time saved per successful report | 160 minutes, approximately 2.7 hours |
| Illustrative loaded PM labor rate | $100/hour |
| Human review cost | Approximately $33.33 |
| Provisional model, hosting, and tool-cost allowance | $1 |
| Estimated cost-to-serve | Approximately $34 per completed report |

The three-hour manual baseline reflects the PM's estimate for a report requiring substantial collection and candidate review. Review time, labor rate, and the operating allowance are assumptions to validate during supervised operation, not measured results. Measure manual and Cortex-assisted human effort for comparable tasks; record total service costs, including failed attempts and retries, against successfully completed reports. The $1 costing allowance is separate from the $0.02 model-spend limit. At the illustrative labor rate, manual effort represents $300 per report versus approximately $34 with Cortex, releasing approximately $266 in potential labor capacity per successfully completed report, not necessarily cash savings. Initial development, ongoing maintenance, and additional failed-run costs have not yet been estimated. The projection is conditional on successful completion; no adjustment for the 98% target has been applied to the weekly time-saving figure.

## Widen-autonomy decision rule

Consider automatic routine leadership delivery only after Cortex achieves at least 98% completion on the agreed reporting eval cases and zero trust incidents over four consecutive weeks. The PM reviews the evidence and explicitly approves any increase in autonomy; meeting the thresholds does not trigger promotion automatically. This is a future gate, not a claim that the current prototype has met it.

## Governance & forward strategy

- **Compliance:** Exclude or redact credentials, customer identifiers, and other sensitive fields before sending real company data to the model. Preserve the source confidentiality flags and audience restrictions throughout processing and output review. The current build uses mock fixtures; an input-redaction control for future real connectors has not been implemented or tested.
- **Safety:** Preserve the existing agent line: human approval before delivery, human acceptance of actual backlog work, and human control of ticket changes, merges, launch gates, and delivery-date commitments. Bob is the primary responsible operator; engineers and others with visibility should also be able to stop Cortex. Future approved delivery must be single-use, limited to the exact approved content and destination, with fresh approval for any change. Shared stop access and delivery authorization remain planned controls.
- **Reliability:** Enforce the agreed collection, revision, time, and estimated per-run cost limits; stop and escalate unresolved work. The combined daily budget remains planned as documented in Module 5. If the model service is unavailable when the weekly report is due, stop and notify Bob, with the engineer as backup, so a person can prepare the report manually. Notification delivery and production scheduling remain to be implemented.
- **Strategy:** The next desired capability is automatic routine leadership status-report delivery after Cortex earns trust. Until then, PM approval remains required. Engineering continues to review proposed stories before accepting them into the active backlog. Apply the Trust Ladder gate and obtain explicit approval of any changed delivery boundary before widening; current run evidence does not establish readiness for unattended delivery.
