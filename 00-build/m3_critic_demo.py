"""M3 exercise: inject one false metric, then use the real critic/revision loop.

Run from 00-build: ../.venv/bin/python m3_critic_demo.py
Only the first draft is altered, after its real model response is logged.
The collected evidence, retrieval behavior, critic, and subsequent revisions
remain unchanged. The deliberately altered output is labelled in the trace.
"""

import json
from unittest.mock import patch

import agent


def main():
    original_complete = agent.complete
    original_emit = agent.emit_deliverable
    injected = False

    def complete_with_fault(client, *, role, **request):
        nonlocal injected
        response = original_complete(client, role=role, **request)
        message = response.choices[0].message
        if role == "drafter" and not injected and not message.tool_calls:
            output = json.loads(message.content)
            if output.get("status") == "draft":
                # Synthetic error is added AFTER logging the actual model response.
                # Do not change source evidence or imply the model authored this line.
                output["draft"] += "\n\nActivation rate is 99%."
                message.content = json.dumps(output)
                injected = True
                print("M3 CONTROLLED FAULT: appended 'Activation rate is 99%.' to the "
                      "first draft after the model response. Source evidence is unchanged.")
        return response

    def emit_demo(which, draft, **kwargs):
        return original_emit("m3-critic-demo", draft, **kwargs)

    with patch.object(agent, "complete", complete_with_fault), \
         patch.object(agent, "emit_deliverable", emit_demo):
        result = agent.run_to_file("happy")
    if not injected:
        print("No controlled fault was injected; this run does not demonstrate the M3 rejection.")
        return 1
    return result


if __name__ == "__main__":
    raise SystemExit(main())
