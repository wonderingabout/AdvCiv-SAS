#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Build check: active BBAI and SASGameRecord rows keep the shared greppable record format.

# <!-- custom: Path/argparse/re/sys read the DLL sources and report findings; no Civ4 or compiler is needed. (Claude code Opus 5.5) -->
from pathlib import Path
import argparse
import re
import sys

# <!-- custom: After the BBAI modernization, a T201 Huge run still showed older rows indented ("    WORKER_..."), civs logged unnamed after player=%d and repeated keys such as target=%S ... target=(%d,%d).
# One normalization pass fixed 381 formats; this check keeps new rows from reintroducing those shapes. It reads only active code, so disabled rows and the TrueStarts.cpp debug surface stay outside it.
# SASGameRecord already followed the format except one unquoted city row, so both sinks share one check rather than two copies drifting apart. (Claude code Opus 5.5) -->
SOURCE_GLOB = "CvGameCoreDLL/*.cpp"
EXCLUDED = {"TrueStarts.cpp"}
CALL_RE = re.compile(r'\b(logBBAI|logSASGameRecord)\(\s*"((?:[^"\\]|\\.)*)"')
# <!-- custom: The ID is uppercase, or a leading %s that substitutes a stable stage ID (FOUND_SITE_%s, the session-header row). (Claude code Opus 5.5) -->
ID_RE = re.compile(r"^(?:[A-Z][A-Z0-9_]*(?:%s[A-Z0-9_]*)?|%s)(?: |$)")
# <!-- custom: An ID followed by a bare string, e.g. player=%d %S, was the unnamed-civ shape; pre-keyed fragments such as techRows=%d %s stay legal because they use %s. (Claude code Opus 5.5) -->
UNNAMED_AFTER_ID_RE = re.compile(r"=%[-+]?\d*[dD] \(?%S\)?(?= |$)")
# <!-- custom: Every token after the ID must be a key=value field or a pre-keyed %s/%S fragment.
# The rerun showed civ=CIVILIZATION_CHINA stageFlags C1=0 and grouped fields such as rejects(edgeOrIgnored=0 ...), whose bare words and parentheses split into apparent fields. (Claude code Opus 5.5) -->
FIELD_TOKEN_RE = re.compile(r"^(?:[A-Za-z_]\w*=\S*|%[sS])$")
# <!-- custom: Display text such as civ=United States of America broke space-separated parsing in 95% of civ values of that run.
# Following SGR (civType=CIVILIZATION_OTTOMAN, playerName="PC"), identities use narrow %s XML types (civ=CIVILIZATION_AMERICA) and names without a type pass through a quoting helper: getSASDiagnosticQuoted, or a wrapper such as getSASGameRecordQuotedCityName.
# A first pass quoted names in the literal (city=\"%S\"), but that leaves a quote inside a human-renamed city unescaped, so a wide %S field must take a helper's result. (Claude code Opus 5.5) -->
DISPLAY_RE = re.compile(r"(\w+)=(\\\"%S\\\"|'%S'|%S)")
QUOTED_HELPER_RE = re.compile(r"\bget\w*Quoted\w*\(")
# <!-- custom: SGR often passes a name quoted earlier, e.g. kContext.szCityName set from getSASGameRecordQuotedCityName, which the format alone cannot show.
# So only an argument that reads raw display text here (getName(), getDescription(), ...) must carry the helper; this flagged three real unquoted SGR city names. (Claude code Opus 5.5) -->
RAW_TEXT_RE = re.compile(r"\b(?:getName|getDescription|getCivilization\w*Description|getCivilizationAdjective|getText|getProductionName|getReplayName)\(")
PLACEHOLDER_RE = re.compile(r"%[-+ #0]*\d*(?:\.\d+)?(?:hh|h|ll|l|I64)?[diouxXeEfgGcsSp%]")
KEY_RE = re.compile(r"(?:^| )([A-Za-z_]\w*)=")


def call_arguments(code: str, open_paren: int) -> list[str]:
    # <!-- custom: Top-level comma-separated arguments of the call opened at open_paren, skipping strings and nested brackets; the format literal is argument 0. (Claude code Opus 5.5) -->
    args, depth, i, start = [], 0, open_paren, open_paren + 1
    while i < len(code):
        ch = code[i]
        if ch in "\"'":
            j = i + 1
            while j < len(code) and code[j] != ch:
                j += 2 if code[j] == "\\" else 1
            i = j
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                args.append(code[start:i])
                return args
        elif ch == "," and depth == 1:
            args.append(code[start:i])
            start = i + 1
        i += 1
    return args


def active_code(text: str) -> str:
    # <!-- custom: Blank out comments but keep strings and line breaks, so line numbers stay exact and "//" inside a literal is not a comment. (Claude code Opus 5.5) -->
    out = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch in "\"'":
            j = i + 1
            while j < n and text[j] != ch and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1])
            i = j + 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", text[i:j]))
            i = j
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def check_source(name: str, text: str) -> list[str]:
    errors = []
    code = active_code(text.replace("\r\n", "\n"))
    for match in CALL_RE.finditer(code):
        sink, fmt = match.group(1), match.group(2)
        line = code.count("\n", 0, match.start()) + 1
        where = "%s:%d" % (name, line)
        if fmt[:1].isspace():
            errors.append("%s: %s format starts with indentation; begin with the record ID" % (where, sink))
        elif not ID_RE.match(fmt):
            errors.append("%s: %s format does not start with an uppercase record ID: %s" % (where, sink, fmt[:60]))
        else:
            loose = [token for token in fmt.split(" ")[1:] if token and not FIELD_TOKEN_RE.match(token)]
            if loose:
                errors.append("%s: token(s) %s are not key=value fields; name or flatten them, e.g. rejectUnowned=%%d instead of rejects(unowned=%%d" % (where, ", ".join(loose[:3])))
        if UNNAMED_AFTER_ID_RE.search(fmt):
            errors.append("%s: unnamed string after an ID field (e.g. player=%%d %%S); name it, e.g. civ=%%s with the XML type" % where)
        args = call_arguments(code, code.index("(", match.start()))
        holders = [m for m in PLACEHOLDER_RE.finditer(fmt) if m.group(0) != "%%"]
        for display in DISPLAY_RE.finditer(fmt):
            if display.group(2) != "%S":
                errors.append("%s: %s= quotes display text in the literal; pass getSASDiagnosticQuoted(name).GetCString() to a bare %%S so embedded quotes are escaped" % (where, display.group(1)))
                continue
            index = [k for k, h in enumerate(holders) if h.start() == display.start(2)]
            if len(holders) == len(args) - 1 and index and RAW_TEXT_RE.search(args[index[0] + 1]) and not QUOTED_HELPER_RE.search(args[index[0] + 1]):
                errors.append("%s: %s=%%S display text is not passed through getSASDiagnosticQuoted; quote it, or log the XML type with %%s" % (where, display.group(1)))
        keys = KEY_RE.findall(fmt)
        repeated = sorted({key for key in keys if keys.count(key) > 1})
        if repeated:
            errors.append("%s: repeated key(s) %s; give each field its own name, e.g. targetPlot=" % (where, ", ".join(repeated)))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that active BBAI and SASGameRecord rows keep the shared greppable record format.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    args = parser.parse_args()
    errors = []
    sources = sorted(path for path in args.repo_root.glob(SOURCE_GLOB) if path.name not in EXCLUDED)
    for path in sources:
        text = path.read_bytes().decode("utf-8", "replace")
        errors.extend(check_source(path.relative_to(args.repo_root).as_posix(), text))
    if errors:
        print("FAIL diagnostic record format")
        for error in errors:
            print("  - " + error)
        return 1
    print("PASS diagnostic record format: %d source file(s) checked" % len(sources))
    return 0


if __name__ == "__main__":
    sys.exit(main())
