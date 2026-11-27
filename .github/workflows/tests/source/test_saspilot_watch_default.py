# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: SASPilotConsole opens for every client unless SAS_PILOT_WATCH=0, which is only for automated tests that must not open windows.
# On 2026-11-20 an agent set it by hand for an interactive test, and the user, watching, found no console; the user asked for a check that keeps it on. No script in the repo may set it. (Claude code Opus 5.5) -->
# <!-- custom: On 2026-11-27 Codex set SAS_PILOT_WATCH=0 by hand eleven times in an interactive test, past the warning printed on each command, so the switch moved to SAS_PILOT_CONSOLE_ON in Assets/Python/SASSessionTunables.py, where a 0 shows in git status and fails hands_free_defaults.py in a commit.
# This check now fails when SASPilot's Python reads an environment variable about the console or its watch again, a switch an agent can flip unseen. (Claude code Opus 5.5) -->

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
# <!-- custom: A read of an environment variable naming the watch or the console, such as the retired os.environ.get("SAS_PILOT_WATCH"). (Claude code Opus 5.5) -->
READS_SWITCH = re.compile(r"""(?:environ|getenv)\b[^#]*["'][A-Z_]*(?:WATCH|CONSOLE)[A-Z_]*["']""")


class SASPilotWatchDefaultTest(unittest.TestCase):
	def test_no_environment_switch_turns_the_console_off(self):
		found = []
		for path in sorted((ROOT / "SASPilot").rglob("*.py")):
			for (number, line) in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
				if READS_SWITCH.search(line):
					found.append("%s:%d: %s" % (path.relative_to(ROOT).as_posix(), number, line.strip()))
		self.assertEqual(found, [], "SASPilot reads an environment switch for its console; every client opens one, see README_SASPilot.md")


if __name__ == "__main__":
	unittest.main()
