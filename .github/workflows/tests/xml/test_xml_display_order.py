# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; tempfile isolates the fixture leaders and text; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Exercise the real leader scan and name lookup rather than duplicating them. (Claude code Opus 5.5) -->
import xml_display_order as order


class XmlDisplayOrderTests(unittest.TestCase):
    def run_check(self, leaders):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            infos = root / order.LEADER_INFOS
            infos.parent.mkdir(parents=True)
            infos.write_text("".join(f"<LeaderHeadInfo><Type>{t}</Type><Description>{k}</Description></LeaderHeadInfo>\n" for t, k in leaders), encoding="utf-8")
            text = root / order.TEXT_DIR / "AdvCiv-SAS_main.xml"
            text.parent.mkdir(parents=True)
            text.write_text("<Civ4GameText>" + "".join(f"<TEXT><Tag>{k}</Tag><English>{n}</English></TEXT>" for k, n in (("TXT_KEY_A", "Mansa Musa"), ("TXT_KEY_B", "Mao Zedong"), ("TXT_KEY_C", "Lincoln"))) + "</Civ4GameText>", encoding="utf-8")
            return order.check(root)

    def test_shown_names_in_order_pass(self):
        self.assertEqual(self.run_check([("LEADER_BARBARIAN", "TXT_KEY_B"), ("LEADER_LINCOLN", "TXT_KEY_C"), ("LEADER_MANSA_MUSA", "TXT_KEY_A"), ("LEADER_CHINESE_LEADER", "TXT_KEY_B")]), [])

    def test_type_order_instead_of_name_order_fails(self):
        self.assertEqual(len(self.run_check([("LEADER_CHINESE_LEADER", "TXT_KEY_B"), ("LEADER_LINCOLN", "TXT_KEY_C"), ("LEADER_MANSA_MUSA", "TXT_KEY_A")])), 1)


if __name__ == "__main__":
    unittest.main()
