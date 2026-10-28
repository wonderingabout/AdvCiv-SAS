# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Exercise production reference checks against disposable real Git histories, including rewritten and preserved identities; pathlib/sys locate the helper and tempfile/unittest isolate the cases. (GPT-6.1-Sol) -->
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/diagnostics"))
# <!-- custom: Exercise the production reference guard through real Git fixtures rather than reproducing its policy in the tests. (GPT-6.1-Sol) -->
import revision_commit_references as refs


class RevisionCommitReferenceTests(unittest.TestCase):
    # <!-- custom: The UI review caught plain commit hashes in revision prose; keep code-value formatting distinct from pending status. (GPT-6.1-Sol) -->
    def test_finalized_references_use_backticks(self):
        plain = "### Revision 1\n- **Git commit:** " + "a" * 40 + "\n"
        self.assertTrue(refs.reference_format_errors(plain))
        self.assertEqual(refs.reference_format_errors(self.document("a" * 40)), [])
        self.assertEqual(refs.reference_format_errors(self.document()), [])
        self.assertTrue(refs.reference_format_errors(self.document().replace("pending", "`pending`")))

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.repo, text=True, stderr=subprocess.DEVNULL).strip()

    def write(self, path, text):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def document(self, value="pending"):
        reference = value if value == "pending" else f"`{value}`"
        return f"### Revision 1\n- **Git commit:** {reference}\n- **Change:** Fixture behavior.\n"

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        self.git("init", "-q")
        for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.invalid"), ("commit.gpgsign", "false"), ("core.autocrlf", "false")):
            self.git("config", key, value)
        self.write("README.md", "baseline\n")
        self.base = self.commit("baseline")
        self.git("branch", "-f", "canonical", self.base)
        self.write(refs.runtime.SOURCE, "enum { SAS_RUNTIME_REVISION = 1 };\n")
        self.write(refs.runtime.HISTORY, self.document())
        self.write(".github/workflows/build/diagnostics/revision_commit_references.py", "# lifetime policy active\n")
        self.introduction = self.commit("introduce recorder")

    def check(self):
        return refs.check(self.repo, "canonical", "push", {"before": self.base, "after": self.git("rev-parse", "HEAD")})

    def test_introduction_passes_but_unrelated_next_commit_fails(self):
        self.assertEqual(self.check(), [])
        self.write("README.md", "unrelated update\n")
        self.commit("next commit")
        self.assertTrue(any("finalize pending" in error for error in self.check()))

    # <!-- custom: Unstaged local artifacts/settings are not the next commit candidate; staging any actual change restores the one-commit lifetime requirement. (GPT-6.1-Sol) -->
    def test_unstaged_build_outputs_do_not_create_a_commit_candidate(self):
        self.write("Assets/CvGameCoreDLL.dll.build.json", '{"configuration":"Debug-opt"}\n')
        self.write("Assets/XML/GlobalDefines_advciv_sas.xml", "<localDiagnostics/>\n")
        self.assertEqual(self.check(), [])
        self.git("add", "Assets/CvGameCoreDLL.dll.build.json")
        self.assertTrue(any("working-tree" in error and "finalize pending" in error for error in self.check()))
        self.write(refs.runtime.HISTORY, self.document(self.introduction))
        self.assertTrue(any("working-tree" in error and "finalize pending" in error for error in self.check()))
        self.git("add", refs.runtime.HISTORY)
        self.assertEqual(self.check(), [])

    def test_next_commit_finalizes_reference(self):
        self.write(refs.runtime.HISTORY, self.document(self.introduction))
        self.commit("finalize reference")
        self.assertEqual(self.check(), [])

    def test_amend_orphans_reference_and_replacement_repairs_it(self):
        self.git("commit", "--amend", "-qm", "rewritten introduction")
        amended = self.git("rev-parse", "HEAD")
        self.write(refs.runtime.HISTORY, self.document(self.introduction))
        errors = refs.reference_errors(self.repo, refs.runtime.HISTORY, refs.runtime_revision, self.base)
        self.assertTrue(any("ancestry" in error for error in errors))
        self.write(refs.runtime.HISTORY, self.document(amended))
        self.assertEqual(refs.reference_errors(self.repo, refs.runtime.HISTORY, refs.runtime_revision, self.base), [])

    def test_merge_preserves_feature_reference(self):
        self.write(refs.runtime.HISTORY, self.document(self.introduction))
        self.commit("finalize reference")
        feature = self.git("branch", "--show-current")
        self.git("checkout", "-qb", "integration", self.base)
        self.git("merge", "--no-ff", "-qm", "preserve feature commits", feature)
        tip = self.git("rev-parse", "HEAD")
        self.assertEqual(refs.reference_errors(self.repo, refs.runtime.HISTORY, refs.runtime_revision, tip), [])

    def test_squash_accepts_pending_then_requires_resulting_identity(self):
        self.write("README.md", "another draft step\n")
        self.commit("intermediate step")
        self.assertEqual(refs.check(self.repo, "canonical", squash=True), [])
        self.git("reset", "--soft", self.base)
        squashed = self.commit("squashed recorder")
        self.write(refs.runtime.HISTORY, self.document(self.introduction))
        self.assertTrue(any("ancestry" in error for error in refs.reference_errors(
            self.repo, refs.runtime.HISTORY, refs.runtime_revision, squashed)))
        self.write(refs.runtime.HISTORY, self.document(squashed))
        self.assertEqual(refs.reference_errors(self.repo, refs.runtime.HISTORY, refs.runtime_revision, squashed), [])

    def test_ancestral_hash_with_wrong_revision_fails(self):
        self.write(refs.runtime.HISTORY, self.document(self.base))
        self.assertTrue(any("matching recorder revision" in error for error in refs.reference_errors(
            self.repo, refs.runtime.HISTORY, refs.runtime_revision, self.base)))


if __name__ == "__main__":
    unittest.main()
