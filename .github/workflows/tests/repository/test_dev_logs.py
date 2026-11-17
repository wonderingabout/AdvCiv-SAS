# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib, subprocess and tempfile build a disposable Git repository; sys locates the checker; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "repository"))
# <!-- custom: dev_logs is the checker under test. (Claude code Opus 5.5) -->
import dev_logs as checker

LOG = "_1_AdvCiv-SAS/Docs/dev_logs/dev_log_anonymized_email_003_AdvCiv-SAS.txt"
OLD = "commit 1111111111111111111111111111111111111111\nAuthor: someone <hidden>\nDate:   2026-01-01 10:00:00 +0100\n\nFix a typo, hand-edited\n"
NEW = "commit 2222222222222222222222222222222222222222\nAuthor: someone <hidden>\nDate:   2026-02-01 10:00:00 +0100\n\nAdd a feature\n\n"


class DevLogTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.repo = Path(self.folder.name)
        for args in (("init", "-q"), ("config", "user.name", "CI fixture"), ("config", "user.email", "fixture@example.invalid"), ("config", "commit.gpgsign", "false"), ("config", "core.autocrlf", "false")):
            subprocess.run(["git", *args], cwd=self.repo, check=True)
        self.commit(LOG, OLD, "Add the log")

    def commit(self, path, text, message):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", message], cwd=self.repo, check=True)
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()

    def test_new_entries_on_top_pass(self):
        self.assertEqual(checker.commit_errors(self.repo, self.commit(LOG, NEW + OLD, "Update the dev log")), [])

    def test_regeneration_that_drops_a_hand_edit_fails_without_the_marker(self):
        regenerated = NEW + OLD.replace("Fix a typo, hand-edited", "Fix a tyop")
        self.assertEqual(len(checker.commit_errors(self.repo, self.commit(LOG, regenerated, "Update the dev log"))), 1)

    def test_marker_allows_a_deliberate_edit(self):
        edited = OLD.replace("hand-edited", "edited again")
        self.assertEqual(checker.commit_errors(self.repo, self.commit(LOG, edited, "Fix a typo\n\n- Edit dev log: reword one entry.")), [])

    def test_a_rename_keeps_the_earlier_content_check(self):
        (self.repo / LOG).unlink()
        renamed = "_0_Legacy/Docs/dev_logs/dev_log_anonymized_email_003_AdvCiv-SAS.txt"
        self.assertEqual(checker.commit_errors(self.repo, self.commit(renamed, NEW + OLD, "Move the log")), [])

    def test_authors_must_be_hidden_while_trailer_addresses_stay(self):
        self.commit(LOG, NEW + OLD + "Co-authored-by: GPT-Codex-5.2 <codex@openai.com>\n", "Keep a trailer")
        self.assertEqual(checker.tree_errors(self.repo), [])
        self.commit(LOG, NEW.replace("someone <hidden>", "someone <someone@example.com>") + OLD, "Leak an address")
        self.assertEqual(len(checker.tree_errors(self.repo)), 1)


if __name__ == "__main__":
    unittest.main()
