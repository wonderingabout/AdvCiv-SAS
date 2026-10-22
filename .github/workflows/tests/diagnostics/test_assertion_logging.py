# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Keep lightweight CI guards around assertion-policy wiring and macro coverage.
# Actual startup fallback, caching, automatic resolution, dialog context and writer behavior are executed by tests/diagnostics/run_assertion_tests.py with VC2003 instead of being inferred from source spellings here. (ChatGPT-5.6-Sol) -->
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[4]
CPP = ROOT / "CvGameCoreDLL/FAssert.cpp"
HEADER = ROOT / "CvGameCoreDLL/FAssert.h"
XML_SET = ROOT / "CvGameCoreDLL/CvXMLLoadUtilitySet.cpp"
DEFINES = ROOT / "Assets/XML/GlobalDefines_advciv_sas.xml"


class AssertionLoggingTests(unittest.TestCase):
    def test_silent_action_define_defaults_to_unattended_ignore_once(self):
        root = ET.parse(DEFINES).getroot()
        values = {}
        for node in root.iter():
            if node.tag.rsplit("}", 1)[-1] != "Define":
                continue
            children = {child.tag.rsplit("}", 1)[-1]: (child.text or "").strip() for child in node}
            name = children.get("DefineName")
            if name:
                values[name] = children.get("iDefineIntVal")
        self.assertEqual(values.get("SAS_ASSERT_SILENT_ACTION"), "1")

    def test_policy_cache_is_initialized_after_global_define_overrides(self):
        source = XML_SET.read_text(encoding="utf-8")
        body = source[source.index("bool CvXMLLoadUtility::SetGlobalDefines()"):source.index("bool CvXMLLoadUtility::SetPostGlobalsGlobalDefines()") ]
        self.assertLess(body.index("GC.cacheGlobals();"), body.index("cacheSASAssertionSilentPolicy();"))
        self.assertLess(body.index("cacheSASAssertionSilentPolicy();"), body.index("return true;"))
        assertion_source = CPP.read_text(encoding="utf-8")
        handler = assertion_source[assertion_source.index("bool FAssertDlg("): ]
        self.assertNotIn("GetVariable(", handler)
        self.assertNotIn("getDefine", handler)

    def test_failure_is_persisted_before_dialog_or_automatic_resolution(self):
        source = CPP.read_text(encoding="utf-8")
        body = source[source.index("bool FAssertDlg("): ]
        failure = body.index('logSASAssertionEvent("SAS_ASSERT_FAILURE"')
        automatic = body.index("resolveSASAssertionSilentAction(")
        dialog = body.index("DisplayAssertDialog();")
        choice = body.index('logSASAssertionEvent("SAS_ASSERT_CHOICE"')
        self.assertLess(failure, automatic)
        self.assertLess(failure, dialog)
        self.assertLess(automatic, choice)
        self.assertLess(dialog, choice)

    def test_assertion_log_uses_menu_and_game_session_rollovers_without_gating(self):
        game = (ROOT / "CvGameCoreDLL/CvGame.cpp").read_text(encoding="utf-8")
        menu = (ROOT / "CvGameCoreDLL/CvInfo_Misc.cpp").read_text(encoding="utf-8")
        self.assertIn("startSASAssertionLogForNewGame();", game)
        self.assertIn("startSASAssertionLogForLoadedSave();", game)
        self.assertGreaterEqual(menu.count("startSASAssertionLogForMainMenu();"), 2)
        assertion_source = CPP.read_text(encoding="utf-8")
        self.assertIn('rollSASAssertionLog("menu", ++g_iSASAssertionMenuSequence);', assertion_source)
        self.assertIn('rollSASAssertionLog("new", ++g_iSASAssertionGameSequence);', assertion_source)
        self.assertIn('rollSASAssertionLog("load", ++g_iSASAssertionGameSequence);', assertion_source)
        self.assertIn("if (g_bSASAssertionMainMenuContext)", assertion_source)
        self.assertIn('record=SAS_ASSERT_METADATA', assertion_source)
        self.assertIn('appendSASAssertionText(kRow, " session=")', assertion_source)
        self.assertIn('appendSASAssertionText(kRow, " sessionSequence=")', assertion_source)
        self.assertIn("getSASDllRuntimeContextFields()", assertion_source)

        # <!-- custom: Heavy fixed identity belongs to SAS_ASSERT_METADATA; compact session/thread context stays on event rows for copied excerpts and multi-thread failures. (ChatGPT-5.6-Sol) -->
        event_body = assertion_source[assertion_source.index("void logSASAssertionEvent("):assertion_source.index("bool FAssertDlg(")]
        self.assertNotIn('appendSASAssertionText(kRow, " pid=")', event_body)
        self.assertNotIn('appendSASAssertionText(kRow, " processStartUtc=")', event_body)
        self.assertIn('appendSASAssertionText(kRow, " tid=")', event_body)
        self.assertIn('appendSASAssertionText(kRow, " session=")', event_body)
        self.assertIn('appendSASAssertionText(kRow, " sessionSequence=")', event_body)

    def test_runtime_assert_family_routes_through_fassertdlg(self):
        header = HEADER.read_text(encoding="utf-8")
        self.assertEqual(header.count("if (FAssertDlg("), 2)
        self.assertIn("#define FAssertBounds", header)
        self.assertIn("FAssertMsg(static_cast<int>(index)", header)
        self.assertIn("#define FAssertBOOL(i)", header)
        self.assertIn("FAssertBounds(0, 2, i)", header)
        self.assertIn("#define FErrorMsg(msg) FAssertMsg(false, msg)", header)


if __name__ == "__main__":
    unittest.main()
