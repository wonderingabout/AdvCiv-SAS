# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: A numbered reference is one token, so one grep finds every mention: KI#1104 is written so 21,972 times and never with a space, while pull requests were written both ways, 29 spaced against 5 joined, and a grep for one missed the other (the user, 2026-11-23).
# Each entry is a label, the spaced spelling it rejects and the joined one it becomes; numbered_references.py checks the repository's files and squash_pr_number.py commit messages against the same table.
# Runtime revisions, such as Runtime12, are not listed yet: 22 are spaced, but 4 of them sit in the Runtime subsystem's own sources, SASRuntimeStatus.cpp and its observer scripts, where even a comment change counts as a Runtime change that needs a revision bump; they can join the table with the next commit that bumps Runtime. (Claude code Opus 5.5) -->
import re

SPELLINGS = (
	("PR", re.compile(r"(?<![A-Za-z0-9_])[Pp][Rr] #([0-9])"), r"PR#\1"),
	("KI", re.compile(r"(?<![A-Za-z0-9_])KI #([0-9])"), r"KI#\1"),
	("SGR", re.compile(r"(?<![A-Za-z0-9_])SGR ([0-9])"), r"SGR\1"),
	# <!-- custom: The oldest KIs were cited in words, such as "see known issue as of now N" or "known issue number N", on 129 lines of C++ and Python comments, XML, the Known Issues and the SAS dev log, which a grep for KI#53.2.2 missed (the user, 2026-11-23).
	# "as of now" was there because KI numbers were not yet stable, which they are now, so it goes with the words.
	# A second pass found "as of" and the typo "of as now" before the number too, which the first pattern missed. (Claude code Opus 5.5) -->
	("Known issue", re.compile(r"(?i)(?<![A-Za-z0-9_])(?:as of now )?known[ _-]?issues?(?: as of(?: now)?| of as now)?:? ?(?:number |no\. ?|#)? ?([0-9])"), r"KI#\1"),
)


def spaced(text):
	return [label for label, pattern, _ in SPELLINGS if pattern.search(text)]


def joined(text):
	for _, pattern, replacement in SPELLINGS:
		text = pattern.sub(replacement, text)
	return text
