# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib, subprocess and tempfile build a disposable Git repository; sys locates the checker; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "repository"))
# <!-- custom: commit_trailers is the checker under test. (Claude code Opus 5.5) -->
import commit_trailers as checker


class CommitTrailerTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.repo = Path(self.folder.name)
        for args in (("init", "-q"), ("config", "user.name", "CI fixture"), ("config", "user.email", "fixture@example.invalid"), ("config", "commit.gpgsign", "false")):
            subprocess.run(["git", *args], cwd=self.repo, check=True)

    def errors(self, message):
        subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", message], cwd=self.repo, check=True)
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()
        return checker.commit_errors(self.repo, commit)

    def test_agent_trailer_fails_in_any_case(self):
        for trailer in ("Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>", "co-authored-by: GPT-Codex-5.2 <codex@openai.com>", "Co-authored-by: ChatGPT (GPT-5.2 Thinking) <chatgpt-gpt-5.2-thinking@advciv-sas.invalid>"):
            self.assertEqual(len(self.errors("Fix a thing\n\n- Detail.\n\n" + trailer)), 1)

    def test_listed_co_authors_pass_and_others_fail(self):
        self.assertEqual(self.errors("Bump a dependency\n\nCo-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>"), [])
        self.assertEqual(len(self.errors("Fix a thing\n\nCo-authored-by: Some New Agent <agent@example.invalid>")), 1)

    def test_inline_credit_and_plain_messages_pass(self):
        self.assertEqual(self.errors("Fix a thing\n\n- Found with Claude Code Opus 5.5; Co-authored-by notes belong in prose here."), [])
        self.assertEqual(self.errors("Fix a thing\n\n- Detail."), [])


if __name__ == "__main__":
    unittest.main()
