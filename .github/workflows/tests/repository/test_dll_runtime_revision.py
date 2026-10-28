# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Exercise real Git/binary/report combinations: a changed revision needs a Release DLL built from that Runtime source, rather than passing on any changed binary.
# tempfile isolates the repositories; hashlib/json make realistic reports, and unittest/subprocess/sys/pathlib run the production checker. (GPT-6.1-Sol) -->
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/repository"))
# <!-- custom: Import the actual new rebuild guard rather than duplicate its revision or source-matching logic. (GPT-6.1-Sol) -->
import dll_runtime_revision as checker


class RuntimeDLLRevisionTests(unittest.TestCase):
    def test_revision_requires_matching_release_source_and_not_comment_rebuilds(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            def git(*args):
                return subprocess.check_output(["git", *args], cwd=repo, stderr=subprocess.DEVNULL).decode().strip()
            def write(path, data):
                p = repo / path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
            def commit(amend=False):
                git("add", "-A")
                git("commit", "-qm", "fixture", *(["--amend"] if amend else []))
                return git("rev-parse", "HEAD")
            def release(data, source):
                write(checker.DLL, data)
                report = dict(configuration="Release", status="SUCCEEDED", request="BUILD", exitCode=0,
                              warningCount=0, errorCount=0, durationMilliseconds=1000, logFile="AdvCiv.log",
                              startedUtc="2026-10-28T10:00:00Z", endedUtc="2026-10-28T10:00:01Z",
                              dllAfter=dict(sizeBytes=len(data), sha256=hashlib.sha256(data).hexdigest()),
                              buildInputsBefore=[dict(path=checker.SOURCE, sha256=hashlib.sha256(source).hexdigest())])
                write(checker.DLL + ".build.json", json.dumps(report).encode())
            git("init", "-q")
            git("config", "user.name", "CI fixture")
            git("config", "user.email", "fixture@example.invalid")
            git("config", "commit.gpgsign", "false")
            git("config", "core.autocrlf", "false")
            write(checker.CHECK, b"# guard present\n")
            write("CvGameCoreDLL/Project/build_with_report.ps1", b"# build report fixture\n")
            source = b"enum { SAS_RUNTIME_REVISION = 1 };\n"
            write(checker.SOURCE, source)
            write(checker.DLL, b"old binary")
            commit()
            write(checker.SOURCE, source + b"// comment only\n")
            unchanged = commit()
            self.assertEqual(checker.check(repo, [unchanged]), ([], 0))
            source2 = b"enum { SAS_RUNTIME_REVISION = 2 };\n"
            write(checker.SOURCE, source2)
            missing = commit()
            self.assertIn("update the Release DLL/report", checker.check(repo, [missing])[0][0])
            release(b"release two", source2.replace(b"\n", b"\r\n"))
            good = commit(amend=True)
            self.assertEqual(checker.check(repo, [good]), ([], 1))
            source3 = b"enum { SAS_RUNTIME_REVISION = 3 };\n"
            write(checker.SOURCE, source3)
            release(b"unrelated new binary", source2)
            wrong_source = commit()
            self.assertIn("does not match the Runtime source", checker.check(repo, [wrong_source])[0][0])
            release(b"release three", source3)
            corrected = commit(amend=True)
            self.assertEqual(checker.check(repo, [corrected]), ([], 1))
            # <!-- custom: A later build cannot rescue an ordinary source-only commit, but an explicit squash PR is one eventual integration and may build at its final head.
            # Test the actual CLI label selection too. (GPT-6.1-Sol) -->
            source4 = b"enum { SAS_RUNTIME_REVISION = 4 };\n"
            write(checker.SOURCE, source4)
            missing4 = commit()
            release(b"release four", source4)
            later4 = commit()
            self.assertTrue(checker.check(repo, [missing4, later4])[0])
            self.assertEqual(checker.check(repo, [later4], corrected), ([], 1))
            event = dict(repository=dict(default_branch="main"), pull_request=dict(
                base=dict(ref="main", sha=corrected), head=dict(sha=later4), labels=[dict(name="revision:squash")]))
            event_path = repo / "event.json"
            command = [sys.executable, checker.__file__, "--repo-root", str(repo), "--event-name", "pull_request", "--event-path", str(event_path)]
            event_path.write_text(json.dumps(event), encoding="utf-8")
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            event["pull_request"]["labels"] = []
            event_path.write_text(json.dumps(event), encoding="utf-8")
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            # <!-- custom: Manual dispatch also supplies GITHUB_EVENT_PATH but lacks push/PR before/after fields; select its requested head before interpreting that event shape. (GPT-6.1-Sol) -->
            manual = [sys.executable, checker.__file__, "--repo-root", str(repo), "--head-ref", corrected, "--event-name", "workflow_dispatch", "--event-path", str(event_path)]
            result = subprocess.run(manual, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
