# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; tempfile isolates XML fixtures and unittest verifies that compact turn units preserve classification coverage. (GPT-6.1-Sol) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Exercise real XML discovery and classification rather than duplicating the checker's regular expressions. (GPT-6.1-Sol) -->
import turn_define_gamespeed as turns


class TurnDefineGameSpeedTests(unittest.TestCase):
    def check_names(self, *names):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / "Assets/XML/GlobalDefines_advciv_sas.xml"
            target.parent.mkdir(parents=True)
            target.write_text(
                "<Civ4Defines>" + "".join(
                    f"<Define><DefineName>{name}</DefineName><iDefineIntVal>1</iDefineIntVal></Define>"
                    for name in names
                ) + "</Civ4Defines>",
                encoding="utf-8",
            )
            return turns.check_turn_define_gamespeed(root)

    def test_compact_and_long_forms_have_the_same_classification(self):
        errors, normal, unscaled = self.check_names(
            "SAS_PROD_SETTLER_MAX_T_NORM_GS",
            "SAS_PROD_SETTLER_MAX_TURNS_NORMAL_GAMESPEED",
            "SAS_PROD_DEF_BLDG_T_UNSCALED_GS_PER_DIST",
            "SAS_PROD_FORT_TURNS_UNSCALED_GAMESPEED_PER_DIST",
        )
        self.assertEqual((errors, normal, unscaled), ([], 2, 2))

    def test_unclassified_or_malformed_turn_units_fail(self):
        for name in (
            "SAS_PROD_SETTLER_MAX_T",
            "SAS_PROD_SETTLER_MAX_T_FAST_GS",
            "SAS_PROD_SETTLER_MAX_T_NORM_GSX",
            "SAS_PROD_SETTLER_MAX_TURNS",
            "SAS_PROD_MAX_COUNTDOWN_LIMIT",
        ):
            with self.subTest(name=name):
                self.assertTrue(self.check_names(name)[0])

    def test_conflicting_classifications_fail_across_spellings(self):
        errors, _, _ = self.check_names(
            "SAS_PROD_MAX_T_NORM_GS_TURNS_UNSCALED_GAMESPEED",
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("both", errors[0])

    def test_scopes_rates_weights_and_unrelated_letters_are_not_durations(self):
        self.assertEqual(self.check_names(
            "SAS_RUNTIME_PLAYER_TURN_LIVE_THRESHOLD_MS",
            "SAS_RUNTIME_PLAYER_TURN_LIVE_REFRESH_MS",
            "SAS_DO_TURN_CHECK_ON",
            "SAS_PROD_PER_T_VALUE",
            "SAS_PROD_PER_TURN_LIMIT",
            "SAS_PROD_PATH_T_VALUE_PENALTY",
            "SAS_WORKER_CITY_JOB_PATH_TURN_VAL_PENALTY",
            "SAS_PROD_SETTLER_ON",
        ), ([], 0, 0))


if __name__ == "__main__":
    unittest.main()
