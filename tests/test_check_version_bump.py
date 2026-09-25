"""Stdlib tests for scripts/check_version_bump.py, against a throwaway git repo.

Run: python -m unittest discover tests
"""
import importlib.util
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "check_version_bump", ROOT / "scripts" / "check_version_bump.py"
)
check_version_bump = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_version_bump)


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def _write(path: str, text: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _plugin_json(version: str) -> str:
    return json.dumps({"name": "6to9", "version": version}) + "\n"


def _commit(message: str) -> str:
    _git("add", "-A")
    _git("commit", "-q", "-m", message)
    return _git("rev-parse", "HEAD")


def _run_main(base: str) -> int:
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        return check_version_bump.main([base])


class CheckVersionBumpTest(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self._tmp = tempfile.TemporaryDirectory()
        os.chdir(self._tmp.name)
        _git("init", "-q", "-b", "main")
        _git("config", "user.email", "test@example.com")
        _git("config", "user.name", "test")
        _write("plugins/6to9/.claude-plugin/plugin.json", _plugin_json("0.1.0"))
        _write("plugins/6to9/skills/6to9/SKILL.md", "# skill\n")
        _write("plugins/6to9/evals/foo/prompt.md", "# eval\n")
        _write("README.md", "# repo\n")
        self.base = _commit("base")

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmp.cleanup()

    def test_no_plugin_change_passes(self):
        _write("README.md", "# repo, updated\n")
        _commit("touch readme only")
        self.assertEqual(_run_main(self.base), 0)

    def test_plugin_change_without_bump_fails(self):
        _write("plugins/6to9/skills/6to9/SKILL.md", "# skill, updated\n")
        _commit("change skill, no bump")
        self.assertEqual(_run_main(self.base), 1)

    def test_plugin_change_with_bump_passes(self):
        _write("plugins/6to9/skills/6to9/SKILL.md", "# skill, updated\n")
        _write("plugins/6to9/.claude-plugin/plugin.json", _plugin_json("0.2.0"))
        _commit("change skill, bump version")
        self.assertEqual(_run_main(self.base), 0)

    def test_version_decreased_fails(self):
        _write("plugins/6to9/skills/6to9/SKILL.md", "# skill, updated\n")
        _write("plugins/6to9/.claude-plugin/plugin.json", _plugin_json("0.0.9"))
        _commit("change skill, decrease version")
        self.assertEqual(_run_main(self.base), 1)

    def test_evals_only_change_passes(self):
        _write("plugins/6to9/evals/foo/prompt.md", "# eval, updated\n")
        _commit("change eval only, no bump")
        self.assertEqual(_run_main(self.base), 0)

    def test_missing_base_plugin_json_passes(self):
        # Simulate a base commit predating the plugin entirely: no plugins/
        # directory at all, so plugin.json doesn't exist at that ref.
        _git("checkout", "-q", "--orphan", "no-plugin")
        _git("rm", "-rq", "--cached", ".")
        shutil.rmtree("plugins", ignore_errors=True)
        _write("README.md", "# repo, pre-plugin\n")
        no_plugin_base = _commit("pre-plugin base")

        _git("checkout", "-q", "main")
        self.assertEqual(_run_main(no_plugin_base), 0)


if __name__ == "__main__":
    unittest.main()
