"""build-from-demo's fetches-source grader is a regex over the eval run's
trace (JSON lines), because a tool_used grader names one exact tool and this
one accepts get_artifact OR the deprecated get_demo_html. A regex over the
whole trace can pass on a tool NAME that appears without a call — in the
session's tool list, or inside another tool's answer (build_options suggests
get_artifact(...)). These traces pin that it doesn't.

⚠ The sample lines follow Claude Code's stream-json shape (a system init
line listing tool names as strings; assistant tool_use blocks with "name";
tool results as escaped text). The eval runner's exact trace format is not
documented (as of 2026-09-28); if it lists tools as {"name": …} objects,
the no-call case below would match and this grader must change."""
import json
import re
import unittest
from pathlib import Path

GRADER = (Path(__file__).resolve().parent.parent
          / "plugins/6to9/evals/build-from-demo/graders/fetches-source.md")
P = "mcp__plugin_6to9_6to9__"


def _pattern() -> re.Pattern:
    front = GRADER.read_text().split("---")[1]
    m = re.search(r"^pattern:\s*'(.*)'\s*$", front, re.M)
    assert m, "fetches-source.md has no single-quoted pattern"
    return re.compile(m.group(1).replace("''", "'"))


def _trace(*calls: str) -> str:
    init = {"type": "system", "subtype": "init",
            "tools": ["Read", "Skill", f"{P}get_build_spec", f"{P}get_artifact",
                      f"{P}get_demo_html", f"{P}list_artifacts"]}
    answer = ('{"build_options": ["1. \\"Working demo\\" (working demo, v2): '
              'get_artifact(spec_id=\\"aaaa\\", artifact_id=\\"cccc\\")"], '
              '"hint": {"name": "' + P + 'get_artifact"}}')
    lines = [init]
    for i, name in enumerate(("get_build_spec", *calls)):
        lines.append({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": f"t{i}", "name": f"{P}{name}", "input": {}}]}})
        lines.append({"type": "user", "message": {"content": [
            {"type": "tool_result", "tool_use_id": f"t{i}", "content": answer}]}})
    return "\n".join(json.dumps(x) for x in lines)


class FetchesSourceGraderTest(unittest.TestCase):
    def test_no_call_to_either_tool_does_not_match_the_tool_list_or_answers(self):
        # the tool list and a tool answer (with a {"name": …} inside its
        # text) both name get_artifact; neither is a call
        self.assertIsNone(_pattern().search(_trace()))

    def test_a_call_to_get_artifact_or_get_demo_html_matches(self):
        self.assertIsNotNone(_pattern().search(_trace("get_artifact")))
        self.assertIsNotNone(_pattern().search(_trace("get_demo_html")))
        self.assertIsNone(_pattern().search(_trace("list_artifacts")))


if __name__ == "__main__":
    unittest.main()
