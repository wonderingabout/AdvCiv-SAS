# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/tempfile isolate real Git histories; subprocess executes Git and extracted production PowerShell functions, hashlib checks actual patch bytes, and json/unittest verify the resulting report.
# shutil locates PowerShell; no compiler, game DLL or real build outputs are touched. (GPT-6.1-Sol) -->
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
# <!-- custom: tempfile keeps Git histories away from the real checkout; unittest verifies successful captures and explicit unavailable results. (GPT-6.1-Sol) -->
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")


@unittest.skipUnless(POWERSHELL, "PowerShell unavailable")
class BuildSourceProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="sas-build-provenance-")
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.project = self.repo / "CvGameCoreDLL/Project"
        self.project.mkdir(parents=True)
        self.names = ["plain.cpp", "caf\u00e9.cpp", "name [x].cpp"]
        for name in self.names:
            (self.repo / "CvGameCoreDLL" / name).write_text("// baseline\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "baseline")
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
        self.script = self.project / "capture.ps1"
        # <!-- custom: Parse only the named production functions, never the wrapper body that starts compilation; replace its project-root context with this disposable repository. (GPT-6.1-Sol) -->
        self.script.write_text("\n".join([
            '$ErrorActionPreference = "Stop"',
            '[Console]::OutputEncoding = New-Object Text.UTF8Encoding($false)',
            '$tokens = $null; $errors = $null',
            '$ast = [Management.Automation.Language.Parser]::ParseFile($args[0], [ref]$tokens, [ref]$errors)',
            'if ($errors.Count) { throw ($errors | Out-String) }',
            '$fixtureProject = Split-Path -Parent $PSCommandPath',
            'Set-Location -LiteralPath $fixtureProject',
            'foreach ($name in @("Get-GitText", "Get-SourceDiffState", "Get-SourceProvenance", "Get-BuildFileState")) {',
            '  $function = $ast.Find({ param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq $name }, $true)',
            "  Invoke-Expression ($function.Extent.Text.Replace('$PSScriptRoot', '$fixtureProject'))",
            '}',
            'Get-SourceProvenance | ConvertTo-Json -Depth 12 -Compress',
        ]), encoding="utf-8-sig")

    def git(self, *args):
        return subprocess.check_output(["git", "-c", "core.autocrlf=false", *args], cwd=self.repo, stderr=subprocess.PIPE)

    def capture(self):
        output = subprocess.check_output([POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(self.script), str(ROOT / "CvGameCoreDLL/Project/build_with_report.ps1")], encoding="utf-8", stderr=subprocess.PIPE)
        return json.loads(output)

    def test_clean_and_partially_staged_unicode_literal_paths(self):
        clean = self.capture()
        self.assertEqual(clean["branchRelation"], "AT_DEFAULT")
        self.assertTrue(clean["unstagedCodeRulesDiff"]["available"])
        self.assertEqual(clean["unstagedCodeRulesDiff"]["fileCount"], 0)
        for name in self.names:
            path = "CvGameCoreDLL/" + name
            (self.repo / path).write_text("// staged\n", encoding="utf-8")
            self.git("--literal-pathspecs", "add", path)
            (self.repo / path).write_text("// unstaged\n", encoding="utf-8")
        snapshot = self.capture()
        for field, cached in (("stagedCodeRulesDiff", True), ("unstagedCodeRulesDiff", False)):
            layer = snapshot[field]
            self.assertTrue(layer["available"], layer)
            self.assertEqual(layer["fileCount"], len(self.names))
            for entry in layer["files"]:
                args = ["--literal-pathspecs", "diff"] + (["--cached"] if cached else [])
                patch = self.git(*args, "--binary", "--full-index", "--no-ext-diff", "--no-textconv", "--no-renames", "--no-color", "--", entry["path"])
                self.assertGreater(len(patch), 0)
                self.assertEqual(entry["diffBytes"], len(patch))
                self.assertEqual(entry["sha256"].lower(), hashlib.sha256(patch).hexdigest())
            self.assertEqual({row["path"] for row in layer["files"]}, {"CvGameCoreDLL/" + name for name in self.names})

    def test_failed_optional_diff_capture_does_not_abort_report(self):
        path = self.repo / "CvGameCoreDLL/plain.cpp"
        path.write_text("// staged\n", encoding="utf-8")
        self.git("add", "CvGameCoreDLL/plain.cpp")
        path.write_text("// unstaged\n", encoding="utf-8")
        self.git("config", "diff.orderFile", str(self.repo / "missing-order-file"))
        snapshot = self.capture()
        self.assertTrue(snapshot["available"])
        for field in ("stagedCodeRulesDiff", "unstagedCodeRulesDiff"):
            self.assertFalse(snapshot[field]["available"])
            self.assertEqual(snapshot[field]["reason"], "GIT_DIFF_UNAVAILABLE")

    def test_branch_relations_and_tracking_fallback(self):
        self.git("checkout", "-qb", "candidate")
        self.git("commit", "--allow-empty", "-qm", "candidate")
        self.assertEqual(self.capture()["branchRelation"], "AHEAD_OF_DEFAULT")
        self.git("checkout", "-q", "main")
        self.git("commit", "--allow-empty", "-qm", "main one")
        self.git("commit", "--allow-empty", "-qm", "main two")
        self.git("checkout", "-q", "candidate")
        diverged = self.capture()
        self.assertEqual((diverged["branchRelation"], diverged["currentOnlyCommits"], diverged["defaultOnlyCommits"]), ("DIVERGED", 1, 2))
        self.git("reset", "--hard", "refs/remotes/origin/main")
        self.assertEqual(self.capture()["branchRelation"], "BEHIND_DEFAULT")
        self.git("branch", "-D", "main")
        fallback = self.capture()
        self.assertEqual((fallback["defaultRefSource"], fallback["branchRelation"]), ("REMOTE_TRACKING", "AT_DEFAULT"))


if __name__ == "__main__":
    unittest.main()
