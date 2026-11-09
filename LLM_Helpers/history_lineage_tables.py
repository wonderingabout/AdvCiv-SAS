#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Standard library only: argparse for options, collections and re to tally authors and model credits. (Claude code Opus 5.5) -->
from __future__ import annotations

import argparse
import collections
import re
# <!-- custom: subprocess reads Git and pathlib reads the corpus and the guide. (Claude code Opus 5.5) -->
import subprocess
from pathlib import Path


# <!-- custom: Caution: tracing each model's contribution is hazy, so the model tables are only a general indication and the real picture may be quite different.
# Credits can be reworded, moved or omitted, which can bring retired models back; names are inconsistent, with typos, "Claude AI" versus "Claude code", and a question mark where a model was unsure. (Claude code Opus 5.5) -->
DOC = "_1_AdvCiv-SAS/Docs/Source_Analysis/README.md"
# <!-- custom: Generated logs, published changelogs and example captures repeat model names without being mentions by anyone. (Claude code Opus 5.5) -->
DOC_MENTION_SKIP = ("git_logs/", "changelogs_web/", "examples/", "AGENTS.md")
COMMIT_DIFFS = "LLM_Helpers/context/commit_diffs"
SVN_INDEX = "LLM_Helpers/context/svn_history/bbai/INDEX.txt"
NAMES = {"KMod": "K-Mod", "AdvCivPreSAS": "AdvCiv before the SAS fork", "SASBranch": "AdvCiv-SAS branch"}
NOTES = {"KMod": "Last commit in this history", "AdvCivPreSAS": "Ends at the SAS fork"}
OTHER_ACCOUNT = {"codingnewcode": "wonderingabout's other account"}
CREDIT_TAIL = re.compile(r"\(([^()]*(?:\([^()]*\)[^()]*)?)\)\s*-->")
CREDIT_TOKEN = re.compile(r"claude(?P<cp>[ -]code|[ -]ai)?[ -](?P<cf>opus|sonnet|haiku)[ -](?P<cv>\d(?:\.\d)?)|(?P<cg>chat[ -]?gpt|chagpt|catgpt|chtagpt|chatcpt|chatgp)(?:[- ]?(?P<cgv>o-?3|3-o|4-o|\d(?:\.\d)?o?))?(?:[- ]?(?P<cgs>sol))?(?:[- ]?(?P<cgt>thinking))?|(?<![a-z-])gpt[- ]?(?P<gv>\d(?:\.\d)?)(?:[- ]?(?P<gs>codex|sol|thinking))?|\b(?P<gem>gemini)(?:[- ](?P<gemv>\d(?:\.\d)?))?(?:[- ](?P<gemk>pro|flash))?\b|\b(?P<other>deepseek|grok|kimi|copilot|antigravity)\b|(?<![\w.-])(?P<bare>o-?3|3-o|4-?o)(?![\w-])|\b(?P<cc>claude[ -]code)\b|\b(?P<ca>claude[ -]?ai)\b|\b(?P<c>claude)\b|\b(?P<x>codex)\b|(?<![a-z-])(?P<g>gpt)\b", re.I)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Regenerate the History lineage tables of the Source Analysis guide from Git, commit_diffs and the SVN history export.")
    parser.add_argument("--upstream-ref", default="upstream/1.14", help="Fetched AdvCiv ref used to separate upstream commits from SAS work")
    parser.add_argument("--write", action="store_true", help="Replace the tables in the guide. Without it, print them.")
    return parser.parse_args()


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, encoding="utf-8", errors="replace").stdout


def load_segments() -> dict[str, list[dict[str, str]]]:
    # <!-- custom: Rows are kept in git log order, newest first, because dates alone cannot order commits made on the same day. (Claude code Opus 5.5) -->
    commits = {}
    for position, line in enumerate(git("log", "--format=%H%x09%an%x09%ad%x09%s", "--date=short", "HEAD").splitlines()):
        full, author, date, title = line.split("\t", 3)
        commits[full[:10]] = {"sha": full[:9], "author": author, "date": date, "title": title, "position": position}
    segments = collections.defaultdict(list)
    for line in Path(COMMIT_DIFFS, "INDEX.txt").read_text(encoding="utf-8").splitlines():
        fields = line.split("\t")
        if not line.startswith("#") and len(fields) >= 3:
            segments[fields[0]].append(commits[fields[2]])
    return {name: sorted(rows, key=lambda row: row["position"], reverse=True) for name, rows in segments.items()}


def load_svn() -> list[dict[str, str]]:
    rows = []
    for line in Path(SVN_INDEX).read_text(encoding="utf-8").splitlines():
        if not line.startswith("#"):
            fields = line.split("\t")
            rows.append({"sha": "r" + fields[0], "author": fields[2], "date": fields[1][:10]})
    return rows


def cell(row: dict[str, str], ongoing: bool = False) -> str:
    identifier = row["sha"] if row["sha"].startswith("r") else f"`{row['sha']}`"
    return f"{row['date']} ({identifier})" + (" (ongoing)" if ongoing else "")


def project_table(segments: dict[str, list[dict[str, str]]], svn: list[dict[str, str]], upstream_ref: str) -> list[str]:
    upstream = {sha[:9] for sha in git("rev-list", upstream_ref).split()}
    merged = [row for row in segments["SASBranch"] if row["sha"] in upstream]
    unmerged = int(git("rev-list", "--count", f"HEAD..{upstream_ref}"))
    tip = git("log", "-1", "--format=%h %ad", "--date=short", "--abbrev=9", upstream_ref).split()
    rows = ["| Project | Searchable in | Commits | First | Last | Notes |", "| --- | --- | --- | --- | --- | --- |"]
    rows.append(f"| Better BTS AI, with its Firaxis SDK drops | `svn_history/bbai/` | {len(svn)} | {cell(svn[0])} | {cell(svn[-1])} | Frozen; a text copy, not joined to our Git ancestry |")
    for name in ("KMod", "AdvCivPreSAS", "SASBranch"):
        data = segments[name]
        note = NOTES.get(name, f"Includes the {len(merged)} upstream AdvCiv commits of the next row")
        rows.append(f"| {NAMES[name]} | `commit_diffs/`, segment `{name}` | {len(data)} | {cell(data[0])} | {cell(data[-1], name == 'SASBranch')} | {note} |")
    authors = sorted({row["author"] for row in merged})
    rows.append(f"| AdvCiv upstream after the SAS fork | Merged into `SASBranch` | {len(merged)}, counted in `SASBranch` | {cell(merged[0])} | {cell(merged[-1], True)} | All by {', '.join(authors)}; fetched `{upstream_ref}` (`{tip[0]}`, {tip[1]}) has {unmerged} more commits not merged here |")
    return rows


def author_rows(project: str, data: list[dict[str, str]], upstream: set[str]) -> list[str]:
    by_author = collections.defaultdict(list)
    for row in data:
        by_author[row["author"]].append(row)
    rows = []
    for author, commits in sorted(by_author.items(), key=lambda item: item[1][0]["date"]):
        label = author
        if author in OTHER_ACCOUNT:
            label += f" ({OTHER_ACCOUNT[author]})"
        is_upstream = project == NAMES["SASBranch"] and all(commit["sha"][:9] in upstream for commit in commits)
        if is_upstream:
            label += " (upstream AdvCiv commits merged in, not SAS work)"
        ongoing = project == NAMES["SASBranch"] and (is_upstream or author == "wonderingabout")
        rows.append(f"| {project} | {label} | {len(commits)} | {cell(commits[0])} | {cell(commits[-1], ongoing)} |")
    return rows


def author_table(segments: dict[str, list[dict[str, str]]], svn: list[dict[str, str]], upstream_ref: str) -> list[str]:
    upstream = {sha[:9] for sha in git("rev-list", upstream_ref).split()}
    rows = ["| Project | Author | Commits | First | Last |", "| --- | --- | --- | --- | --- |"]
    rows += author_rows("Better BTS AI", svn, upstream)
    for name in ("KMod", "AdvCivPreSAS", "SASBranch"):
        rows += author_rows(NAMES[name], segments[name], upstream)
    return rows


def title_table(segments: dict[str, list[dict[str, str]]]) -> list[str]:
    # <!-- custom: Same labels as the credit table, so both tables can be read per model. (Claude code Opus 5.5) -->
    named = collections.defaultdict(list)
    for row in segments["SASBranch"]:
        for label in {credit_label(match) for match in CREDIT_TOKEN.finditer(row["title"])}:
            named[label].append(row)
    rows = ["| Model, as named in titles | Commit titles | First | Last |", "| --- | --- | --- | --- |"]
    for label in sorted(named, key=lambda name: (named[name][0]["date"], name)):
        rows.append(f"| {label} | {len(named[label])} | {cell(named[label][0])} | {cell(named[label][-1])} |")
    return rows


def chatgpt_version(raw: str) -> str:
    # <!-- custom: Spellings come from a fuzzy scan of the real history: "chatgpt 3-o" and "o-3" are o3, and CREDIT_TOKEN lists only misspellings that occur, such as chagpt and chtagpt. (Claude code Opus 5.5) -->
    return {"o-3": "o3", "3-o": "o3", "4-o": "4o"}.get(raw.lower(), raw.lower())


def credit_label(match: re.Match) -> str:
    if match["cf"]:
        prefix = {"code": " code", "ai": " AI", "": ""}[(match["cp"] or "").strip(" -").lower()]
        return f"Claude{prefix} {match['cf'].capitalize()} {match['cv']}"
    if match["bare"]:
        return f"ChatGPT-{chatgpt_version(match['bare'])}"
    if match["cg"]:
        return "ChatGPT" + (f"-{chatgpt_version(match['cgv'])}" if match["cgv"] else "") + ("-Sol" if match["cgs"] else "") + (" Thinking" if match["cgt"] else "")
    if match["gv"]:
        return f"GPT-{match['gv']}" + {"codex": "-Codex", "sol": "-Sol", "thinking": " Thinking", "": ""}[(match["gs"] or "").lower()]
    if match["gem"]:
        return "Gemini" + (f" {match['gemv']}" if match["gemv"] else "") + (f" {match['gemk'].capitalize()}" if match["gemk"] else "")
    if match["other"]:
        return {"deepseek": "DeepSeek", "grok": "Grok", "kimi": "Kimi", "copilot": "Copilot", "antigravity": "Antigravity"}[match["other"].lower()]
    for group, label in (("cc", "Claude code, no model"), ("ca", "Claude AI, no model"), ("c", "Claude, no model"), ("x", "Codex, no model")):
        if match[group]:
            return label
    return "GPT, no version"


def credit_table(segments: dict[str, list[dict[str, str]]]) -> list[str]:
    # <!-- custom: Added comment lines only, and not Markdown or logs, whose examples quote credits without being credited work. (Claude code Opus 5.5) -->
    # <!-- custom: A credit is re-added whenever a comment is moved or reworded, which made GPT-5.2-Codex look active in November 2026.
    # So the last date needs a commit adding more lines ending in that credit than it removes; a same-commit move or rewrite nets to zero.
    # Only the last-named model counts, because credits are appended: a new comment keeping "GPT-5.2-Codex + ChatGPT-5.6-Sol" is ChatGPT-5.6-Sol's work.
    # Test fixtures are skipped: the 2026-10-10 reflow commit's fixtures quote "(GPT-5.3-Codex) -->" as sample text, which wrongly showed that retired model as active. (Claude code Opus 5.5) -->
    credited = collections.defaultdict(dict)
    net_new = collections.defaultdict(dict)
    lines = collections.Counter()
    inline = collections.Counter()
    inline_rows = collections.defaultdict(list)
    doc_mentions = collections.Counter()
    doc_rows = collections.defaultdict(list)
    by_short_sha = {row["sha"]: row for row in segments["SASBranch"]}
    for path in Path(COMMIT_DIFFS).glob("SASBranch_*.diff"):
        row = by_short_sha[path.stem.rsplit("_", 1)[1][:9]]
        current = ""
        net = collections.Counter()
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("diff --git"):
                current = line.split(" b/")[-1].strip()
            if line.startswith("+") and not line.startswith("+++") and current.endswith((".md", ".txt")) and not any(part in current for part in DOC_MENTION_SKIP):
                for label in {credit_label(match) for match in CREDIT_TOKEN.finditer(line)}:
                    doc_mentions[label] += 1
                    doc_rows[label].append(row)
            if line[:1] not in ("+", "-") or line.startswith(("+++", "---")) or current.endswith((".md", ".txt", ".diff", ".log")) or ("-->" not in line and "custom:" not in line):
                continue
            tails = list(CREDIT_TAIL.finditer(line))
            # <!-- custom: Older comments often name a model in the prose, such as "advised by chatgpt 5", without a closing credit, which left ChatGPT-5.1 with no row.
            # Keep these apart from formal credits, because a mention can also merely refer to a model. (Claude code Opus 5.5) -->
            if line[0] == "+" and "tests/" not in current:
                for label in {credit_label(match) for match in CREDIT_TOKEN.finditer(line[:tails[-1].start()] if tails else line)}:
                    inline[label] += 1
                    inline_rows[label].append(row)
            if not tails:
                continue
            tokens = list(CREDIT_TOKEN.finditer(tails[-1].group(1)))
            if not tokens:
                continue
            if "tests/" not in current:
                net[credit_label(tokens[-1])] += 1 if line[0] == "+" else -1
            if line[0] == "+":
                for label in {credit_label(token) for token in tokens}:
                    credited[label][row["sha"]] = row
                    lines[label] += 1
        for label, amount in net.items():
            if amount > 0:
                net_new[label][row["sha"]] = row
    rows = ["| Model, as credited | First credit | Last new credit | Commits | Credited lines | Inline mentions | Doc mentions |", "| --- | --- | --- | --- | --- | --- | --- |"]
    first = {label: max([*credited[label].values(), *inline_rows[label], *doc_rows[label]], key=lambda row: row["position"]) for label in {*credited, *inline_rows, *doc_rows}}
    for label in sorted(first, key=lambda name: (first[name]["date"], -first[name]["position"], name)):
        last = cell(min(net_new[label].values(), key=lambda row: row["position"])) if net_new[label] else "-"
        rows.append(f"| {label} | {cell(first[label])} | {last} | {len(credited[label])} | {lines[label]} | {inline[label]} | {doc_mentions[label]} |")
    return rows


def replace_table(lines: list[str], table: list[str]) -> None:
    # <!-- custom: Find each table by its first two header cells, so prose and the hand-written base-game table stay untouched. (Claude code Opus 5.5) -->
    prefix = "|".join(table[0].split("|")[:3])
    start = next(index for index, line in enumerate(lines) if line.startswith(prefix))
    end = start
    while lines[end].startswith("|"):
        end += 1
    lines[start:end] = table


def main() -> int:
    args = parse_args()
    segments = load_segments()
    svn = load_svn()
    tables = [project_table(segments, svn, args.upstream_ref), author_table(segments, svn, args.upstream_ref), title_table(segments), credit_table(segments)]
    if not args.write:
        print("\n\n".join("\n".join(table) for table in tables))
        return 0
    raw = Path(DOC).read_bytes()
    lines = raw.decode("utf-8").replace("\r\n", "\n").split("\n")
    for table in tables:
        replace_table(lines, table)
    text = "\n".join(lines)
    Path(DOC).write_bytes((text.replace("\n", "\r\n") if b"\r\n" in raw else text).encode("utf-8"))
    print(f"Updated {DOC}; the commit corpus ends at {segments['SASBranch'][-1]['sha']} ({segments['SASBranch'][-1]['date']}). Update the as-of date in its prose if it moved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
