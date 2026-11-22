# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Share numbered-entry parsing and explanation presence between recorder histories; their different revision/provenance policies remain in their own checkers.
# Regex locates Markdown fields/headings; fenced examples and HTML comments cannot substitute for a real history entry or explanatory text. (GPT-6.1-Sol) -->
import re
# <!-- custom: subprocess reads the PR's newest commit message from Git for the squash-intent rule below; ci_markers holds the marker's one spelling. (Claude code Opus 5.5) -->
import subprocess
from ci_markers import SQUASH_PR


# <!-- custom: Whether a PR is intended to be squash-merged, so its revision checks judge it as the one commit it becomes rather than each of its commits.
# A GitHub label, revision:squash, said so, but the user does not use labels, so PR#50's SGR step failed on the 210, 211, 210 bumps of its draft commits although the squash commit, 209 to 210, passes (2026-11-22).
# The intent now comes from the commit messages, like the other markers: [ci_squash_pr] in the PR's newest commit, which states the intent as it stands; the label is no longer read, so one spelling decides. (Claude code Opus 5.5) -->
# <!-- custom: The tree a squash merge of tip onto target would commit, or None when they conflict; diffing target against it shows what the squash commit really changes.
# Codex's review (2026-11-22) found the merge-base diff blocking a valid squash: an entry already on main read as new to the PR, so a check demanded 3+ where the squash left it untouched. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
def squash_tree(repo, target, tip):
    result = subprocess.run(["git", "merge-tree", "--write-tree", target, tip], cwd=repo, capture_output=True, text=True)
    return result.stdout.split("\n", 1)[0].strip() if result.returncode == 0 else None


def pull_request_squashes(repo, pull):
    tip = pull.get("head", {}).get("sha")
    if not tip:
        return False
    return SQUASH_PR in subprocess.check_output(["git", "log", "-1", "--format=%B", tip], cwd=repo, text=True)


def revision_entries(text):
    visible = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence is not None:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}[ \t]*", line):
                fence = None
            continue
        if marker:
            fence = marker.group(1)
            continue
        visible.append(line)
    text = re.sub(r"<!--.*?-->", "", "\n".join(visible), flags=re.DOTALL)
    headings = list(re.finditer(r"^#{1,3}[ \t]+[^\n]+$", text, re.MULTILINE))
    result = []
    for index, heading in enumerate(headings):
        number = re.match(r"### Revision (\d+)\b", heading.group())
        if number:
            end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            result.append((int(number.group(1)), text[heading.end():end]))
    return result


# <!-- custom: A matching revision heading with only Date/Git commit fields previously passed.
# Require actual Change text, allowing continued paragraphs/sub-bullets without minimum length or subjective writing rules; an optional revision selects the entry belonging to one committed bump. (GPT-6.1-Sol) -->
def change_errors(text, revision=None):
    entries = revision_entries(text)
    if revision is not None:
        entries = [(number, body) for number, body in entries if number == revision]
        if not entries:
            return [f"revision {revision}: missing corresponding history entry"]
    errors = []
    for number, body in entries:
        change = re.search(r"^- \*\*Change:\*\*[ \t]*(.*?)(?=^- \*\*[^*\n]+:\*\*|\Z)", body, re.MULTILINE | re.DOTALL)
        if change is None or not change.group(1).strip(" \t\r\n-*+_`"):
            errors.append(f"revision {number}: missing nonempty Change explanation")
    return errors
