# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and tempfile hold the JSON copies; subprocess runs the check as CI does; sys gives the interpreter; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
CHECK = ROOT / ".github" / "workflows" / "build" / "repository" / "ui_map_sync.py"
MAP_JSON = ROOT / "LLM_Helpers" / "game_runs" / "ui_maps" / "civ4_ui_map.json"


# <!-- custom: On 2026-11-16 the check compared bytes and failed on an unchanged JSON in a Windows clone whose checkout writes CRLF; line endings must not matter, while a content change must still fail. (Claude code Opus 5.5) -->
class UiMapSyncTests(unittest.TestCase):
    def run_check(self, text):
        with tempfile.TemporaryDirectory() as folder:
            copy = Path(folder) / "civ4_ui_map.json"
            copy.write_bytes(text.encode("utf-8"))
            return subprocess.run([sys.executable, str(CHECK), "--map-json", str(copy)], capture_output=True, text=True)

    def committed_text(self):
        return MAP_JSON.read_text(encoding="utf-8")

    def test_crlf_and_lf_copies_pass(self):
        text = self.committed_text()
        for newline in ("\n", "\r\n"):
            result = self.run_check(text.replace("\n", newline))
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_content_change_fails(self):
        result = self.run_check(self.committed_text().replace("scenario", "scenari0", 1))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("differs", result.stdout)


if __name__ == "__main__":
    unittest.main()
