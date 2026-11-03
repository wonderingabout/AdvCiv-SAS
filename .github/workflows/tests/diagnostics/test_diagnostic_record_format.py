# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Path/sys load the actual record-format checker; unittest exercises the shapes the BBAI normalization pass removed. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/diagnostics"))
# <!-- custom: Import the same checker as CI so fixtures exercise one implementation. (Claude code Opus 5.5) -->
import diagnostic_record_format as checker


class DiagnosticRecordFormatTests(unittest.TestCase):
    def errors(self, source):
        return checker.check_source("Test.cpp", source)

    def test_current_record_shapes_pass(self):
        for source in ['logBBAI("PLAYER_STATUS turn=%d player=%d civ=%s city=%S cities=%d build=%s", 1, 2, "CIVILIZATION_AMERICA", getSASDiagnosticQuoted(kCity.getName().GetCString()).GetCString(), 3, "BUILD_COTTAGE");',
                       'logBBAI("FOUND_SITE_%s turn=%d", szStage, 1);',
                       'logBBAI("BBAI_INITIAL_STATE_SUMMARY techRows=%d %s source=FINALIZED_STATE", 1, szFields);',
                       'logBBAI("%s processUtc=%s", szId, szUtc);',
                       'logSASGameRecord("GAME_RECORD_ACTION turn=%d type=CITY_RAZED city=%S", 1, kContext.szCityName.GetCString());',
                       'logSASGameRecord("GAME_RECORD_AI_GREAT_GENERAL_DECISION targetCity=%S", getSASGameRecordQuotedCityName(pTargetCity).GetCString());']:
            with self.subTest(source=source):
                self.assertEqual(self.errors(source), [])

    def test_removed_shapes_fail(self):
        cases = {'logBBAI("    WORKER_YIELD_BUILD turn=%d", 1);': "indentation",
                 'logBBAI("WORKER_YIELD_BUILD turn=%d player=%d %S", 1, 2, L"x");': "unnamed string",
                 'logBBAI("SETTLER_PARKED player=%d (%S)", 1, L"x");': "unnamed string",
                 'logBBAI("OVERSEAS_CONQUEST_CANDIDATE target=%S target=(%d,%d)", L"x", 1, 2);': "repeated key",
                 'logBBAI("Settler heading for site %d, %d", 1, 2);': "uppercase record ID",
                 'logBBAI("PLAYER_STATUS player=%d city=%S", 1, kCity.getName().GetCString());': "not passed through getSASDiagnosticQuoted",
                 'logBBAI("PLAYER_STATUS player=%d city=\\"%S\\"", 1, kCity.getName().GetCString());': "quotes display text in the literal",
                 'logBBAI("SCRAP_EVENT player=%d unitAI=\'%S\'", 1, L"x");': "quotes display text in the literal",
                 'logBBAI("CULTURE_WEIGHT_SUMMARY player=%d stageFlags C1=%d", 1, 2);': "not key=value fields",
                 'logBBAI("IRRIGATION_CHAIN_NO_USABLE_STEP rejects(unowned=%d foreign=%d)", 1, 2);': "not key=value fields",
                 'logSASGameRecord("GAME_RECORD_AI_GREAT_PERSON_DECISION slowCity=%S", pSlowCity->getName().GetCString());': "not passed through getSASDiagnosticQuoted"}
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertTrue(any(expected in error for error in self.errors(source)), self.errors(source))

    def test_disabled_rows_and_line_numbers(self):
        source = '// logBBAI("    old row %d", 1);\n/* logBBAI("old %S", L"x"); */\nint x = 1;\nlogBBAI("    NEW_ROW turn=%d", 1);\n'
        errors = self.errors(source)
        self.assertEqual(len(errors), 1)
        self.assertIn("Test.cpp:4:", errors[0])


if __name__ == "__main__":
    unittest.main()
