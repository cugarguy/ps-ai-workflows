# Cortex — Weekly PM Reporting and Backlog Preparation

> Cortex collects project evidence, selects opportunities, drafts a weekly leadership update and proposed backlog, and uses an independent critic before handing the package to the PM for approval.

_Bob Steeger · Advanced AI Agents · October 2026_

Repo: https://github.com/cugarguy/ps-ai-workflows

This repo is my final project for the Agentic Loops for PMs Certification, **Cortex — Weekly PM Reporting and Backlog Preparation**. Each module’s artifact lives in its own folder; this README is the dashboard and the pitch.

---

## Module artifacts

### M1 · The Agent Line
- **Agent-line map**: [`01-agent-line/agent-line-map.md`](01-agent-line/agent-line-map.md)

### M2 · Loop Engineering
- **Loop spec**: [`02-loop-design/loop-spec.md`](02-loop-design/loop-spec.md)

### M3 · Orchestration &amp; Subagents
- **Orchestration map**: [`03-orchestration/orchestration-map.md`](03-orchestration/orchestration-map.md)

### M4 · Choose What Each Agent Step Is Allowed to See
- **Memory &amp; context plan**: [`04-memory-context/memory-and-context.md`](04-memory-context/memory-and-context.md)

### M5 · Bounds &amp; Evals
- **Bounds &amp; evals**: [`05-bounds-evals/bounds-and-evals.md`](05-bounds-evals/bounds-and-evals.md)

### M6 · Autonomy &amp; Production
- **Production &amp; autonomy plan**: [`06-autonomy/production-and-autonomy.md`](06-autonomy/production-and-autonomy.md)
- **Prototype write-up**: [`06-autonomy/prototype.md`](06-autonomy/prototype.md)

---

## Ship plan

### Autonomy dial (per segment)
Product manager: Supervised delivery with autonomous preparation. Cortex collects, selects, drafts, and revises within bounds; the PM approves each send or post.
Engineering: Cortex prepares proposed backlog items with roadmap context, then stops. Engineering reviews and accepts actual work into the active backlog.
Leadership: Reports require PM approval today. Future target: bounded-autonomous routine delivery after trust is earned, the delivery boundary is explicitly changed, and delivery controls are implemented.
Current prototype: mock source fixtures, no sending or ticket-changing tools, and no production deployment.

### Trust Ladder rung + eval gate
Current rung: Supervised, following the reference card’s Cortex example: independent preparation followed by human approval of delivery.
Gate to consider bounded-autonomous routine delivery: at least 98% completion on agreed reporting eval cases and zero trust incidents over four consecutive weeks, with enough comparable cases to support that rate. The PM must explicitly approve promotion and the changed delivery boundary.
This gate has not been met. Prototype evidence includes incorrect story selection passing the critic, malformed critic responses held by the runtime, and repeated collection. No clean production window has been established.

### Deployment plan
Runtime plan: serverless functions on a weekly schedule before the leadership meeting, with persistent reports and history stored between runs. Pay per run is preferred; no provider has been selected or deployment completed.
Owner / on-call: Bob is primary. A backup engineer must be named before deployment; engineers and others with visibility should be able to stop Cortex.
Rollback: revert significant model or tool regressions to the prior version. Revert or adjust prompt changes based on their output. These are planned recovery policies.
Monitoring plan: eval pass rates, escalation frequency, cost per completed report, and trust incidents. Production monitoring and alert delivery are not implemented.

### ROI metrics + widen-autonomy rule
Projected ROI and operating targets: Cortex targets 98% completion of routine reporting tasks, saving approximately 2.7 hours per week at an estimated $34 cost-to-serve per completed report, with zero trust incidents as the target. These are projections and targets, not measured results.
Derivation per successful weekly report: manual collection 60 minutes + story review/selection 60 minutes + report preparation 60 minutes = 180 minutes. Assumed PM review/correction with Cortex: 20 minutes. Projected saving: 160 minutes, approximately 2.7 hours.
At an illustrative $100/hour loaded PM rate, review costs $33.33; add a provisional $1 model/hosting/tool allowance for approximately $34 per completed report, versus $300 manual labor. Approximately $266 is potential released labor capacity, not necessarily cash savings. The $1 allowance is separate from the $0.02 model-spend threshold. Development, maintenance, and additional failed-run costs remain unestimated; weekly savings have not been adjusted for the 98% target.
Measurement plan: compare manual and assisted human effort on comparable tasks; include retries and failed attempts in total cost per successful report. Widen autonomy only after the 98% completion / zero trust incident gate over four consecutive weeks, sufficient comparable cases, implemented delivery controls, and explicit PM approval.

### Governance &amp; strategy
Compliance plan: redact credentials, customer identifiers, and other sensitive fields before real company data enters the model. Preserve confidentiality flags and audience restrictions. Current sources are mock fixtures; real-connector redaction is unimplemented.
Safety: human approval before delivery; engineering accepts actual backlog work; ticket changes, merges, launch gates, and date commitments remain human-controlled. Future delivery authorization must be single-use for exact approved content and destination. Shared stop access and delivery controls are planned.
Runtime bounds: 5 collection turns, 3 critic-driven revisions using frozen evidence, 60 seconds, $0.02 estimated model spend per run, and a 10-proposal queue cap. Cost is checked after responses and can overrun the threshold. The $0.20 daily cap and three-attempt source retry policy remain planned.
Reliability plan: stop and escalate unresolved work. On model outage, notify Bob and the backup engineer for manual reporting; notification and production scheduling remain unimplemented.
Strategy: earn trust in supervised operation, then consider routine automatic leadership delivery with explicit approval. Current evidence does not establish readiness for unattended delivery.

---

## Build insights

- **Friction point.** Understanding and validating the critic took the most work: distinguishing formatting failures from substantive rejections, and examining passes that still allowed incorrect story selection. A validator’s approval depends on its evidence, checks, and response handling. Reconciling broad course definitions with the Cortex examples was another challenge.
- **Key learning.** Managing an agent requires controls at multiple points in the workflow and across the system. Different stages need different checks and limits; one evaluation at the end is not enough. Next time, I would build step by step, with appropriate measurements and checks along the way.
- **Aha moment.** I had already considered token usage, but had not deliberately measured run time in previous work. Considering elapsed time alongside tokens gave me another way to assess efficiency and set limits.

---

_Certification submission, Agentic Loops for PMs Certification._
