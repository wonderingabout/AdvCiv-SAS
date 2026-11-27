#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Which map scripts Simple Game lists, shared by map_preview_dds.py, make_civ4_ui_map.py and the CI check .github/workflows/build/assets/map_previews.py, so the three cannot disagree. See KI#1082.
# It lived in the CI check at first, but .github/ is left out of GitHub ZIP downloads while LLM_Helpers/ ships, so the two helpers failed at startup from a ZIP; Codex found this.
# The helpers' side owns it now and CI loads it from here. (Claude code Opus 5.5 + GPT-6.1-Sol) -->

# <!-- custom: re reads each script's isAdvancedMap; Path lists the scripts. (Claude code Opus 5.5) -->
import re
from pathlib import Path

# <!-- custom: Scripts that keep the default globe on purpose, each with its reason: the CI check accepts them without a preview, and map_preview_dds.py --all skips them. (Claude code Opus 5.5) -->
DEFAULT_GLOBE_ON_PURPOSE = {
	"RandomScriptMap": "picks another map script at random each game, so no single preview fits it (the user's choice, 2026-11-12)",
}


def shown_scripts(private_maps: Path) -> list[str]:
	# <!-- custom: Simple Game lists a script only when its isAdvancedMap returns 0; a script without the function stays hidden (KI#1082). (Claude code Opus 5.5) -->
	# <!-- custom: The first version matched only "return 0" at a line start, so PerfectMongoose's "return False" left it out: 37 of 38 shown scripts, and its missing preview went unflagged.
	# Python treats 0 and False alike, so both count, as does a one-line "def isAdvancedMap(): return 0". (Claude code Opus 5.5 + GPT-6.1-Sol) -->
	shown = []
	for path in sorted(private_maps.glob("*.py")):
		match = re.search(r"^def isAdvancedMap\(\):(.*?)(?=^\S|\Z)", path.read_text(encoding="latin-1"), re.S | re.M)
		# <!-- custom: Comments are dropped first: BTG_Cross and BTG_Lagoon say "return 1 hides it" beside their return 0. (Claude code Opus 5.5) -->
		returns = re.findall(r"\breturn\s+(\w+)", re.sub(r"#[^\n]*", "", match.group(1))) if match else []
		if returns and all(value in ("0", "False") for value in returns):
			shown.append(path.stem)
	return shown
