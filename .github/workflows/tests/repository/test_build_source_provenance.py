# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/tempfile isolate real Git histories; subprocess executes Git and extracted production PowerShell functions, hashlib checks actual patch bytes, and json/unittest verify the resulting report.
# shutil locates PowerShell; no compiler, game DLL or real build outputs are touched. (GPT-6.1-Sol) -->
from pathlib import Path
# <!-- custom: Compare reconstructed UTC instants without assuming a PowerShell serializer retains redundant .000 fractional seconds. (GPT-6.1-Sol) -->
from datetime import datetime, timezone
import hashlib
import json
# <!-- custom: os selects Windows-only Makefile/tool-resource tests and the optional local NMake path. (GPT-6.1-Sol) -->
import os
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


    # <!-- custom: A smaller report is useful only if the next build reconstructs exactly the same final input snapshot.
    # Exercise extracted production functions with compact and legacy timestamp entries plus real byte/add/remove changes; reject a compact entry that has no manifest baseline. (GPT-6.1-Sol) -->
    def test_compact_timestamp_round_trip_and_legacy_reports(self):
        def state(letter, utc):
            return {"sizeBytes": 10, "sha256": letter * 64, "modifiedUtc": utc}

        before = {"caf\u00e9.cpp": state("a", "2026-10-28T10:00:00.000Z"), "edited.cpp": state("b", "2026-10-28T10:00:00.000Z"), "removed.cpp": state("c", "2026-10-28T10:00:00.000Z")}
        after = {"caf\u00e9.cpp": state("a", "2026-10-28T11:00:00.000Z"), "edited.cpp": state("d", "2026-10-28T11:00:00.123Z"), "added.cpp": state("e", "2026-10-28T11:00:00.000Z")}
        payload = self.project / "inputs.json"
        payload.write_text(json.dumps({"before": before, "after": after}), encoding="utf-8")
        self.script.write_text("\n".join([
            '$ErrorActionPreference = "Stop"',
            '$tokens = $null; $errors = $null',
            '$ast = [Management.Automation.Language.Parser]::ParseFile($args[0], [ref]$tokens, [ref]$errors)',
            'if ($errors.Count) { throw ($errors | Out-String) }',
            'foreach ($name in @("Get-BuildInputReport", "Get-PreviousBuildInputs")) {',
            '  $f = $ast.Find({ param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq $name }, $true)',
            '  Invoke-Expression $f.Extent.Text',
            '}',
            '$data = Get-Content -LiteralPath $args[1] -Raw | ConvertFrom-Json',
            '$before = @{}; $after = @{}',
            '$data.before.PSObject.Properties | ForEach-Object { $before[$_.Name] = $_.Value }',
            '$data.after.PSObject.Properties | ForEach-Object { $after[$_.Name] = $_.Value }',
            '$changes = @(Get-BuildInputReport $before $after -IncludeBefore)',
            '$report = @{request="BUILD";status="SUCCEEDED";startedUtc="start";endedUtc="end";configuration="Release";commitAfter="fixture";',
            '  buildInputsBefore=@($before.Keys | ForEach-Object { @{path=$_;sizeBytes=$before[$_].sizeBytes;sha256=$before[$_].sha256;modifiedUtc=$before[$_].modifiedUtc} });',
            '  buildInputChanges=$changes;buildInputSummary=@{afterCount=$after.Count}}',
            '$reportPath = Join-Path (Split-Path -Parent $PSCommandPath) "report.json"',
            '[IO.File]::WriteAllText($reportPath, ($report | ConvertTo-Json -Depth 10), (New-Object Text.UTF8Encoding($false)))',
            '$compact = Get-PreviousBuildInputs $reportPath',
            '$report.buildInputChanges = @($changes | ForEach-Object { if ($_.change -eq "TIMESTAMP_ONLY") { @{path=$_.path;change=$_.change;before=$before[$_.path];after=$after[$_.path]} } else { $_ } })',
            '$report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $reportPath -Encoding UTF8',
            '$legacy = Get-PreviousBuildInputs $reportPath',
            '$report.buildInputChanges = @(@{path="missing.cpp";change="TIMESTAMP_ONLY";beforeModifiedUtc="old";afterModifiedUtc="new"})',
            '$report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $reportPath -Encoding UTF8',
            '@{changes=$changes;within=@(Get-BuildInputReport $before $after);compact=$compact;legacy=$legacy;invalid=(Get-PreviousBuildInputs $reportPath)} | ConvertTo-Json -Depth 12 -Compress',
        ]), encoding="utf-8-sig")
        result = json.loads(subprocess.check_output([POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(self.script), str(ROOT / "CvGameCoreDLL/Project/build_with_report.ps1"), str(payload)], encoding="utf-8", stderr=subprocess.PIPE))
        # <!-- custom: Windows PowerShell 5.1 preserves .000Z while PowerShell 7 can serialize that same instant as Z. Check UTC instants, including nonzero milliseconds, rather than serializer spelling; every path, hash and size must still match exactly. (GPT-6.1-Sol) -->
        def normalized_state(value):
            instant = datetime.fromisoformat(value["modifiedUtc"].replace("Z", "+00:00"))
            self.assertIsNotNone(instant.tzinfo)
            self.assertEqual(instant.utcoffset(), timezone.utc.utcoffset(instant))
            return dict(value, modifiedUtc=instant)

        for shape in ("compact", "legacy"):
            self.assertTrue(result[shape]["available"], result[shape])
            self.assertEqual({path: normalized_state(value) for path, value in result[shape]["snapshot"].items()},
                             {path: normalized_state(value) for path, value in after.items()})
        timestamp = next(row for row in result["changes"] if row["change"] == "TIMESTAMP_ONLY")
        self.assertEqual(set(timestamp), {"path", "change", "beforeModifiedUtc", "afterModifiedUtc"})
        self.assertEqual(next(row for row in result["within"] if row["change"] == "TIMESTAMP_ONLY"), timestamp)
        self.assertNotIn("before", next(row for row in result["within"] if row["change"] == "CONTENT_CHANGED"))
        edited = next(row for row in result["changes"] if row["change"] == "CONTENT_CHANGED")
        self.assertEqual((normalized_state(edited["before"]), normalized_state(edited["after"])),
                         (normalized_state(before["edited.cpp"]), normalized_state(after["edited.cpp"])))
        self.assertFalse(result["invalid"]["available"])
        self.assertEqual(result["invalid"]["reason"], "UNREADABLE_PREVIOUS_REPORT")


# <!-- custom: Exercise the real Makefile metadata recipe and extracted production parser with an overridden compiler path; merely checking a VC2003 label would miss other people's configured toolchains.
# No compiler/linker is executed. (GPT-6.1-Sol) -->
@unittest.skipUnless(POWERSHELL and os.name == "nt", "requires Windows PowerShell and NMake")
class BuildToolchainTests(unittest.TestCase):
    def setUp(self):
        nmake = shutil.which("nmake") or str(Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Microsoft Visual Studio 10.0/VC/bin/nmake.exe")
        if not Path(nmake).is_file():
            self.skipTest("NMake unavailable")
        self.nmake = nmake
        self.temporary = tempfile.TemporaryDirectory(prefix="sas-toolchain-")
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name)
        makefile = (ROOT / "CvGameCoreDLL/Project/Makefile").read_text(encoding="utf-8")
        recipe = makefile[makefile.index("sas_toolchain_info:"):makefile.index("\nclean:")]
        (self.project / "Makefile").write_text('CPP="missing-default.exe"\n!include Makefile.user\n' + recipe, encoding="utf-8")
        self.script = self.project / "capture.ps1"
        self.script.write_text("\n".join([
            '$ErrorActionPreference="Stop"',
            '$tokens=$null; $errors=$null',
            '$ast=[Management.Automation.Language.Parser]::ParseFile($args[0],[ref]$tokens,[ref]$errors)',
            'if($errors.Count){throw ($errors|Out-String)}',
            '$f=$ast.Find({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq "Get-BuildToolchain"},$true)',
            'Invoke-Expression $f.Extent.Text',
            'Set-Location -LiteralPath (Split-Path -Parent $PSCommandPath)',
            'Get-BuildToolchain -NMakePath $args[1] | ConvertTo-Json -Depth 8 -Compress',
        ]), encoding="utf-8-sig")

    def capture(self, tool):
        (self.project / "Makefile.user").write_text('\n'.join('%s="%s"' % (key, tool) for key in ("CC", "CPP", "LD", "RC")) + '\nTOOLKIT=fixture-selected-toolkit\nPSDK=fixture-selected-sdk\n', encoding="utf-8")
        return json.loads(subprocess.check_output([POWERSHELL, "-NoProfile", "-File", str(self.script), str(ROOT / "CvGameCoreDLL/Project/build_with_report.ps1"), self.nmake], encoding="utf-8", stderr=subprocess.PIPE))

    def test_overridden_selection_and_executable_version(self):
        # <!-- custom: Query a copied Windows executable's real resource version; a non-compiler fixture proves the parser reads metadata instead of hardcoding VC2003 and never invokes the selected tool. (GPT-6.1-Sol) -->
        tool = self.project / "custom compiler.exe"
        shutil.copyfile(POWERSHELL, tool)
        report = self.capture(tool)
        self.assertTrue(report["available"], report)
        self.assertEqual(report["toolkit"], "fixture-selected-toolkit")
        compiler = report["tools"]["cppCompiler"]
        self.assertTrue(compiler["available"], compiler)
        self.assertEqual(compiler["path"].lower(), str(tool).lower())
        self.assertTrue(compiler["fileVersion"], compiler)

    def test_missing_selected_executable_is_explicit(self):
        report = self.capture(self.project / "missing compiler.exe")
        self.assertTrue(report["available"], report)
        compiler = report["tools"]["cppCompiler"]
        self.assertFalse(compiler["available"], compiler)
        self.assertEqual(compiler["reason"], "EXECUTABLE_UNAVAILABLE")


# <!-- custom: Verify wrapper-entry provenance separately from compiler selection: the same selected compiler can be launched through an IDE or directly.
# Use actual parent evidence without assuming an installed IDE. (GPT-6.1-Sol) -->
@unittest.skipUnless(POWERSHELL and os.name == "nt", "requires Windows PowerShell/CIM")
class BuildInvocationTests(unittest.TestCase):
    def test_entry_modes_and_actual_parent_evidence(self):
        with tempfile.TemporaryDirectory(prefix="sas-invocation-") as temporary:
            script = Path(temporary) / "capture.ps1"
            script.write_text("\n".join([
                '$ErrorActionPreference="Stop"',
                '$tokens=$null; $errors=$null',
                '$ast=[Management.Automation.Language.Parser]::ParseFile($args[0],[ref]$tokens,[ref]$errors)',
                'if($errors.Count){throw ($errors|Out-String)}',
                '$f=$ast.Find({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq "Get-BuildInvocation"},$true)',
                'Invoke-Expression $f.Extent.Text',
                '@((Get-BuildInvocation $false),(Get-BuildInvocation $true)) | ConvertTo-Json -Depth 8 -Compress',
            ]), encoding="utf-8-sig")
            direct, ide = json.loads(subprocess.check_output([POWERSHELL, "-NoProfile", "-File", str(script), str(ROOT / "CvGameCoreDLL/Project/build_with_report.ps1")], encoding="utf-8", stderr=subprocess.PIPE))
            self.assertEqual(direct["entryMode"], "DIRECT_WRAPPER")
            self.assertEqual(ide["entryMode"], "IDE_SWITCH")
            for context in (direct, ide):
                self.assertTrue(context["powershellVersion"])
                self.assertEqual(context["ancestorState"], "OBSERVED", context)
                self.assertEqual(context["ancestors"][0]["processId"], os.getpid(), context)
                self.assertLessEqual(len(context["ancestors"]), 8)
                self.assertNotIn("commandLine", context["ancestors"][0])


if __name__ == "__main__":
    unittest.main()
