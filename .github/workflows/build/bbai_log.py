#!/usr/bin/env python3
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# Build check: BBAI logging must be disabled by default.

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from xml_defines import main_from_expected_values


EXPECTED_DISABLED_BBAI_DEFINES = {
	"SAS_BBAI_LOG_ENABLE": 0,
	"SAS_BBAI_PLAYER_LOG_LEVEL": 0,
	"SAS_BBAI_TEAM_LOG_LEVEL": 0,
	"SAS_BBAI_CITY_LOG_LEVEL": 0,
	"SAS_BBAI_UNIT_LOG_LEVEL": 0,
	"SAS_BBAI_MAP_LOG_LEVEL": 0,
	"SAS_BBAI_FOUND_LOG_LEVEL": 0,
	"SAS_BBAI_DEAL_CANCEL_LOG_LEVEL": 0,
}


if __name__ == "__main__":
	main_from_expected_values("BBAI logging disabled by default", EXPECTED_DISABLED_BBAI_DEFINES, "Check that AdvCiv-SAS BBAI logging is disabled by default.")
