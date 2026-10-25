#!/usr/bin/env python3
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

from pathlib import Path
import sys

# <!-- custom: Reuse the shared XML-default validator; Battles coordinates are useful by default, while users can disable the columns locally when width is scarce. (GPT-6.1-Sol) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))

from xml_defines import main_from_expected_values

EXPECTED_ADVISOR_DEFINES = {"SAS_MILIT_UI_BATTLE_XY_ON": 1}

if __name__ == "__main__":
    main_from_expected_values("advisor defaults", EXPECTED_ADVISOR_DEFINES, "Check shipped advisor presentation defaults.")
