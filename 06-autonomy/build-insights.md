# Build Insights: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 4, what you learned building it
>
> ✅ **What this validates:** you can reflect on what building it taught you, by the end you'll have proven the friction, the learning, and the aha that changes how you'd design your next agent.

## Friction

The biggest friction was understanding and validating the critic. We spent substantial time distinguishing formatting failures from substantive rejections and examining cases where a pass still allowed incorrect story selection. This showed me that a validator's approval is only as useful as its evidence, checks, and response handling. Another challenge was reconciling broad course definitions with the Cortex examples so that our design decisions matched the intended workflow.

## Learning

Managing an agent requires controls at multiple points in the workflow and across the system. Different stages need different checks and limits; one evaluation at the end is not enough.

## Aha moment

I had already considered token usage, but I had not deliberately measured run time in my previous work. Considering elapsed time alongside tokens gave me another way to assess efficiency and set limits.

## What you'd do differently

Rather than trying to build the whole agent end to end in one shot, I would build it step by step, with appropriate measurements and checks along the way.
