"""Offline contract checks for the learner's M2 loop; no API calls or file writes."""

import io
import json
import sys
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import agent
import critic as critic_module
from loop_state import RunStopped, SelectionHistory, deadline, parse_output


def output(selected=("A", "B"), **changes):
    result = {"status": "draft", "reason": "", "needs_new_data": False,
              "candidates": [{"id": key, "title": f"Story {key}", "evidence": "PRD in scope",
                              "reason": f"Reason for {key}"} for key in "ABCD"],
              "selected": list(selected), "comparisons": [], "change_reason": "",
              "draft": "Queued for review: Story A and Story B."}
    result.update(changes)
    return result


def message(content=None, calls=None):
    return NS(content=content, tool_calls=calls)


def tool_call(name):
    return NS(id=name, function=NS(name=name, arguments=json.dumps(
        {"project_id": "P-NORTH"} if name in ("get_project", "get_activity") else {})))


class LoopTests(unittest.TestCase):
    def exercise(self, outputs, verdicts=None, missing=False, project_only=False, **overrides):
        responses = [message(calls=[tool_call("get_project")])]
        if not missing and not project_only:
            responses += [message(calls=[tool_call(n) for n in
                           ("get_activity", "search_past_updates", "get_roadmap", "get_norms")])]
        responses += [message(json.dumps(o)) for o in outputs]
        complete = Mock(side_effect=[NS(choices=[NS(message=m)],
                                        usage=NS(prompt_tokens=1, completion_tokens=1))
                                     for m in responses])
        if verdicts is None:
            verdicts = [("pass", False)] * len(outputs)
        critic = Mock(side_effect=[{"verdict": v, "wording_only": w,
                                   "reasons": [] if v == "pass" else ["Fix grounded content"],
                                   "_usage": {"prompt": 1, "completion": 1}}
                                  for v, w in verdicts])
        read_results = {
            "get_project": {"error": "project_not_found"} if missing else
                           {"project_id": "P-NORTH", "flags": []},
            "get_activity": {"activity": []}, "search_past_updates": {"matches": []},
            "get_roadmap": {"roadmap": "In-scope PRD"}, "get_norms": {"norms": "Draft only"},
        }
        readers = {name: Mock(return_value=value) for name, value in read_results.items()}
        emit = Mock()
        propose = Mock(return_value={"status": "queued_for_approval"})
        with patch.object(agent, "OpenAI"), patch.object(agent, "complete", complete), \
             patch.object(agent, "review", critic), patch.object(agent, "emit_deliverable", emit), \
             patch.dict(agent.tools.TOOLS, readers), \
             patch.object(agent.tools, "propose_stories", propose), \
             patch.multiple(agent, **({"MAX_RUN_SECONDS": 300} | overrides)), redirect_stdout(io.StringIO()):
            agent.run()
        return emit.call_args, complete, critic, readers, propose

    def test_initial_success(self):
        emitted, calls, critic, readers, propose = self.exercise([output()])
        self.assertTrue(emitted.kwargs["accepted"])
        self.assertEqual(propose.call_args.kwargs["project_id"], "P-NORTH")
        self.assertEqual(propose.call_args.kwargs["stories"], ["Story A", "Story B"])
        self.assertIn("Other viable stories", emitted.args[1])

    def test_no_forced_source_checklist_or_ready_stage(self):
        emitted, calls, _, readers, _ = self.exercise([output()], project_only=True)
        self.assertTrue(emitted.kwargs["accepted"])
        self.assertEqual(calls.call_count, 2)  # project lookup, then initial output
        readers["get_activity"].assert_not_called()
        self.assertEqual({s["function"]["name"] for s in calls.call_args_list[0].kwargs["tools"]},
                         {"get_project", "get_activity", "search_past_updates", "get_roadmap", "get_norms"})

    def test_full_source_results_reach_initial_output(self):
        _, calls, _, _, _ = self.exercise([output()])
        tool_messages = [m for m in calls.call_args_list[2].kwargs["messages"]
                         if isinstance(m, dict) and m.get("role") == "tool"]
        self.assertEqual(len(tool_messages), 5)
        self.assertIn('{"roadmap": "In-scope PRD"}', [m["content"] for m in tool_messages])

    def test_three_revisions_after_initial_no_new_retrieval(self):
        emitted, calls, critic, readers, _ = self.exercise(
            [output()] * 4, [("fail", False)] * 3 + [("pass", False)])
        self.assertTrue(emitted.kwargs["accepted"])
        self.assertEqual(critic.call_count, 4)
        for reader in readers.values():
            self.assertEqual(reader.call_count, 1)
        for call in calls.call_args_list[3:]:
            self.assertNotIn("tools", call.kwargs)
        evidence = [c.args[3] for c in critic.call_args_list]
        self.assertTrue(all(e == evidence[0] for e in evidence))

    def test_revision_exhaustion(self):
        emitted, calls, critic, _, propose = self.exercise([output()] * 4, [("fail", False)] * 4)
        self.assertFalse(emitted.kwargs["accepted"])
        self.assertIn("3 revisions exhausted", emitted.kwargs["reason"])
        self.assertEqual(critic.call_count, 4)
        propose.assert_not_called()

    def test_two_wording_only_revisions(self):
        emitted, _, critic, _, _ = self.exercise([output()] * 3,
            [("fail", False), ("fail", True), ("pass", True)])
        self.assertIn("2 consecutive wording-only", emitted.kwargs["reason"])
        self.assertFalse(emitted.kwargs["accepted"])

    def test_third_selection_change(self):
        values = [output(), output(("A", "C"), change_reason="C is more relevant"),
                  output(("B", "C"), change_reason="B addresses risk"),
                  output(("C", "D"), change_reason="D is now preferred")]
        emitted, _, critic, _, _ = self.exercise(values, [("fail", False)] * 4)
        self.assertIn("third selection change", emitted.kwargs["reason"])
        self.assertIn("Initial selection", emitted.args[1])
        self.assertIn("D is now preferred", emitted.args[1])
        self.assertEqual(critic.call_count, 3)

    def test_two_unresolved_comparisons(self):
        one = {"options": ["A", "B"], "result": "Equal value; unresolved"}
        two = {"options": ["A", "B"], "result": "Equal urgency; unresolved"}
        values = [output(status="compare", reason="Tie", comparisons=[one]),
                  output(status="compare", reason="Still tied", comparisons=[one, two])]
        emitted, _, critic, _, _ = self.exercise(values)
        self.assertIn("unresolved after 2 comparisons", emitted.kwargs["reason"])
        critic.assert_not_called()

    def test_feedback_needing_new_data_stops(self):
        emitted, _, critic, readers, _ = self.exercise(
            [output(), output(needs_new_data=True, reason="Need fresh usage")], [("fail", False)])
        self.assertIn("new evidence required", emitted.kwargs["reason"])
        self.assertEqual(critic.call_count, 1)
        self.assertTrue(all(r.call_count == 1 for r in readers.values()))

    def test_missing_data_stops(self):
        emitted, _, critic, _, propose = self.exercise([], missing=True)
        self.assertIn("required data unavailable", emitted.kwargs["reason"])
        critic.assert_not_called()
        propose.assert_not_called()

    def test_time_limit_interrupts_inflight_work(self):
        with self.assertRaisesRegex(RunStopped, "time limit"):
            with deadline(0.02):
                time.sleep(0.1)

    def test_cost_stop(self):
        emitted, _, critic, _, _ = self.exercise([], COST_CAP_USD=0)
        self.assertIn("cost cap", emitted.kwargs["reason"])
        critic.assert_not_called()

    def test_invalid_selected_ids_rejected(self):
        with self.assertRaisesRegex(ValueError, "selected"):
            parse_output(json.dumps(output(("A", "missing"))))

    def test_explained_escalation_is_held_not_accepted(self):
        emitted, _, _, _, propose = self.exercise([
            output(status="escalate", reason="Unconfirmed date requires human decision")])
        self.assertFalse(emitted.kwargs["accepted"])
        self.assertIn("Unconfirmed date", emitted.kwargs["reason"])
        propose.assert_not_called()

    def test_critic_must_supply_wording_assessment(self):
        response = NS(choices=[NS(message=message('{"verdict":"pass","reasons":[]}'))],
                      usage=NS(prompt_tokens=1, completion_tokens=1))
        with patch.object(critic_module, "complete", return_value=response):
            result = critic_module.review(Mock(), "model", "draft", "evidence", "previous")
        self.assertEqual(result["verdict"], "fail")
        self.assertIn("wording-only", result["reasons"][0])

    def test_critic_wording_assessment_preserved(self):
        response = NS(choices=[NS(message=message(
            '{"verdict":"fail","reasons":["Unsupported claim"],"wording_only":true}'))],
            usage=NS(prompt_tokens=1, completion_tokens=1))
        with patch.object(critic_module, "complete", return_value=response) as call:
            result = critic_module.review(Mock(), "model", "draft", "evidence", "previous")
        self.assertTrue(result["wording_only"])
        self.assertIn("previous", call.call_args.kwargs["messages"][-1]["content"])


if __name__ == "__main__":
    unittest.main()
