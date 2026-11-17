# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: os sets the fixture's commit dates; pathlib, subprocess and tempfile build a disposable Git repository; sys locates the checker; unittest runs the cases. (Claude code Opus 5.5) -->
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "repository"))
# <!-- custom: future_dates is the checker under test. (Claude code Opus 5.5) -->
import future_dates as checker


class FutureDateTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.repo = Path(self.folder.name)
        for args in (("init", "-q"), ("config", "user.name", "CI fixture"), ("config", "user.email", "fixture@example.invalid"), ("config", "commit.gpgsign", "false"), ("config", "core.autocrlf", "false")):
            subprocess.run(["git", *args], cwd=self.repo, check=True)

    def errors(self, path, text, committed="2026-11-16T21:24:48+01:00"):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        env = dict(os.environ, GIT_AUTHOR_DATE=committed, GIT_COMMITTER_DATE=committed)
        subprocess.run(["git", "commit", "-q", "-m", "Fixture"], cwd=self.repo, check=True, env=env)
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()
        return checker.commit_errors(self.repo, commit)

    def test_next_day_fails_and_same_or_earlier_day_passes(self):
        self.assertEqual(len(self.errors("AGENTS.md", "- Example (KI#1084, 2026-11-17): a slip.\n")), 1)
        self.assertEqual(self.errors("AGENTS.md", "- Example (KI#1084, 2026-11-16) and 2026-11-12.\n"), [])

    def test_committer_time_zone_decides_the_day(self):
        # <!-- custom: 00:30 at +01:00 is still 23:30 on the 16th in UTC, yet the 17th where the committer is. (Claude code Opus 5.5) -->
        self.assertEqual(self.errors("notes.md", "- On 2026-11-17.\n", committed="2026-11-17T00:30:00+01:00"), [])

    def test_unchanged_lines_generated_history_and_non_dates_pass(self):
        self.errors("AGENTS.md", "- Old line.\n")
        self.assertEqual(self.errors("AGENTS.md", "- Old line.\n- New line.\n"), [])
        self.assertEqual(self.errors("LLM_Helpers/context/commit_diffs/X.diff", "Date: 2027-01-01\n"), [])
        self.assertEqual(self.errors(".github/workflows/tests/repository/test_x.py", "# 2027-01-01\n"), [])
        self.assertEqual(self.errors("ids.txt", "build 12026-11-30 and 2026-11-30-1 and 2026-13-40\n"), [])


if __name__ == "__main__":
    unittest.main()
