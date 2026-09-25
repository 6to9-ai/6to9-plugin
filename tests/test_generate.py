"""Stdlib tests for scripts/generate.py. Run: python -m unittest discover tests"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("generate", ROOT / "scripts" / "generate.py")
generate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(generate)


class GenerateTest(unittest.TestCase):
    def setUp(self):
        meta, body = generate.parse(generate.SOURCE.read_text(encoding="utf-8"))
        self.meta, self.body = meta, body
        self.out = {p.relative_to(ROOT).as_posix(): t for p, t in generate.render(meta, body).items()}

    def test_committed_outputs_are_current(self):
        self.assertEqual(generate.main(["--check"]), 0, "run python scripts/generate.py")

    def test_skill_frontmatter_is_first(self):
        skill = self.out["plugins/6to9/skills/6to9/SKILL.md"]
        self.assertTrue(skill.startswith("---\nname: 6to9\ndescription: "))
        self.assertIn("landing page", skill.split("---")[1])

    def test_cursor_rule_is_apply_intelligently(self):
        rule = self.out["clients/cursor/6to9.mdc"]
        front = rule.split("---")[1]
        self.assertIn("alwaysApply: false", front)
        self.assertIn("description: ", front)
        self.assertNotIn("globs", front)

    def test_codex_block_is_delimited_and_nested(self):
        block = self.out["clients/codex/AGENTS.snippet.md"]
        self.assertTrue(block.startswith("<!-- 6to9:start -->"))
        self.assertTrue(block.rstrip().endswith("<!-- 6to9:end -->"))
        self.assertNotIn("\n# ", block)

    def test_server_instructions_are_the_core_only(self):
        text = self.out["generated/server_instructions.md"]
        self.assertTrue(text.startswith("<!-- GENERATED"))
        self.assertNotIn("## Guardrails", text)
        lead = text.split("-->", 1)[1].strip().split("\n\n")[0]
        self.assertLessEqual(len(lead), 512)
        self.assertIn("recommend_features", lead)

    def test_no_core_markers_leak(self):
        for name, text in self.out.items():
            if name != "generated/server_instructions.md":
                self.assertNotIn("<!-- core", text, name)
                self.assertNotIn("<!-- /core", text, name)

    def test_every_tool_is_named_in_the_guide(self):
        for tool in ("list_my_products", "recommend_features", "get_build_spec", "get_mvp_brief",
                     "get_competitors", "get_market_updates", "mark_event", "report_build_result"):
            self.assertIn(tool, self.body, tool)


if __name__ == "__main__":
    unittest.main()
