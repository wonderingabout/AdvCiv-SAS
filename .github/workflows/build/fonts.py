#!/usr/bin/env python3
# AI, UI, or other modifications
# Created as part of AdvCiv-SAS improvements
# (c) 2026 wonderingabout & AI helpers (see Authors in root README.md)
#
# Build check: shared UI font defaults must stay release-safe.

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from xml_defines import main_from_expected_values


EXPECTED_FONT_DEFINES = {
	"SAS_UI_FONT_TINY": 1,
	"SAS_UI_FONT_BODY": 2,
	"SAS_UI_FONT_LABEL": 3,
	"SAS_UI_FONT_TITLE": 4,
	"SAS_UI_FONT_HOVER": 3,
}


if __name__ == "__main__":
	main_from_expected_values("shared UI font defaults", EXPECTED_FONT_DEFINES, "Check that AdvCiv-SAS shared UI font defaults are release-safe.")
