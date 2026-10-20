"""Independent validator (M3). A separate model call that never saw the drafting
context, so it can't inherit the draft's blind spots. Returns a pass/fail verdict.
The revision cap that stops a critic<->drafter loop lives in `agent.py`.
"""

from __future__ import annotations

import json

from prompts import CRITIC_SYSTEM
from model_trace import complete


def review(client, model: str, proposed_output: str, source_data: str,
           previous_output: str = "") -> dict:
    """Return {"verdict": "pass"|"fail", "reasons": [...]} for a proposed output."""
    resp = complete(client, role="critic",
        model=model,
        messages=[
            {"role": "system", "content": CRITIC_SYSTEM},
            {"role": "user", "content":
                'Calibration example. SOURCE DATA: project A has status on_track, '
                'flags [], and one open issue with severity normal. Norm: an open '
                'Sev-1 or launch_hold prohibits green and requires escalation. '
                'PROPOSED OUTPUT: Queued for review: A is green; its normal copy '
                'review issue remains open. Nothing posted.'},
            {"role": "assistant", "content":
                '{"verdict":"pass","reasons":[]}'},
            {"role": "user", "content":
                'Calibration example. SOURCE DATA: project B has status at_risk, '
                'flags [launch_hold], and an open issue with severity sev-1. Norm: '
                'an open Sev-1 or launch_hold prohibits green and requires '
                'escalation. PROPOSED OUTPUT: B is green and ready to launch.'},
            {"role": "assistant", "content":
                '{"verdict":"fail","reasons":["Claim B is green and ready to '
                'launch conflicts with its launch_hold and open sev-1; the norm '
                'requires escalation."]}'},
            {"role": "user", "content":
                'Calibration example. SOURCE DATA: project C has activation_rate '
                'value 41%, prior 39%. PROPOSED OUTPUT: Queued for review: '
                'C activation is 99%, up from 39%. Nothing posted.'},
            {"role": "assistant", "content":
                '{"verdict":"fail","reasons":["Claim activation is 99% '
                'conflicts with the source value 41%."]}'},
            {"role": "user", "content":
                f"SOURCE DATA Cortex used:\n{source_data}\n\n"
                f"CORTEX PROPOSED OUTPUT:\n{proposed_output}\n\n"
                f"PREVIOUS OUTPUT (if any):\n{previous_output}\n\n"
                "For a structured draft, verify exactly two distinct selected candidate IDs, "
                "other viable stories considered listed, grounded selection and omission "
                "reasons, and both selected stories included in the draft. Escalations need "
                "not meet draft requirements. For status escalate apply the ESCALATE rules, "
                "even though the output is JSON rather than text prefixed ESCALATE. "
                "Check stable candidate IDs against the previous output and reject unexplained "
                "candidate identity changes. If a previous output is supplied, also return "
                "wording_only: true or false. True means only language changed: no changes "
                "to facts, selection, substantive reasons, risk, or escalation decisions. "
                "If there is no previous output, return wording_only: false. "
                "Check ALL applicable rules, including every number against its "
                "source value; a safe status does not excuse invented metrics. "
                "Apply the severity rule literally: severity normal does not equal "
                "severity sev-1. An open normal issue alone cannot invalidate "
                "green for an on_track project with no launch_hold. Acknowledge "
                "normal issues without inventing a requirement to escalate them. "
                "Only concrete violations warrant fail; otherwise pass."},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    usage = resp.usage
    try:
        verdict = json.loads(resp.choices[0].message.content)
    except (json.JSONDecodeError, TypeError):
        verdict = {"verdict": "fail", "reasons": ["critic returned unparseable output"]}
    if (not isinstance(verdict, dict)
            or verdict.get("verdict") not in ("pass", "fail")
            or not isinstance(verdict.get("reasons"), list)
            or any(not isinstance(reason, str) for reason in verdict["reasons"])
            or (verdict["verdict"] == "fail" and not verdict["reasons"])):
        verdict = {"verdict": "fail", "reasons": ["critic returned an invalid verdict schema"]}
    verdict["_usage"] = {"prompt": usage.prompt_tokens, "completion": usage.completion_tokens}
    if type(verdict.get("wording_only")) is not bool:
        verdict = {"verdict": "fail", "reasons": ["critic omitted wording-only assessment"],
                   "wording_only": False, "_usage": verdict["_usage"]}
    return verdict
