# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Share literal-aware blank-line detection and diff ancestry between source provenance and supplementary text hygiene; deleting a block can join separators without adding any lines. (GPT-6.1-Sol) -->

# <!-- custom: difflib traces existing blank rows, re recognizes structured text regions, and tokenize/StringIO preserve Python strings without requiring engine imports or a runtime parser. (GPT-6.1-Sol) -->
import difflib
from io import StringIO
import re
import tokenize

CPP_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl", ".rc"}
PY_SUFFIXES = {".py"}
XML_SUFFIXES = {".xml"}


# <!-- custom: YAML block scalars, shell/PowerShell here-documents, Makefile define bodies and archived comment payloads can contain meaningful empty rows.
# Preserve these regions rather than treating every textual file as interchangeable prose. (GPT-6.1-Sol) -->
def structured_text_protected_lines(text, suffix):
    protected = set()
    lines = text.splitlines()
    if suffix in {".toml", ".json", ".jsonc", ".ps1", ".sh", ".yml", ".yaml"}:
        pattern = r"'{3}[\s\S]*?'{3}|\"\"\"[\s\S]*?\"\"\"|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'"
        for match in re.finditer(pattern, text):
            protected.update(range(text.count("\n", 0, match.start()) + 1, text.count("\n", 0, match.end()) + 2))
    if suffix in {".yml", ".yaml"}:
        indentation = None
        for index, line in enumerate(lines):
            stripped = line.lstrip()
            width = len(line) - len(stripped)
            if indentation is not None and (not stripped or width > indentation):
                protected.add(index + 1)
                continue
            indentation = None
            if re.search(r"(?:[:\-]\s+)[|>][+\-]?[0-9]*[+\-]?\s*(?:#.*)?$", line):
                indentation = width
    terminator = None
    for index, line in enumerate(lines):
        if terminator is not None:
            protected.add(index + 1)
            if line.strip() == terminator:
                terminator = None
            continue
        if suffix == ".sh":
            match = re.search(r"<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?", line)
            if match:
                terminator = match.group(1)
        elif suffix == ".ps1":
            match = re.search(r"@(['\"])\s*$", line)
            if match:
                terminator = match.group(1) + "@"
        elif suffix == "makefile" and re.match(r"\s*define\s+", line):
            terminator = "endef"
        elif suffix == ".txt" and re.match(r"----- Comment #\d+ -----", line):
            protected.update(range(index + 1, len(lines) + 1))
            break
    return protected


# <!-- custom: The comment checker passed a newly added triple-blank separator because comment reflow and Ruff's blocking gate do not enforce source spacing.
# Protect literal/text regions first; blank rows inside captured examples or multiline strings are data, while ordinary source separators need at most two. (GPT-6.1-Sol) -->
def spacing_protected_lines(text: str, suffix: str) -> set[int] | None:
    protected = set()
    if suffix in PY_SUFFIXES:
        fstrings = []
        try:
            for token in tokenize.generate_tokens(StringIO(text).readline):
                kind = tokenize.tok_name.get(token.type, "")
                if kind == "FSTRING_START":
                    fstrings.append(token.start[0])
                elif kind == "FSTRING_END" and fstrings:
                    protected.update(range(fstrings.pop(), token.end[0] + 1))
                elif token.type == tokenize.STRING:
                    protected.update(range(token.start[0], token.end[0] + 1))
        except (tokenize.TokenError, IndentationError):
            return None
        return protected
    if suffix not in CPP_SUFFIXES | XML_SUFFIXES:
        return structured_text_protected_lines(text, suffix)
    if suffix in CPP_SUFFIXES:
        pattern = r'//[^\n]*|/\*.*?\*/|R"(?P<delimiter>[^\s()\\]{0,16})\(.*?\)(?P=delimiter)"|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
    else:
        pattern = r'<!--.*?-->|<!\[CDATA\[.*?\]\]>|<(?:[^<>"\']|"[^"]*"|\'[^\']*\')*>|[^<]+'
    cursor = 0
    line = 1
    for match in re.finditer(pattern, text, re.S):
        value = match.group()
        line += text.count("\n", cursor, match.start())
        start = line
        line += value.count("\n")
        cursor = match.end()
        # <!-- custom: XML text with non-whitespace content, comments, CDATA and attribute-bearing markup are text regions; whitespace between elements remains eligible for the spacing check. (GPT-6.1-Sol) -->
        if suffix in XML_SUFFIXES and not value.startswith("<") and not value.strip():
            continue
        protected.update(range(start, line + 1))
    return protected


def long_blank_runs(text: str, suffix: str, maximum: int = 2) -> list[tuple[int, int]]:
    # <!-- custom: Skip tokenization when there is no candidate separator, and count regex match lines incrementally above so full-tree previews do not repeatedly scan large XML prefixes. (GPT-6.1-Sol) -->
    if not re.search(rf"(?:^[ \t]*\n){{{maximum + 1}}}", text, re.M):
        return []
    protected = spacing_protected_lines(text, suffix)
    if protected is None:
        return []
    lines = text.splitlines()
    runs = []
    index = 0
    while index < len(lines):
        if lines[index].strip() or index + 1 in protected:
            index += 1
            continue
        start = index
        while index < len(lines) and not lines[index].strip() and index + 1 not in protected:
            index += 1
        if index - start > maximum:
            runs.append((start, index))
    return runs


# <!-- custom: Compare blank-row ancestry rather than only inserted lines: removing code between two short separators can create a new long separator without inserting any blank row.
# Normalize whitespace-only rows for matching so cleaning their trailing spaces or shortening an inherited long run does not require a wider formatting cleanup. (GPT-6.1-Sol) -->
def blank_line_errors(path: str, old_text: str, new_text: str, suffix: str, maximum: int = 2) -> list[str]:
    new_runs = long_blank_runs(new_text, suffix, maximum)
    if not new_runs:
        return []
    old_runs = long_blank_runs(old_text, suffix, maximum)
    old_lines = [line if line.strip() else "" for line in old_text.splitlines()]
    new_lines = [line if line.strip() else "" for line in new_text.splitlines()]
    ancestry = {}
    for tag, old_start, old_end, new_start, new_end in difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False).get_opcodes():
        if tag == "equal":
            ancestry.update((new_start + offset, old_start + offset) for offset in range(new_end - new_start))
    errors = []
    for start, end in new_runs:
        mapped = [ancestry.get(index) for index in range(start, end)]
        inherited = (
            None not in mapped
            and mapped == list(range(mapped[0], mapped[0] + len(mapped)))
            and any(old_start <= mapped[0] and mapped[-1] < old_end for old_start, old_end in old_runs)
        )
        if not inherited:
            errors.append("%s:%d: newly introduced run of %d blank lines; use at most %s outside literal/text regions" % (path, start + 1, end - start, "two" if maximum == 2 else str(maximum)))
    return errors
