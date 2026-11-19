#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
"""Validate and normalize Civ4 BtS T0 WorldBuilder saves for AdvCiv-SAS.

This is deliberately a text-world bridge, not a binary CivBeyondSwordSave parser.
The intended migration path is:

1. Load an old T0 binary save with the matching historical game/DLL/XML.
2. Export a .CivBeyondSwordWBSave from that source build.
3. Run this helper against the destination AdvCiv-SAS XML.
4. Load the validated WBSave with the destination build and save normally.

The historical game therefore decodes its own binary format, while this helper
operates on logical XML type names and produces an auditable conversion report.
"""

# <!-- custom: Future annotations keep the helper usable with modern typing while argparse drives the CLI, collections builds inventories, hashlib fingerprints artifacts, and json records explicit mappings and reports. (ChatGPT-5.6-Sol) -->
from __future__ import annotations

import argparse
import collections
import hashlib
import json
# <!-- custom: pathlib provides filesystem paths, re parses the stable text grammar, sys provides CLI status/error handling, and typing documents the validator data flow. (ChatGPT-5.6-Sol) -->
from pathlib import Path
import re
import sys
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple

WB_ENCODING = "latin-1"
REPORT_FORMAT_VERSION = 1
SUPPORTED_WB_VERSION = 11

# <!-- custom: Limit symbolic validation to WB keys whose values are Civ4 XML type names; ordinary names, descriptions and script data must remain opaque text. (ChatGPT-5.6-Sol) -->
XML_TYPE_KEYS = {
    "Era",
    "Speed",
    "Calendar",
    "Option",
    "MPOption",
    "ForceControl",
    "Victory",
    "Tech",
    "ProjectType",
    "LeaderType",
    "CivType",
    "Handicap",
    "Color",
    "ArtStyle",
    "StateReligion",
    "StartingEra",
    "CivicOption",
    "Civic",
    "UnitType",
    "LeaderUnitType",
    "PromotionType",
    "UnitAIType",
    "ProductionUnit",
    "ProductionBuilding",
    "ProductionProject",
    "ProductionProcess",
    "BuildingType",
    "ReligionType",
    "HolyCityReligionType",
    "CorporationType",
    "HeadquarterCorporationType",
    "FreeSpecialistType",
    "BonusType",
    "ImprovementType",
    "FeatureType",
    "RouteType",
    "TerrainType",
    "world size",
    "climate",
    "sealevel",
}

# <!-- custom: Treat the WB empty/NONE sentinels as valid values rather than unresolved XML identities. (ChatGPT-5.6-Sol) -->
TYPE_SENTINELS = {"", "NONE"}

# <!-- custom: Player blocks name their leader and civilization texts by key, such as LeaderName=TXT_KEY_LEADER_MOCTEZUMA. The 4986 transplant passed validation with that retired key, and the current game then showed the raw key as the Aztec leader's name.
# So a TXT_KEY_ value under these keys is checked against the destination's <Tag> definitions and remapped like a type; a plain name such as "PC" stays as it is. (Claude code Fable 5.2) -->
TEXT_KEY_KEYS = {"LeaderName", "CivDesc", "CivShortDesc", "CivAdjective"}
TEXT_TAG_RE = re.compile(r"<Tag>\s*([^<]+?)\s*</Tag>", re.IGNORECASE)


def is_checked_value(key: str, value: str) -> bool:
    if key in XML_TYPE_KEYS:
        return value not in TYPE_SENTINELS
    return key in TEXT_KEY_KEYS and value.startswith("TXT_KEY_")

BEGIN_RE = re.compile(r"^\s*Begin([A-Za-z0-9_]+)\s*$")
END_RE = re.compile(r"^\s*End([A-Za-z0-9_]+)\s*$")
TOKEN_RE = re.compile(r"(?P<prefix>(?:^|,\s*)(?P<key>[^=,]+?)\s*=\s*)(?P<value>[^,\r\n]*)")
XML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
TYPE_TAG_RE = re.compile(r"<Type>\s*([^<]+?)\s*</Type>", re.IGNORECASE)


class WBError(Exception):
    """A source WBSave is not safe to transplant automatically."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_wb(path: Path) -> Tuple[bytes, str, str]:
    data = path.read_bytes()
    try:
        text = data.decode(WB_ENCODING)
    except UnicodeDecodeError as exc:
        # <!-- custom: Latin-1 is total, but retain an explicit defensive error path so a future encoding change fails with a transplant-specific diagnostic. (ChatGPT-5.6-Sol) -->
        raise WBError("could not decode WorldBuilder save as Latin-1: %s" % exc)
    newline = "\r\n" if b"\r\n" in data else "\n"
    return data, text, newline


def split_tokens(line: str) -> List[Tuple[str, str]]:
    """Return Civ4-style comma-separated key/value tokens from one line."""
    result = []
    for match in TOKEN_RE.finditer(line):
        result.append((match.group("key").strip(), match.group("value").strip()))
    return result


def first_value(lines: Iterable[str], key: str) -> Optional[str]:
    for line in lines:
        for token_key, token_value in split_tokens(line):
            if token_key == key:
                return token_value
    return None


def int_value(value: Optional[str], label: str, errors: List[str]) -> Optional[int]:
    if value is None:
        errors.append("missing required %s" % label)
        return None
    try:
        return int(value)
    except ValueError:
        errors.append("invalid integer for %s: %r" % (label, value))
        return None


def scan_structure(lines: Sequence[str]) -> Tuple[collections.Counter, List[str]]:
    counts = collections.Counter()
    stack: List[str] = []
    errors: List[str] = []
    for line_number, line in enumerate(lines, 1):
        stripped = line.rstrip("\r\n")
        begin = BEGIN_RE.match(stripped)
        if begin:
            name = begin.group(1)
            counts[name] += 1
            stack.append(name)
            continue
        end = END_RE.match(stripped)
        if end:
            name = end.group(1)
            if not stack:
                errors.append("line %d: End%s without matching Begin%s" % (line_number, name, name))
            elif stack[-1] != name:
                errors.append("line %d: End%s closes Begin%s" % (line_number, name, stack[-1]))
                if name in stack:
                    while stack and stack[-1] != name:
                        stack.pop()
                    if stack:
                        stack.pop()
            else:
                stack.pop()
    if stack:
        errors.append("unclosed WB sections: %s" % ", ".join(stack))
    return counts, errors


def block_lines(lines: Sequence[str], block_name: str) -> List[List[str]]:
    """Return lines inside each named block; nested blocks remain included."""
    result: List[List[str]] = []
    current: Optional[List[str]] = None
    depth = 0
    for line in lines:
        stripped = line.rstrip("\r\n")
        begin = BEGIN_RE.match(stripped)
        end = END_RE.match(stripped)
        if begin and begin.group(1) == block_name:
            if current is None:
                current = []
                depth = 1
                continue
            depth += 1
        if current is not None:
            if end and end.group(1) == block_name:
                depth -= 1
                if depth == 0:
                    result.append(current)
                    current = None
                    continue
            current.append(line)
    return result


def load_destination_types(xml_roots: Sequence[Path]) -> Tuple[set, Dict[str, int], List[str]]:
    """Collect identities from the effective destination XML overlay.

    Pass XML roots from lowest to highest precedence (for example base game,
    Warlords, BtS, then the mod). A later file with the same relative path
    replaces the earlier file, matching Civ4's mod override model.
    """
    warnings: List[str] = []
    active_files: Dict[str, Tuple[Path, Path]] = {}
    seen_roots = set()
    normalized_roots: List[Path] = []
    for root in xml_roots:
        xml_root = root.resolve()
        if xml_root in seen_roots:
            continue
        seen_roots.add(xml_root)
        normalized_roots.append(xml_root)
        xml_paths = sorted(p for p in xml_root.rglob("*.xml") if p.is_file())
        if not xml_paths:
            raise WBError("destination XML root contains no .xml files: %s" % xml_root)
        for path in xml_paths:
            relative = path.relative_to(xml_root).as_posix().lower()
            active_files[relative] = (xml_root, path)

    symbols = set()
    per_root: Dict[str, int] = {str(root): 0 for root in normalized_roots}
    for _relative, (root, path) in sorted(active_files.items()):
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")
        # <!-- custom: Strip XML comments before collecting <Type> values so disabled/historical definitions cannot satisfy destination-identity validation accidentally. (ChatGPT-5.6-Sol) -->
        text = XML_COMMENT_RE.sub("", text)
        before = len(symbols)
        symbols.update(m.group(1).strip() for m in TYPE_TAG_RE.finditer(text))
        # <!-- custom: The first real run, on a 4986 save, reported ARTSTYLE_ASIAN, ARTSTYLE_EUROPEAN, ARTSTYLE_MIDDLE_EAST and ARTSTYLE_SOUTH_AMERICA as missing from the current XML, although the game has them: GlobalTypes.xml defines such engine types as <ArtStyleType>ARTSTYLE_ASIAN</ArtStyleType>, with no <Type> tag.
        # So every element of that file counts as a definition. (Claude code Fable 5.2) -->
        symbols.update(m.group(1).strip() for m in TEXT_TAG_RE.finditer(text))
        if path.name.lower() == "globaltypes.xml":
            symbols.update(m.group(1) for m in re.finditer(r">\s*([A-Z][A-Z0-9_]+)\s*<", text))
        per_root[str(root)] += len(symbols) - before
    if not symbols:
        warnings.append("no symbolic XML identities were discovered under destination XML roots")
    return symbols, per_root, warnings


def load_mapping(path: Optional[Path]) -> Dict[str, str]:
    if path is None:
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise WBError("could not read mapping JSON %s: %s" % (path, exc))
    if isinstance(payload, dict) and "types" in payload:
        payload = payload["types"]
    if not isinstance(payload, dict):
        raise WBError("mapping JSON must be an object or contain a 'types' object")
    result: Dict[str, str] = {}
    for old, new in payload.items():
        if not isinstance(old, str) or not isinstance(new, str) or not old or not new:
            raise WBError("type mappings must be non-empty string -> string pairs")
        result[old] = new
    return result


def replace_type_values(line: str, mapping: Mapping[str, str], remapped: MutableMapping[str, int]) -> str:
    if not mapping or "=" not in line:
        return line

    def repl(match: re.Match) -> str:
        key = match.group("key").strip()
        value = match.group("value").strip()
        if not is_checked_value(key, value) or value not in mapping:
            return match.group(0)
        new_value = mapping[value]
        remapped["%s -> %s" % (value, new_value)] += 1
        prefix = match.group("prefix")
        # <!-- custom: Preserve value-field spacing so an explicit type remap changes only the symbolic identity, not unrelated WB formatting. (ChatGPT-5.6-Sol) -->
        original = match.group("value")
        left = original[: len(original) - len(original.lstrip())]
        right = original[len(original.rstrip()) :]
        return prefix + left + new_value + right

    return TOKEN_RE.sub(repl, line)


def replace_single_key(lines: Sequence[str], key: str, value: str) -> Tuple[List[str], int]:
    pattern = re.compile(r"^(?P<indent>\s*)" + re.escape(key) + r"\s*=.*?(?P<eol>\r?\n)?$")
    out: List[str] = []
    changed = 0
    in_game = False
    for line in lines:
        stripped = line.rstrip("\r\n")
        if stripped.strip() == "BeginGame":
            in_game = True
        elif stripped.strip() == "EndGame":
            in_game = False
        match = pattern.match(line) if in_game else None
        if match:
            eol = match.group("eol") or ""
            replacement = "%s%s=%s%s" % (match.group("indent"), key, value, eol)
            if replacement != line:
                changed += 1
            out.append(replacement)
        else:
            out.append(line)
    return out, changed


def analyze(lines: Sequence[str], destination_types: Optional[set], allow_nonzero_turn: bool, allow_unresolved_types: bool = False) -> Dict[str, object]:
    errors: List[str] = []
    warnings: List[str] = []
    counts, structure_errors = scan_structure(lines)
    errors.extend(structure_errors)

    version = int_value(first_value(lines[:20], "Version"), "Version", errors)
    if version is not None and version != SUPPORTED_WB_VERSION:
        errors.append("unsupported WorldBuilder Version=%d (expected %d)" % (version, SUPPORTED_WB_VERSION))

    game_blocks = block_lines(lines, "Game")
    map_blocks = block_lines(lines, "Map")
    if len(game_blocks) != 1:
        errors.append("expected exactly one BeginGame block, found %d" % len(game_blocks))
    if len(map_blocks) != 1:
        errors.append("expected exactly one BeginMap block, found %d" % len(map_blocks))

    game = game_blocks[0] if game_blocks else []
    map_lines = map_blocks[0] if map_blocks else []
    game_turn = int_value(first_value(game, "GameTurn"), "GameTurn", errors)
    if game_turn is not None and game_turn != 0 and not allow_nonzero_turn:
        errors.append("GameTurn=%d is outside the initial T0-only scope" % game_turn)

    width = int_value(first_value(map_lines, "grid width"), "map grid width", errors)
    height = int_value(first_value(map_lines, "grid height"), "map grid height", errors)
    num_plots_written = int_value(first_value(map_lines, "num plots written"), "num plots written", errors)
    num_signs_written = int_value(first_value(map_lines, "num signs written"), "num signs written", errors)
    randomize_resources = first_value(map_lines, "Randomize Resources")
    if randomize_resources is None:
        errors.append("missing Randomize Resources map setting")
    elif randomize_resources.lower() != "false":
        errors.append("Randomize Resources=%s would destroy exact source bonuses on import" % randomize_resources)

    plots = block_lines(lines, "Plot")
    if width is not None and height is not None:
        expected = width * height
        if num_plots_written is not None and num_plots_written != expected:
            errors.append("map declares %d plots but grid dimensions require %d" % (num_plots_written, expected))
        if len(plots) != expected:
            errors.append("WBSave contains %d BeginPlot blocks but grid dimensions require %d" % (len(plots), expected))
        if num_plots_written is not None and len(plots) != num_plots_written:
            errors.append("WBSave contains %d BeginPlot blocks but map declares %d" % (len(plots), num_plots_written))

    plot_coords: List[Tuple[int, int]] = []
    duplicate_coords: List[Tuple[int, int]] = []
    out_of_bounds: List[Tuple[int, int]] = []
    seen = set()
    starting_plots: List[Tuple[int, int]] = []
    plot_type_inventory: Dict[str, collections.Counter] = {
        "TerrainType": collections.Counter(),
        "FeatureType": collections.Counter(),
        "BonusType": collections.Counter(),
        "ImprovementType": collections.Counter(),
        "RouteType": collections.Counter(),
        "PlotType": collections.Counter(),
    }
    for plot in plots:
        local_errors: List[str] = []
        x = int_value(first_value(plot, "x"), "plot x", local_errors)
        y = int_value(first_value(plot, "y"), "plot y", local_errors)
        if local_errors:
            errors.extend(local_errors)
            continue
        assert x is not None and y is not None
        coord = (x, y)
        plot_coords.append(coord)
        if coord in seen:
            duplicate_coords.append(coord)
        seen.add(coord)
        if width is not None and height is not None and not (0 <= x < width and 0 <= y < height):
            out_of_bounds.append(coord)
        if any(line.strip() == "StartingPlot" for line in plot):
            starting_plots.append(coord)
        for key in plot_type_inventory:
            value = first_value(plot, key)
            if value not in (None, ""):
                plot_type_inventory[key][value] += 1
    if duplicate_coords:
        errors.append("duplicate plot coordinates: %s" % duplicate_coords[:20])
    if out_of_bounds:
        errors.append("out-of-bounds plot coordinates: %s" % out_of_bounds[:20])

    player_starts: List[Dict[str, object]] = []
    players = block_lines(lines, "Player")
    for player_index, player in enumerate(players):
        sx = first_value(player, "StartingX")
        sy = first_value(player, "StartingY")
        if sx is None and sy is None:
            continue
        # <!-- custom: Was int(sx) and int(sy) silenced for the type checker, relying on int(None) raising TypeError when a file gives only one of the two; checking for None first says it in code, so nothing needs silencing.
        # The same error is reported as before, for a missing coordinate and for one that is not a number. (Claude code Opus 5.5) -->
        if sx is None or sy is None:
            errors.append("player %d has invalid StartingX/StartingY: %r/%r" % (player_index, sx, sy))
            continue
        try:
            coord = (int(sx), int(sy))
        except ValueError:
            errors.append("player %d has invalid StartingX/StartingY: %r/%r" % (player_index, sx, sy))
            continue
        if width is not None and height is not None and not (0 <= coord[0] < width and 0 <= coord[1] < height):
            errors.append("player %d start %s is outside the map" % (player_index, coord))
        player_starts.append({"player_index": player_index, "x": coord[0], "y": coord[1]})

    signs = block_lines(lines, "Sign")
    if num_signs_written is not None and len(signs) != num_signs_written:
        errors.append("WBSave contains %d BeginSign blocks but map declares %d" % (len(signs), num_signs_written))

    type_usage: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    missing_types: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for line in lines:
        for key, value in split_tokens(line):
            if not is_checked_value(key, value):
                continue
            type_usage[key][value] += 1
            if destination_types is not None and value not in destination_types:
                missing_types[key][value] += 1

    if destination_types is not None and missing_types:
        for key in sorted(missing_types):
            values = ", ".join(sorted(missing_types[key]))
            message = "destination XML roots do not contain %s value(s): %s" % (key, values)
            if allow_unresolved_types:
                warnings.append(message)
            else:
                errors.append(message)

    # <!-- custom: Older AdvCiv/SAS WB saves may legitimately contain fewer team/player slots; advc.056 pads the missing tail, so report count differences instead of rejecting them. (ChatGPT-5.6-Sol) -->
    if counts["Team"] != counts["Player"]:
        warnings.append("team/player block counts differ: %d teams, %d players" % (counts["Team"], counts["Player"]))

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "wb_version": version,
        "game_turn": game_turn,
        "game": {
            "era": first_value(game, "Era"),
            "speed": first_value(game, "Speed"),
            "calendar": first_value(game, "Calendar"),
            "start_year": first_value(game, "StartYear"),
            "mod_path": first_value(game, "ModPath"),
        },
        "map": {
            "width": width,
            "height": height,
            "wrap_x": first_value(map_lines, "wrap X"),
            "wrap_y": first_value(map_lines, "wrap Y"),
            "world_size": first_value(map_lines, "world size"),
            "climate": first_value(map_lines, "climate"),
            "sea_level": first_value(map_lines, "sealevel"),
            "declared_plots": num_plots_written,
            "plot_blocks": len(plots),
            "declared_signs": num_signs_written,
            "sign_blocks": len(signs),
            "randomize_resources": randomize_resources,
            "starting_plots": [{"x": x, "y": y} for x, y in starting_plots],
        },
        "blocks": dict(sorted(counts.items())),
        "player_starts": player_starts,
        "plot_inventory": {key: dict(sorted(counter.items())) for key, counter in plot_type_inventory.items()},
        "xml_type_usage": {key: dict(sorted(counter.items())) for key, counter in sorted(type_usage.items())},
        "missing_destination_types": {key: dict(sorted(counter.items())) for key, counter in sorted(missing_types.items())},
    }


def canonical_line(line: str) -> str:
    stripped = line.strip()
    if not stripped or stripped.startswith("###"):
        return ""
    stripped = re.sub(r"\s*=\s*", "=", stripped)
    stripped = re.sub(r",\s*", ",", stripped)
    return stripped


def canonical_block(block: Sequence[str]) -> List[str]:
    """Canonicalize one WB block while retaining repeated fields and nesting."""
    result = []
    for line in block:
        normalized = canonical_line(line)
        if normalized:
            result.append(normalized)
    return result


def keyed_plot_blocks(lines: Sequence[str]) -> Tuple[Dict[str, List[str]], List[str]]:
    result: Dict[str, List[str]] = {}
    errors: List[str] = []
    for index, plot in enumerate(block_lines(lines, "Plot")):
        local_errors: List[str] = []
        x = int_value(first_value(plot, "x"), "plot x", local_errors)
        y = int_value(first_value(plot, "y"), "plot y", local_errors)
        if local_errors or x is None or y is None:
            errors.append("plot block %d has no valid coordinate" % index)
            continue
        key = "%d,%d" % (x, y)
        if key in result:
            errors.append("duplicate plot coordinate during comparison: %s" % key)
        result[key] = canonical_block(plot)
    return result, errors


def extra_slot_activity(block: Sequence[str], block_name: str) -> List[str]:
    """Return state-bearing fields that make an added destination slot nonempty."""
    active = []
    team_id = first_value(block, "TeamID") if block_name == "Team" else None
    for line in block:
        for key, value in split_tokens(line):
            if block_name == "Team":
                if key == "TeamID" or (key == "RevealMap" and value == "0"):
                    continue
                # <!-- custom: The writer gives every team slot, used or not, contact with itself, so the 30 slots that current SAS adds to a 4986 world each counted as active and failed the comparison. (Claude code Fable 5.2) -->
                if key == "ContactWithTeam" and team_id is not None and value == team_id:
                    continue
                if key in {"VassalPower", "MasterPower", "EspionageEverAmount"} and value == "0":
                    continue
                active.append(canonical_line(line))
                break
            if block_name == "Player":
                if key == "Team" or key == "Handicap":
                    continue
                if key in {"LeaderType", "CivType", "Color", "ArtStyle"} and value == "NONE":
                    continue
                if key in {"PlayableCiv", "MinorNationStatus", "StartingGold"} and value == "0":
                    continue
                if key == "StateReligion" and value == "":
                    continue
                if key == "RandomStartLocation" and value.lower() == "false":
                    continue
                active.append(canonical_line(line))
                break
    return active


def compare_sequence_blocks(source_lines: Sequence[str], destination_lines: Sequence[str], block_name: str) -> Dict[str, object]:
    source_raw = block_lines(source_lines, block_name)
    destination_raw = block_lines(destination_lines, block_name)
    source_blocks = [canonical_block(block) for block in source_raw]
    destination_blocks = [canonical_block(block) for block in destination_raw]
    overlap = min(len(source_blocks), len(destination_blocks))
    changed = []
    for index in range(overlap):
        if source_blocks[index] != destination_blocks[index]:
            changed.append({
                "index": index,
                "source": source_blocks[index],
                "destination": destination_blocks[index],
            })
    extra_active = []
    for index in range(len(source_raw), len(destination_raw)):
        activity = extra_slot_activity(destination_raw[index], block_name)
        if activity:
            extra_active.append({"index": index, "activity": activity})
    return {
        "source_count": len(source_blocks),
        "destination_count": len(destination_blocks),
        "compared_count": overlap,
        "extra_destination_count": max(0, len(destination_blocks) - len(source_blocks)),
        "missing_destination_count": max(0, len(source_blocks) - len(destination_blocks)),
        "changed": changed,
        "active_extra_destination_slots": extra_active,
    }


# <!-- custom: Added allowed_plot_changes for SASSaveTransplanter.py's "update" map variant, which adds features and bonuses on purpose: it maps "x,y" to the exact lines that plot may lose ("removed") and gain ("added").
# A plot whose difference is exactly that passes, any other difference still fails, and an announced change that is not found fails too.
# Before, the caller waived all plot differences of that variant, which Codex (GPT-6.1-Sol)'s 2026-11-16 review showed could hide a changed river. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
def compare_worldbuilder(source_lines: Sequence[str], destination_lines: Sequence[str], allowed_plot_changes: Optional[Mapping[str, Mapping[str, Sequence[str]]]] = None) -> Dict[str, object]:
    """Compare the T0 payload of two WB saves, tolerating added tail slots."""
    source_game = block_lines(source_lines, "Game")
    destination_game = block_lines(destination_lines, "Game")
    source_map = block_lines(source_lines, "Map")
    destination_map = block_lines(destination_lines, "Map")

    # <!-- custom: Ignore ModPath and free-form Description during semantic verification because they are transport metadata rather than transplanted T0 world state. (ChatGPT-5.6-Sol) -->
    ignored_game_keys = {"ModPath", "Description"}

    def filtered_block(blocks: List[List[str]], ignored_keys: set) -> List[str]:
        if not blocks:
            return []
        result = []
        for line in blocks[0]:
            tokens = split_tokens(line)
            if tokens and all(key in ignored_keys for key, _value in tokens):
                continue
            normalized = canonical_line(line)
            if normalized:
                result.append(normalized)
        return result

    source_game_canonical = filtered_block(source_game, ignored_game_keys)
    destination_game_canonical = filtered_block(destination_game, ignored_game_keys)
    source_map_canonical = filtered_block(source_map, set())
    destination_map_canonical = filtered_block(destination_map, set())

    source_plots, source_plot_errors = keyed_plot_blocks(source_lines)
    destination_plots, destination_plot_errors = keyed_plot_blocks(destination_lines)
    source_coords = set(source_plots)
    destination_coords = set(destination_plots)
    changed_plots = []
    allowed_found = set()
    for coord in sorted(source_coords & destination_coords):
        if source_plots[coord] != destination_plots[coord]:
            allowed = (allowed_plot_changes or {}).get(coord)
            if allowed is not None:
                removed = collections.Counter(source_plots[coord]) - collections.Counter(destination_plots[coord])
                added = collections.Counter(destination_plots[coord]) - collections.Counter(source_plots[coord])
                if sorted(removed.elements()) == sorted(canonical_line(line) for line in allowed.get("removed", [])) and sorted(added.elements()) == sorted(canonical_line(line) for line in allowed.get("added", [])):
                    allowed_found.add(coord)
                    continue
            changed_plots.append({
                "coordinate": coord,
                "source": source_plots[coord],
                "destination": destination_plots[coord],
            })

    teams = compare_sequence_blocks(source_lines, destination_lines, "Team")
    players = compare_sequence_blocks(source_lines, destination_lines, "Player")
    signs = compare_sequence_blocks(source_lines, destination_lines, "Sign")

    failures = []
    if source_game_canonical != destination_game_canonical:
        failures.append("game settings differ (excluding ModPath/Description)")
    if source_map_canonical != destination_map_canonical:
        failures.append("map metadata differs")
    if source_coords != destination_coords:
        failures.append("plot coordinate sets differ")
    if changed_plots:
        failures.append("%d plot payload(s) differ" % len(changed_plots))
    allowed_missing = sorted(set(allowed_plot_changes or {}) - allowed_found)
    if allowed_missing:
        failures.append("%d announced plot change(s) not found as announced" % len(allowed_missing))
    if teams["missing_destination_count"] or teams["changed"]:
        failures.append("source team payload differs within source slot range")
    if teams["active_extra_destination_slots"]:
        failures.append("added destination team slots contain active state")
    if players["missing_destination_count"] or players["changed"]:
        failures.append("source player payload differs within source slot range")
    if players["active_extra_destination_slots"]:
        failures.append("added destination player slots contain active state")
    if signs["source_count"] != signs["destination_count"] or signs["changed"]:
        failures.append("sign payload differs")
    failures.extend(source_plot_errors)
    failures.extend(destination_plot_errors)

    return {
        "equivalent_t0_world": not failures,
        "failures": failures,
        "game": {
            "equal": source_game_canonical == destination_game_canonical,
            "source": source_game_canonical,
            "destination": destination_game_canonical,
            "ignored_keys": sorted(ignored_game_keys),
        },
        "map": {
            "equal": source_map_canonical == destination_map_canonical,
            "source": source_map_canonical,
            "destination": destination_map_canonical,
        },
        "plots": {
            "source_count": len(source_plots),
            "destination_count": len(destination_plots),
            "missing_coordinates": sorted(source_coords - destination_coords),
            "extra_coordinates": sorted(destination_coords - source_coords),
            "changed": changed_plots,
            "allowed_changes_found": len(allowed_found),
            "allowed_changes_missing": allowed_missing,
        },
        "teams": teams,
        "players": players,
        "signs": signs,
    }

def report_for(
    source: Path,
    source_data: bytes,
    analysis: Dict[str, object],
    destination_xml_roots: Optional[Sequence[Path]],
    destination_type_count: Optional[int],
    transformations: Dict[str, object],
    source_build: Optional[str] = None,
    destination_build: Optional[str] = None,
    output: Optional[Path] = None,
    output_data: Optional[bytes] = None,
) -> Dict[str, object]:
    report: Dict[str, object] = {
        "report_format_version": REPORT_FORMAT_VERSION,
        "tool": "LLM_Helpers/sassavetransplanter/SASSaveTransplanterWorld.py",
        "source": {
            "path": str(source),
            "size_bytes": len(source_data),
            "sha256": sha256_bytes(source_data),
        },
        "destination_xml": None if destination_xml_roots is None else {
            "roots": [str(path) for path in destination_xml_roots],
            "symbol_count": destination_type_count,
        },
        "analysis": analysis,
        "transformations": transformations,
        "provenance": {
            "source_build": source_build,
            "destination_build": destination_build,
        },
    }
    if output is not None and output_data is not None:
        report["output"] = {
            "path": str(output),
            "size_bytes": len(output_data),
            "sha256": sha256_bytes(output_data),
            "written": False,
        }
    return report


def write_report(path: Optional[Path], report: Mapping[str, object]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def print_summary(report: Mapping[str, object]) -> None:
    analysis = report["analysis"]
    assert isinstance(analysis, dict)
    map_info = analysis.get("map", {})
    blocks = analysis.get("blocks", {})
    print("T0 WorldBuilder transplant inspection")
    print("  valid: %s" % analysis.get("valid"))
    print("  WB version: %s" % analysis.get("wb_version"))
    print("  game turn: %s" % analysis.get("game_turn"))
    if isinstance(map_info, dict):
        print("  map: %sx%s; plots=%s; starting plots=%s" % (
            map_info.get("width"), map_info.get("height"), map_info.get("plot_blocks"),
            len(map_info.get("starting_plots", [])),
        ))
    if isinstance(blocks, dict):
        print("  blocks: teams=%s players=%s units=%s cities=%s signs=%s" % (
            blocks.get("Team", 0), blocks.get("Player", 0), blocks.get("Unit", 0),
            blocks.get("City", 0), blocks.get("Sign", 0),
        ))
    missing = analysis.get("missing_destination_types", {})
    if isinstance(missing, dict):
        missing_count = sum(len(values) for values in missing.values() if isinstance(values, dict))
        print("  missing destination type names: %d" % missing_count)
    errors = analysis.get("errors", [])
    warnings = analysis.get("warnings", [])
    if warnings:
        print("  warnings:")
        for item in warnings:
            print("    - %s" % item)
    if errors:
        print("  errors:")
        for item in errors:
            print("    - %s" % item)


def ensure_wb_source(path: Path) -> None:
    suffix_lower = path.name.lower()
    if suffix_lower.endswith(".civbeyondswordsave") and not suffix_lower.endswith(".civbeyondswordwbsave"):
        raise WBError(
            "binary .CivBeyondSwordSave input is intentionally not decoded by this helper; "
            "load it with its matching historical Civ4/AdvCiv-SAS build, export a "
            ".CivBeyondSwordWBSave, then run this tool on that logical world description"
        )


def command_inspect(args: argparse.Namespace) -> int:
    source = args.source.resolve()
    ensure_wb_source(source)
    source_data, text, _newline = read_wb(source)
    destination_types = None
    destination_type_count = None
    xml_warnings: List[str] = []
    xml_roots = [path.resolve() for path in args.dest_xml_root] if args.dest_xml_root else []
    if xml_roots:
        destination_types, _per_root, xml_warnings = load_destination_types(xml_roots)
        destination_type_count = len(destination_types)
    analysis = analyze(text.splitlines(True), destination_types, args.allow_nonzero_turn, args.allow_unresolved_types)
    # <!-- custom: Was analysis["warnings"].extend(...) silenced for the type checker, as analyze() returns Dict[str, object] although its "warnings" value is the list it builds.
    # Checking that it is a list says so in code, so nothing needs silencing, and fails loudly if analyze() ever changes it. (Claude code Opus 5.5) -->
    analysis_warnings = analysis["warnings"]
    if not isinstance(analysis_warnings, list):
        raise TypeError("analyze() returned warnings as %s, not a list" % type(analysis_warnings).__name__)
    analysis_warnings.extend(xml_warnings)
    report = report_for(source, source_data, analysis, xml_roots or None, destination_type_count, {"type_remaps": {}, "mod_path_changes": 0}, args.source_build, args.destination_build)
    write_report(args.report.resolve() if args.report else None, report)
    print_summary(report)
    return 0 if analysis["valid"] else 2


def command_transplant(args: argparse.Namespace) -> int:
    source = args.source.resolve()
    output = args.output.resolve()
    ensure_wb_source(source)
    if output == source:
        raise WBError("refusing to overwrite the source WBSave; choose a distinct --output path")
    if output.exists() and not args.overwrite:
        raise WBError("output already exists; choose a new path or pass --overwrite: %s" % output)
    source_data, text, newline = read_wb(source)
    mapping = load_mapping(args.mapping.resolve() if args.mapping else None)
    xml_roots = [path.resolve() for path in args.dest_xml_root]
    destination_types, _per_root, xml_warnings = load_destination_types(xml_roots)

    lines = text.splitlines(True)
    remapped: MutableMapping[str, int] = collections.Counter()
    transformed = [replace_type_values(line, mapping, remapped) for line in lines]
    mod_path_changes = 0
    if args.mod_path is not None:
        transformed, mod_path_changes = replace_single_key(transformed, "ModPath", args.mod_path)

    # <!-- custom: Preserve source line endings and a missing final newline so a no-op transplant can remain byte-identical apart from explicitly requested transformations. (ChatGPT-5.6-Sol) -->
    output_text = "".join(transformed)
    if newline == "\r\n" and "\r\n" not in output_text and "\n" in output_text:
        # <!-- custom: Keep a defensive CRLF restoration path even though the current replacement operations preserve EOLs. (ChatGPT-5.6-Sol) -->
        output_text = output_text.replace("\n", "\r\n")
    output_data = output_text.encode(WB_ENCODING)

    analysis = analyze(transformed, destination_types, args.allow_nonzero_turn, args.allow_unresolved_types)
    # <!-- custom: Was analysis["warnings"].extend(...) silenced for the type checker, as analyze() returns Dict[str, object] although its "warnings" value is the list it builds.
    # Checking that it is a list says so in code, so nothing needs silencing, and fails loudly if analyze() ever changes it. (Claude code Opus 5.5) -->
    analysis_warnings = analysis["warnings"]
    if not isinstance(analysis_warnings, list):
        raise TypeError("analyze() returned warnings as %s, not a list" % type(analysis_warnings).__name__)
    analysis_warnings.extend(xml_warnings)
    transformations = {
        "type_remaps": dict(sorted(remapped.items())),
        "mapping_file": str(args.mapping.resolve()) if args.mapping else None,
        "mod_path": args.mod_path,
        "mod_path_changes": mod_path_changes,
        "unknown_lines_preserved": True,
        "slot_padding": False,
    }
    report = report_for(source, source_data, analysis, xml_roots, len(destination_types), transformations, args.source_build, args.destination_build, output, output_data)
    report_path = args.report.resolve() if args.report else output.with_suffix(output.suffix + ".transplant.json")
    write_report(report_path, report)
    print_summary(report)

    if not analysis["valid"] and not args.write_invalid:
        print("Refusing to write invalid transplant; report written to %s" % report_path, file=sys.stderr)
        return 2
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(output_data)
    output_report = report.get("output")
    if isinstance(output_report, dict):
        output_report["written"] = True
        write_report(report_path, report)
    print("  output: %s" % output)
    print("  report: %s" % report_path)
    if not analysis["valid"]:
        print("  NOTE: output was written only because --write-invalid was supplied")
    return 0 if analysis["valid"] else 2


def command_compare(args: argparse.Namespace) -> int:
    source = args.source.resolve()
    destination = args.destination.resolve()
    ensure_wb_source(source)
    ensure_wb_source(destination)
    source_data, source_text, _ = read_wb(source)
    destination_data, destination_text, _ = read_wb(destination)
    source_lines = source_text.splitlines(True)
    destination_lines = destination_text.splitlines(True)
    if args.ignore_free_grants:
        # <!-- custom: SASSaveTransplanter.py's default policy lets the destination build deal its own civilization free techs and free promotions, and checks them itself against both builds' lists; team Tech lines and unit PromotionType lines then differ by design and would hide any other difference. (Claude code Fable 5.2) -->
        source_lines = [line for line in source_lines if not line.strip().startswith(("Tech=", "PromotionType="))]
        destination_lines = [line for line in destination_lines if not line.strip().startswith(("Tech=", "PromotionType="))]
    if args.ignore_player_names:
        # <!-- custom: For SASSaveTransplanter.py's load check, which compares a game's world before saving with the same game's world after loading the save.
        # A scenario start keeps each player's name lines as text keys (LeaderName=TXT_KEY_LEADER_ISABELLA); after a save and load the game only has the resolved text (LeaderName=Isabella I), so all 11 players of the first check differed in those lines and nothing else. (Claude code Fable 5.2) -->
        name_keys = ("LeaderName=", "CivDesc=", "CivShortDesc=", "CivAdjective=")
        source_lines = [line for line in source_lines if not line.strip().startswith(name_keys)]
        destination_lines = [line for line in destination_lines if not line.strip().startswith(name_keys)]
    allowed_plot_changes = json.loads(args.allowed_plot_changes.read_text(encoding="utf-8")) if args.allowed_plot_changes else None
    comparison = compare_worldbuilder(source_lines, destination_lines, allowed_plot_changes)
    source_validation = analyze(source_lines, None, False, False)
    destination_validation = analyze(destination_lines, None, False, False)
    if not source_validation["valid"]:
        comparison["failures"].insert(0, "source WBSave fails T0 structural validation")
    if not destination_validation["valid"]:
        comparison["failures"].insert(0, "destination WBSave fails T0 structural validation")
    comparison["equivalent_t0_world"] = not comparison["failures"]
    comparison["source_validation"] = source_validation
    comparison["destination_validation"] = destination_validation
    report = {
        "report_format_version": REPORT_FORMAT_VERSION,
        "tool": "LLM_Helpers/sassavetransplanter/SASSaveTransplanterWorld.py compare",
        "source": {"path": str(source), "size_bytes": len(source_data), "sha256": sha256_bytes(source_data)},
        "destination": {"path": str(destination), "size_bytes": len(destination_data), "sha256": sha256_bytes(destination_data)},
        "comparison": comparison,
        "provenance": {"source_build": args.source_build, "destination_build": args.destination_build},
    }
    write_report(args.report.resolve() if args.report else None, report)
    print("T0 WorldBuilder semantic comparison")
    print("  equivalent T0 world: %s" % comparison["equivalent_t0_world"])
    plots = comparison["plots"]
    teams = comparison["teams"]
    players = comparison["players"]
    print("  plots: source=%d destination=%d changed=%d" % (plots["source_count"], plots["destination_count"], len(plots["changed"])))
    print("  teams: source=%d destination=%d changed=%d extra destination=%d" % (teams["source_count"], teams["destination_count"], len(teams["changed"]), teams["extra_destination_count"]))
    print("  players: source=%d destination=%d changed=%d extra destination=%d" % (players["source_count"], players["destination_count"], len(players["changed"]), players["extra_destination_count"]))
    if comparison["failures"]:
        print("  differences:")
        for item in comparison["failures"]:
            print("    - %s" % item)
    return 0 if comparison["equivalent_t0_world"] else 3

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate/normalize T0 Civ4 WorldBuilder saves for AdvCiv-SAS migration.",
        epilog=(
            "Binary .CivBeyondSwordSave files are not parsed directly. Export them to "
            "WorldBuilder format with the matching source build first; the current build "
            "then imports the validated WBSave and writes a fresh current-format binary save."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    compare_parser = sub.add_parser("compare", help="compare source and post-import/re-export WBSave T0 payloads")
    compare_parser.add_argument("source", type=Path)
    compare_parser.add_argument("destination", type=Path)
    compare_parser.add_argument("--report", type=Path, help="write JSON semantic comparison report")
    compare_parser.add_argument("--ignore-free-grants", action="store_true", help="leave team Tech lines and unit PromotionType lines out of the comparison")
    compare_parser.add_argument("--ignore-player-names", action="store_true", help="leave the players' LeaderName, CivDesc, CivShortDesc and CivAdjective lines out of the comparison")
    compare_parser.add_argument("--allowed-plot-changes",type=Path, help="JSON of \"x,y\" to {removed, added} lines: plot differences that are expected and must be exactly these")
    compare_parser.add_argument("--source-build",help="source build/version/commit label recorded in the report")
    compare_parser.add_argument("--destination-build", help="destination build/version/commit label recorded in the report")
    compare_parser.set_defaults(func=command_compare)

    inspect_parser = sub.add_parser("inspect", help="inspect a source WBSave without modifying it")
    inspect_parser.add_argument("source", type=Path)
    inspect_parser.add_argument("--dest-xml-root", type=Path, action="append", help="destination XML root; repeat in low-to-high precedence order (base/Warlords/BtS/mod)")
    inspect_parser.add_argument("--report", type=Path, help="write JSON inspection report")
    inspect_parser.add_argument("--source-build", help="source build/version/commit label recorded in the report")
    inspect_parser.add_argument("--destination-build", help="intended destination build/version/commit label recorded in the report")
    inspect_parser.add_argument("--allow-nonzero-turn", action="store_true", help="inspect later-turn WB files (outside supported transplant scope)")
    inspect_parser.add_argument("--allow-unresolved-types", action="store_true", help="downgrade missing destination XML identities to warnings; use only with an incomplete XML snapshot")
    inspect_parser.set_defaults(func=command_inspect)

    transplant_parser = sub.add_parser("transplant", help="normalize/remap a WBSave for a destination SAS tree")
    transplant_parser.add_argument("source", type=Path)
    transplant_parser.add_argument("--dest-xml-root", type=Path, action="append", required=True, help="destination XML root; repeat in low-to-high precedence order (base/Warlords/BtS/mod)")
    transplant_parser.add_argument("--output", type=Path, required=True, help="destination .CivBeyondSwordWBSave")
    transplant_parser.add_argument("--mapping", type=Path, help="JSON old-type -> new-type mapping; no implicit substitutions are made")
    transplant_parser.add_argument("--mod-path", help="explicitly rewrite BeginGame ModPath (for example Mods\\AdvCiv-SAS)")
    transplant_parser.add_argument("--report", type=Path, help="JSON report path (default: OUTPUT.transplant.json)")
    transplant_parser.add_argument("--source-build", help="source build/version/commit label recorded in the report")
    transplant_parser.add_argument("--destination-build", help="destination build/version/commit label recorded in the report")
    transplant_parser.add_argument("--allow-nonzero-turn", action="store_true", help="allow nonzero GameTurn for investigation only")
    transplant_parser.add_argument("--allow-unresolved-types", action="store_true", help="downgrade missing destination XML identities to warnings; use only with an incomplete XML snapshot")
    transplant_parser.add_argument("--write-invalid", action="store_true", help="write output despite validation errors; exit remains nonzero")
    transplant_parser.add_argument("--overwrite", action="store_true", help="replace an existing destination output; the source path is never overwritable")
    transplant_parser.set_defaults(func=command_transplant)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (WBError, OSError) as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
