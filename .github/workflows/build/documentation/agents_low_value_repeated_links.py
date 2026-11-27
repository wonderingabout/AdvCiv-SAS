#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Keeps low-value repeated links out of AGENTS.md: agents read it whole, so a link whose target the text already names only adds a path to read past (the user, 2026-11-24).
# KI links are the only kind covered as of now: AGENTS.md links only its first KI mention, to show where the Known Issues live, and names every KI as plain KI#N after that, as a KI number names itself and the 50-character Known Issues path was churn that took agents' focus.
# The request named the rule but not its intent, so Claude Code Opus 5.5 first read it as each KI's own first mention, and its --fix added 46 links; once the user gave the intent, it was clear that this went the opposite way.
# Other links are not covered: links to helpers may repeat, as each repeat reminds agents that the helper matters, and links to guides and AGENTS.md's own sections may too, as only about 20 of them repeated, too few to be worth a rule.
# Mentions inside code spans, fenced blocks and other links' labels are skipped, as a link cannot go there.
# Named for what it removes: links repeated across the document that are of low value; not agents_ki_links, too narrow, or agents_repeated_links alone, as some repeats are allowed, or agents_boilerplate_links, as these links were written one by one, not copied in a set shape.
# --fix links the first mention and unlinks the rest in place. (Claude code Opus 5.5) -->

from __future__ import annotations

# <!-- custom: argparse reads the options, pathlib finds the file, re finds the mentions and sys reports the result. (Claude code Opus 5.5) -->
import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
FILES = ("AGENTS.md",)
KI_DOC = "/_1_AdvCiv-SAS/Docs/README_Known_Issues.md"
NUMBER = r"\d+(?:\.\d+)*"
# <!-- custom: A KI link, a bare KI#N, a code span or any other link; the last two are kept as they are, and a bare KI#N inside another link's label is not a separate mention. (Claude code Opus 5.5) -->
TOKEN = re.compile(r"(?P<code>`[^`]*`)|\[KI#(?P<linked>" + NUMBER + r")\]\(" + re.escape(KI_DOC) + r"#ki-(?P=linked)\)|(?P<other>\[[^\]]*\]\([^)]*\))|KI#(?P<bare>" + NUMBER + r")(?![\d])")


def link(number):
    return "[KI#%s](%s#ki-%s)" % (number, KI_DOC, number)


# <!-- custom: A number with no entry is not linked: an earlier --fix run linked KI#176.2, a number the docs mention as filed and then merged into KI#1091, whose anchor does not exist. (Claude code Opus 5.5) -->
def ki_anchors(root):
    text = (root / KI_DOC.lstrip("/")).read_bytes().decode("utf-8")
    return set(re.findall(r'<a id="ki-(' + NUMBER + r')"></a>', text))


def process(text, anchors):
    seen = set()
    first_done = False
    errors = []
    out_lines = []
    in_fence = False
    for line_number, line in enumerate(text.split("\n"), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:
            out_lines.append(line)
            continue
        pieces = []
        last = 0
        for match in TOKEN.finditer(line):
            pieces.append(line[last:match.start()])
            last = match.end()
            replacement = match.group(0)
            if match.group("code"):
                for number in re.findall(r"KI#(" + NUMBER + r")(?![\d])", match.group("code")):
                    seen.add(number)
            elif match.group("other"):
                for number in re.findall(r"KI#(" + NUMBER + r")(?![\d])", match.group("other")):
                    seen.add(number)
            elif match.group("linked"):
                number = match.group("linked")
                if first_done:
                    errors.append("%d: KI#%s is linked; only the file's first KI mention is" % (line_number, number))
                    replacement = "KI#" + number
                first_done = True
                seen.add(number)
            else:
                number = match.group("bare")
                if not first_done and number in anchors:
                    errors.append("%d: KI#%s is the file's first KI mention and has no link" % (line_number, number))
                    replacement = link(number)
                    first_done = True
                seen.add(number)
            pieces.append(replacement)
        pieces.append(line[last:])
        out_lines.append("".join(pieces))
    return errors, "\n".join(out_lines), len(seen)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check that AGENTS.md links only its first Known Issue mention.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--fix", action="store_true", help="link the first KI mention and unlink the rest in place")
    args = parser.parse_args(argv)
    errors = []
    count = 0
    anchors = ki_anchors(args.repo_root)
    for name in FILES:
        path = args.repo_root / name
        text = path.read_bytes().decode("utf-8")
        file_errors, fixed, file_count = process(text, anchors)
        count += file_count
        if args.fix and fixed != text:
            path.write_bytes(fixed.encode("utf-8"))
            print("fixed %s: %d change(s)" % (name, len(file_errors)))
            continue
        errors.extend("%s:%s" % (name, error) for error in file_errors)
    print("%s AGENTS.md low-value repeated links: first KI mention only (%d KIs)" % ("FAIL" if errors else "PASS", count))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
