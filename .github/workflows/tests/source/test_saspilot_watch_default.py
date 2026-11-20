# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: SASPilotConsole opens for every client unless SAS_PILOT_WATCH=0, which is only for automated tests that must not open windows.
# On 2026-11-20 an agent set it by hand for an interactive test, and the user, watching, found no console; the user asked for a check that keeps it on. No script in the repo may set it. (Claude code Opus 5.5) -->

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
# <!-- custom: An assignment in shell, PowerShell or Python; the docs and the client's own messages name it without setting it. (Claude code Opus 5.5) -->
SETS_OFF = re.compile(r"""(?:^\s*|[&|]\s*|export\s+)SAS_PILOT_WATCH=0|environ\[\s*["']SAS_PILOT_WATCH["']\s*\]\s*=|\$env:SAS_PILOT_WATCH\s*=|setdefault\(\s*["']SAS_PILOT_WATCH|["']SAS_PILOT_WATCH["']\s*:\s*["']0""")
SCANNED = ("SASPilot", "LLM_Helpers", "tests", ".github")
SUFFIXES = (".py", ".ps1", ".sh", ".bat", ".cmd", ".yml")


class SASPilotWatchDefaultTest(unittest.TestCase):
	def test_no_script_turns_the_console_off(self):
		found = []
		for folder in SCANNED:
			for path in (ROOT / folder).rglob("*"):
				if path.suffix not in SUFFIXES or path.resolve() == Path(__file__).resolve() or "commit_diffs" in path.parts:
					continue
				for (number, line) in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
					if SETS_OFF.search(line) and "os.environ.get(" not in line:
						found.append("%s:%d: %s" % (path.relative_to(ROOT).as_posix(), number, line.strip()))
		self.assertEqual(found, [], "SAS_PILOT_WATCH=0 is set in a script, so its SASPilotConsole would not open")


if __name__ == "__main__":
	unittest.main()
