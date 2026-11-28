# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Stage part of a file without touching the working file: the non-interactive counterpart of 'git add -p', which agents cannot drive.
# On 2026-11-19 the SASPilot strategy commit had to leave out the Greatest Civilizations work mixed into the same files (a command, its help, two screen fixes, a doc row and a playtests bullet), kept for its own commit; a scratch script did it first, and the user asked that such scripts join the repository. (Claude code Opus 5.5) -->
# <!-- custom: Example: python LLM_Helpers/commits/stage_partial.py SASPilot/game/SASPilotCommands.py --head "def cmd_topcivs(args):" "\n\n\n" --drop " - Turn 82:" "\n - The user's" (Claude code Opus 5.5) -->

# <!-- custom: argparse for the regions, codecs to decode the markers' escapes, difflib for the dry run, io and os to read the working file, subprocess for git, sys for the exit code. (Claude code Opus 5.5) -->
import argparse
import codecs
import difflib
import io
import os
import subprocess
import sys


def unescape(text):
    # <!-- custom: Markers come from a shell, so escapes such as \n are decoded here; a Bash heredoc or script would halve the backslashes (AGENTS.md, Naming, diagnostics and text encoding). (Claude code Opus 5.5) -->
    # <!-- custom: unicode_escape alone read a non-ASCII marker as UTF-8 bytes, so "x → y" became mojibake and was reported not found; turning such characters into \u escapes first lets them pass through unchanged. (Claude code Opus 5.5) -->
    return codecs.decode(text.encode("latin-1", "backslashreplace"), "unicode_escape")


def region(text, start, end, label):
    i = text.find(start)
    if i < 0:
        raise SystemExit("%s: start marker not found: %r" % (label, start))
    if text.find(start, i + 1) >= 0:
        raise SystemExit("%s: start marker found more than once: %r" % (label, start))
    # <!-- custom: <EOF> ends a region at the file's end, for an entry appended last, such as KI#1103 after KI#1102 in the Known Issues (2026-11-21). (Claude code Opus 5.5) -->
    if end == "<EOF>":
        return i, len(text)
    j = text.find(end, i + len(start))
    if j < 0:
        raise SystemExit("%s: end marker not found after the start: %r" % (label, end))
    return i, j


# <!-- custom: --keep stages only the hunks whose old or new lines hold one of the markers, and leaves every other hunk at HEAD: the opposite of --head, for a commit that takes a few hunks out of a file mostly meant for later commits.
# A hunk is a run of changes with at most one unchanged line between them, close to git diff -U1's; added on 2026-11-21 for the first of the themed commits to main, whose fix sat among the advisor work in CvMilitaryAdvisor.py.
# Unchanged context lines are not searched: on 2026-11-26, --keep SAS_SGR_REVISION found no hunk for a revision bump, as the define's name sits on the unchanged line above its value, so the help and the error now say so; --keep "<iDefineIntVal>216</iDefineIntVal>" staged it. (Claude code Opus 5.5) -->
def keep_hunks(old, text, markers):
    old_lines = old.splitlines(True)
    new_lines = text.splitlines(True)
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    # <!-- custom: Copied before grouping: get_grouped_opcodes trims the first and last unchanged runs of the matcher's own cached list, and the first version, reading get_opcodes() again afterwards, staged CvMilitaryAdvisor.py without its first 341 and last 356 lines. (Claude code Opus 5.5) -->
    opcodes = list(matcher.get_opcodes())
    kept = set()
    for group in matcher.get_grouped_opcodes(1):
        changed = [(i1, i2, j1, j2) for (tag, i1, i2, j1, j2) in group if tag != "equal"]
        lines = "".join("".join(old_lines[i1:i2]) + "".join(new_lines[j1:j2]) for (i1, i2, j1, j2) in changed)
        if any(marker in lines for marker in markers):
            kept.update(changed)
    found = [marker for marker in markers if any(marker in "".join(old_lines[i1:i2]) + "".join(new_lines[j1:j2]) for (i1, i2, j1, j2) in kept)]
    missing = [marker for marker in markers if marker not in found]
    if missing:
        raise SystemExit("--keep marker found in no changed hunk: %r (only the hunk's removed and added lines are searched, not its unchanged context)" % missing[0])
    result = []
    for (tag, i1, i2, j1, j2) in opcodes:
        if tag == "equal" or (i1, i2, j1, j2) not in kept:
            result.extend(old_lines[i1:i2])
        else:
            result.extend(new_lines[j1:j2])
    return "".join(result)


def git(root, args, data=None):
    result = subprocess.run(["git"] + args, cwd=root, input=data, capture_output=True)
    if result.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), result.stderr.decode("utf-8", "replace")))
    return result.stdout


def main(argv):
    parser = argparse.ArgumentParser(description="Stage a file with chosen regions taken from HEAD or dropped; the working file is not changed.")
    parser.add_argument("path", help="file to stage, relative to the repository root")
    parser.add_argument("--head", nargs=2, action="append", default=[], metavar=("START", "END"), help="replace the working region from START up to END (END excluded) with HEAD's same region; END may be <EOF> for the file's end; repeatable")
    parser.add_argument("--drop", nargs=2, action="append", default=[], metavar=("START", "END"), help="leave the region from START up to END (END excluded) out of the staged version; END may be <EOF> for the file's end; repeatable")
    parser.add_argument("--keep", action="append", default=[], metavar="MARKER", help="stage only the changed hunks whose removed or added lines hold MARKER (unchanged context lines do not count), every other hunk staying at HEAD; repeatable, and applied before --head and --drop")
    parser.add_argument("--dry-run", action="store_true", help="print the staged diff against HEAD without staging")
    args = parser.parse_args(argv)
    # <!-- custom: Windows consoles default to cp1252, and a dry run printing a line holding a character such as → stopped with UnicodeEncodeError, so print UTF-8. (Claude code Opus 5.5) -->
    sys.stdout.reconfigure(encoding="utf-8")
    if not args.head and not args.drop and not args.keep:
        raise SystemExit("give at least one --keep marker or --head or --drop region")
    root = git(".", ["rev-parse", "--show-toplevel"]).decode("utf-8").strip()
    path = args.path.replace("\\", "/")
    text = io.open(os.path.join(root, path), encoding="utf-8", newline="").read()
    old = git(root, ["show", "HEAD:" + path]).decode("utf-8")
    if args.keep:
        text = keep_hunks(old, text, [unescape(marker) for marker in args.keep])
    for (start, end) in args.head:
        start, end = unescape(start), unescape(end)
        i, j = region(text, start, end, "working file")
        a, b = region(old, start, end, "HEAD")
        text = text[:i] + old[a:b] + text[j:]
    for (start, end) in args.drop:
        start, end = unescape(start), unescape(end)
        i, j = region(text, start, end, "working file")
        text = text[:i] + text[j:]
    data = text.encode("utf-8")
    # <!-- custom: The dry run diffs in Python: the first version passed git diff a blob it had only hashed, not written, and this blobless clone then asked the remote for it ("not our ref"). (Claude code Opus 5.5) -->
    if args.dry_run:
        sys.stdout.write("".join(difflib.unified_diff(old.splitlines(True), text.splitlines(True), "HEAD:" + path, "staged:" + path)))
        return 0
    blob = git(root, ["hash-object", "-w", "--stdin"], data).decode().strip()
    mode = git(root, ["ls-files", "-s", "--", path]).decode().split(" ")[0] or "100644"
    git(root, ["update-index", "--cacheinfo", "%s,%s,%s" % (mode, blob, path)])
    print("staged %s (%s); the working file is unchanged" % (path, blob[:10]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
