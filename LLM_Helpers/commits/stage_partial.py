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
    return codecs.decode(text, "unicode_escape")


def region(text, start, end, label):
    i = text.find(start)
    if i < 0:
        raise SystemExit("%s: start marker not found: %r" % (label, start))
    if text.find(start, i + 1) >= 0:
        raise SystemExit("%s: start marker found more than once: %r" % (label, start))
    j = text.find(end, i + len(start))
    if j < 0:
        raise SystemExit("%s: end marker not found after the start: %r" % (label, end))
    return i, j


def git(root, args, data=None):
    result = subprocess.run(["git"] + args, cwd=root, input=data, capture_output=True)
    if result.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), result.stderr.decode("utf-8", "replace")))
    return result.stdout


def main(argv):
    parser = argparse.ArgumentParser(description="Stage a file with chosen regions taken from HEAD or dropped; the working file is not changed.")
    parser.add_argument("path", help="file to stage, relative to the repository root")
    parser.add_argument("--head", nargs=2, action="append", default=[], metavar=("START", "END"), help="replace the working region from START up to END (END excluded) with HEAD's same region; repeatable")
    parser.add_argument("--drop", nargs=2, action="append", default=[], metavar=("START", "END"), help="leave the region from START up to END (END excluded) out of the staged version; repeatable")
    parser.add_argument("--dry-run", action="store_true", help="print the staged diff against HEAD without staging")
    args = parser.parse_args(argv)
    if not args.head and not args.drop:
        raise SystemExit("give at least one --head or --drop region")
    root = git(".", ["rev-parse", "--show-toplevel"]).decode("utf-8").strip()
    path = args.path.replace("\\", "/")
    text = io.open(os.path.join(root, path), encoding="utf-8", newline="").read()
    old = git(root, ["show", "HEAD:" + path]).decode("utf-8")
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
