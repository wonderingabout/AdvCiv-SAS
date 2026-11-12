#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: A guide's disclaimer only protects the user if readers meet it before anything else.
# On 2026-11-12 the user asked that the modding and EXE patches disclaimers stay first, so a later edit cannot push them down unnoticed.
# A first draft required them as the first sections after the description; the user preferred them directly under the title, before the description, as a quote block, so that is what this checks. (Claude code Opus 5.5) -->
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
# <!-- custom: Each guide and the bold label its disclaimer quote starts with.
# The user preferred a plain "Disclaimer:", which covers the whole guide, over narrower labels such as "EXE patches disclaimer:".
# Add a guide here when it gets a disclaimer of its own. (Claude code Opus 5.5) -->
REQUIRED_DISCLAIMERS = {
	"_1_AdvCiv-SAS/Docs/Modding_Resources/README.md": "Disclaimer:",
	"_1_AdvCiv-SAS/Docs/Modding_Resources/README_EXE_Patches.md": "Disclaimer:",
}


def errors_for(document, text, label):
	# <!-- custom: The first non-blank line must be the "# " title and the next one the quote "> **<label>**". (Claude code Opus 5.5) -->
	lines = [line for line in text.splitlines() if line.strip()]
	expected = "> **%s**" % label
	if not lines or not lines[0].startswith("# "):
		return ["%s: must start with its '# ' title, followed by the disclaimer %r" % (document, expected)]
	if len(lines) < 2 or not lines[1].startswith(expected):
		found = lines[1][:80] if len(lines) > 1 else "(nothing)"
		return ["%s: the line after the title is %r; keep the disclaimer quote starting %r directly under the title, before the description" % (document, found, expected)]
	return []


def main():
	errors = []
	for document, label in sorted(REQUIRED_DISCLAIMERS.items()):
		path = ROOT / document
		if not path.is_file():
			errors.append("%s: missing; update REQUIRED_DISCLAIMERS in disclaimers_first.py if it moved" % document)
			continue
		errors.extend(errors_for(document, path.read_text(encoding="utf-8"), label))
	for error in errors:
		print("ERROR: " + error)
	if errors:
		return 1
	print("PASS: %d guides keep their disclaimer directly under the title" % len(REQUIRED_DISCLAIMERS))
	return 0


if __name__ == "__main__":
	sys.exit(main())
