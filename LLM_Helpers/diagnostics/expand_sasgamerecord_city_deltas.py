#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# Expand revision-123+ bounded SASGameRecord city-detail deltas back to full rows.
#
# The log is treated byte-preservingly through latin-1 because Civ4 diagnostics can contain
# legacy ANSI bytes. Unrelated rows are copied unchanged. Delta chains are validated against
# their explicit previousTurn/fullBaseTurn metadata and fail closed if an excerpt is missing
# its required base/link.

from __future__ import annotations

import argparse
from pathlib import Path
import sys


BASE_TYPES = {
    "GAME_RECORD_CITY",
    "GAME_RECORD_CITY_DEVELOPMENT",
    "GAME_RECORD_CITY_HAPPINESS",
    "GAME_RECORD_CITY_HEALTH",
    "GAME_RECORD_CITY_BUILDINGS",
}
DELTA_SUFFIX = "_DELTA"
DECORATION_FIELDS = {"seq", "tx"}
DELTA_META_FIELDS = {"previousTurn", "fullBaseTurn", "changed"}
IDENTITY_FIELDS = {"turn", "player", "cityId"}


def parse_fields(line: str) -> tuple[str, list[tuple[str, str]]]:
    type_end = line.find(" ")
    if type_end < 0:
        return line, []
    row_type = line[:type_end]
    fields: list[tuple[str, str]] = []
    pos = type_end + 1
    while pos < len(line):
        while pos < len(line) and line[pos] == " ":
            pos += 1
        if pos >= len(line):
            break
        start = pos
        equals = line.find("=", start)
        if equals < 0:
            raise ValueError(f"malformed field after {row_type}: {line[start:start + 80]!r}")
        end = equals + 1
        if end < len(line) and line[end] == '"':
            end += 1
            escaped = False
            while end < len(line):
                char = line[end]
                if escaped:
                    escaped = False
                    end += 1
                    continue
                if char == "\\":
                    escaped = True
                    end += 1
                    continue
                if char == '"':
                    end += 1
                    break
                end += 1
        else:
            next_space = line.find(" ", end)
            end = len(line) if next_space < 0 else next_space
        token = line[start:end]
        fields.append((line[start:equals], token))
        pos = end
    return row_type, fields


def field_value(fields: list[tuple[str, str]], name: str) -> str | None:
    for field_name, token in fields:
        if field_name == name:
            return token.split("=", 1)[1]
    return None


def require_value(fields: list[tuple[str, str]], name: str, row_type: str) -> str:
    value = field_value(fields, name)
    if value is None:
        raise ValueError(f"{row_type}: missing required {name}= field")
    return value


def write_line(output, text: str, ending: bytes) -> None:
    output.write(text.encode("latin-1") + ending)


def expand(input_path: Path, output_path: Path) -> tuple[int, int]:
    states: dict[tuple[str, str, str], dict[str, object]] = {}
    delta_rows = 0
    full_rows = 0
    with input_path.open("rb") as source, output_path.open("wb") as output:
        for line_number, raw in enumerate(source, 1):
            if raw.endswith(b"\r\n"):
                body, ending = raw[:-2], b"\r\n"
            elif raw.endswith(b"\n"):
                body, ending = raw[:-1], b"\n"
            else:
                body, ending = raw, b""
            line = body.decode("latin-1")
            row_type = line.split(" ", 1)[0]
            is_delta = row_type.endswith(DELTA_SUFFIX) and row_type[:-len(DELTA_SUFFIX)] in BASE_TYPES
            is_full = row_type in BASE_TYPES
            if not is_delta and not is_full:
                output.write(raw)
                continue
            try:
                parsed_type, fields = parse_fields(line)
                player = require_value(fields, "player", parsed_type)
                city_id = require_value(fields, "cityId", parsed_type)
                turn = int(require_value(fields, "turn", parsed_type))
                if is_full:
                    state_fields = [(name, token) for name, token in fields if name not in DECORATION_FIELDS]
                    states[(parsed_type, player, city_id)] = {
                        "fields": state_fields,
                        "turn": turn,
                        "full_base_turn": turn,
                    }
                    full_rows += 1
                    output.write(raw)
                    continue

                base_type = parsed_type[:-len(DELTA_SUFFIX)]
                key = (base_type, player, city_id)
                if key not in states:
                    raise ValueError(f"missing full/base row for {base_type} player={player} cityId={city_id}")
                state = states[key]
                previous_turn = int(require_value(fields, "previousTurn", parsed_type))
                full_base_turn = int(require_value(fields, "fullBaseTurn", parsed_type))
                if previous_turn != state["turn"]:
                    raise ValueError(f"previousTurn={previous_turn} but reconstructed previous turn is {state['turn']}")
                if full_base_turn != state["full_base_turn"]:
                    raise ValueError(f"fullBaseTurn={full_base_turn} but active full base is {state['full_base_turn']}")

                decorations = [(name, token) for name, token in fields if name in DECORATION_FIELDS]
                changes = {
                    name: token for name, token in fields
                    if name not in DECORATION_FIELDS | IDENTITY_FIELDS | DELTA_META_FIELDS
                }
                changed_declared = int(require_value(fields, "changed", parsed_type))
                if changed_declared != len(changes):
                    raise ValueError(f"changed={changed_declared} but row carries {len(changes)} changed payload fields")

                rebuilt: list[tuple[str, str]] = []
                seen_changes: set[str] = set()
                for name, token in state["fields"]:
                    if name == "turn":
                        token = f"turn={turn}"
                    elif name == "player":
                        token = f"player={player}"
                    elif name == "cityId":
                        token = f"cityId={city_id}"
                    elif name in changes:
                        token = changes[name]
                        seen_changes.add(name)
                    rebuilt.append((name, token))
                unknown_changes = sorted(set(changes) - seen_changes)
                if unknown_changes:
                    raise ValueError(f"delta contains field(s) absent from active full schema: {', '.join(unknown_changes)}")

                state["fields"] = rebuilt
                state["turn"] = turn
                tokens = [token for _, token in decorations] + [token for _, token in rebuilt]
                write_line(output, base_type + (" " + " ".join(tokens) if tokens else ""), ending)
                delta_rows += 1
            except Exception as exc:
                raise ValueError(f"line {line_number}: {exc}") from exc
    return full_rows, delta_rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Expand bounded SASGameRecord city *_DELTA rows into ordinary full city-detail rows.")
    parser.add_argument("input", type=Path, help="SASGameRecord_*.log to expand")
    parser.add_argument("output", type=Path, help="destination expanded .log")
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error("input and output must be different files")
    try:
        full_rows, delta_rows = expand(args.input, args.output)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Expanded {delta_rows} city delta rows; observed {full_rows} full city-detail checkpoints -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
