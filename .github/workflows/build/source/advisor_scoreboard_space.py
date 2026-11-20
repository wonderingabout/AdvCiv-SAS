#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: every advisor that leaves the scoreboard the space getAdvisorScoreboardSpace gives carries SAS_LEAVES_SCOREBOARD_SPACE, and only those do.
# <!-- custom: While such an advisor is open, the scoreboard shortens leader names to fit beside it; CvScreensInterface finds open advisors by that class marker, which replaced a hand-kept list of 8 screen IDs (the user, 2026-11-20).
# An advisor without the marker would leave the scoreboard's war dots and power ratios under it at 1920 px and font 4; a marker on a screen sized otherwise would cut names for nothing. (Claude code Opus 5.5) -->

from pathlib import Path
import argparse
import re
import sys

# <!-- custom: xml_defines from the workflows' lib/ gives the repository root, as the other build checks find it. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import get_default_repo_root


SCAN_RELATIVE_DIR = Path("Assets/Python")
# <!-- custom: A call, not the definition: "def getAdvisorScoreboardSpace(" is excluded by the lookbehind.
# Comments are stripped first, whole-line and inline, so a mention in prose does not count (Claude code Opus 5.5 + GPT-6.2-Sol). -->
CALL = re.compile(r"(?<!def )\bgetAdvisorScoreboardSpace\(")
COMMENT = re.compile(r"#.*$")
# <!-- custom: The marker is a class-body declaration, so a subclass inherits it; the convention is that the advisor class calling getAdvisorScoreboardSpace declares it in its own file, not in __init__.
# A subclass that calls the helper itself while only inheriting the marker would fail this check, as would self.SAS_LEAVES_SCOREBOARD_SPACE set in __init__ (Claude code Opus 5.5 + GPT-6.2-Sol). -->
MARKER = re.compile(r"^\s+SAS_LEAVES_SCOREBOARD_SPACE = True\b", re.M)
# <!-- custom: Files that call getAdvisorScoreboardSpace without being such an advisor, with the reason. (Claude code Opus 5.5) -->
EXEMPT = {
	"Assets/Python/EntryPoints/CvScreensInterface.py": "looks up the space the open advisor leaves",
	"Assets/Python/Screens/CvTechChooser.py": "the Tech Advisor reaches further below 2560 px, and getOpenAdvisorScoreboardSpace reads its space apart",
}


def find_problems(repo_root):
	problems = []
	for path in sorted((repo_root / SCAN_RELATIVE_DIR).rglob("*.py")):
		relative = path.relative_to(repo_root).as_posix()
		text = path.read_text(encoding="utf-8", errors="replace")
		code = "\n".join(COMMENT.sub("", line) for line in text.splitlines())
		bCalls = CALL.search(code) is not None
		bMarked = MARKER.search(code) is not None
		if relative in EXEMPT:
			if bMarked:
				problems.append("%s: carries SAS_LEAVES_SCOREBOARD_SPACE but is exempt (%s)" % (relative, EXEMPT[relative]))
			continue
		if bCalls and not bMarked:
			problems.append("%s: calls getAdvisorScoreboardSpace but its advisor class lacks SAS_LEAVES_SCOREBOARD_SPACE = True, so the scoreboard would not fit beside it" % relative)
		elif bMarked and not bCalls:
			problems.append("%s: carries SAS_LEAVES_SCOREBOARD_SPACE but never calls getAdvisorScoreboardSpace" % relative)
	return problems


def main():
	parser = argparse.ArgumentParser(description="Check that every advisor leaving the scoreboard space carries SAS_LEAVES_SCOREBOARD_SPACE.")
	parser.add_argument("--repo-root", type=Path, default=get_default_repo_root())
	args = parser.parse_args()
	problems = find_problems(args.repo_root.resolve())
	for problem in problems:
		print("ERROR: " + problem)
	if problems:
		print("FAIL advisor scoreboard space (%d)" % len(problems))
		return 1
	print("PASS advisor scoreboard space")
	return 0


if __name__ == "__main__":
	sys.exit(main())
