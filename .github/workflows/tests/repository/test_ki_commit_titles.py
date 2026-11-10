# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib, subprocess and tempfile build disposable Git repositories; sys locates the checker; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/repository"))
# <!-- custom: ki_commit_titles is the checker under test. (Claude code Opus 5.5) -->
import ki_commit_titles as checker


def entry(ki):
    return '<a id="ki-%s"></a>\n\n## KI#%s - Fixture issue\n\nText.\n' % (ki, ki)


class KnownIssueCommitTitleTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.repo = Path(self.folder.name)
        for args in (("init", "-q"), ("config", "user.name", "CI fixture"), ("config", "user.email", "fixture@example.invalid"), ("config", "commit.gpgsign", "false")):
            subprocess.run(["git", *args], cwd=self.repo, check=True)
        self.commit(["1"], "base")

    def commit(self, kis, message):
        path = self.repo / checker.KNOWN_ISSUES
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Known Issues\n\n" + "".join(entry(ki) for ki in kis), encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", message], cwd=self.repo, check=True)
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()

    def errors(self, kis, message):
        return checker.commit_errors(self.repo, self.commit(kis, message))

    def test_up_to_three_new_kis_belong_in_the_title(self):
        self.assertEqual(self.errors(["1", "2", "2.2"], "Fix things (KI#2, KI#2.2)"), [])
        self.assertTrue(self.errors(["1", "2", "2.2", "3", "3.2"], "Fix things (KI#3)\n\nAlso KI#3.2."))
        self.assertTrue(self.errors(["1", "2", "2.2", "3", "3.2", "4"], "Fix KI#40 and KI#4.2"))

    def test_more_new_kis_may_be_named_in_the_body_or_as_a_range(self):
        self.assertEqual(self.errors(["1", "5", "6", "7", "8"], "Audit pass\n\nAdds KI#5-KI#7 and KI#8."), [])
        self.assertTrue(self.errors(["1", "5", "6", "7", "8", "8.2"], "Audit pass\n\nAdds KI#5-8."))

    def test_moved_or_edited_kis_are_not_new(self):
        self.commit(["1", "2"], "Add KI#2")
        self.assertEqual(self.errors(["2", "1"], "Reorder entries"), [])


if __name__ == "__main__":
    unittest.main()
