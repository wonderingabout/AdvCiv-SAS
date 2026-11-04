# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; tempfile isolates the fixture XML and text; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Exercise the real XML scans and name lookup rather than duplicating them. (Claude code Opus 5.5) -->
import xml_display_order as order

TEXTS = (("TXT_KEY_A", "Mansa Musa"), ("TXT_KEY_B", "Mao Zedong"), ("TXT_KEY_C", "Lincoln"), ("TXT_KEY_USA", "United States"), ("TXT_KEY_ARABIA", "Arabia"))
TECHS = (("TECH_PHILOSOPHY", 6), ("TECH_CIVIL_SERVICE", 7))


class XmlDisplayOrderTests(unittest.TestCase):
    # <!-- custom: run_check takes leaders, civilizations, civics and religions separately, since the check covers all four lists; omitted lists are written empty. (Claude code Opus 5.5) -->
    def run_check(self, leaders=(), civs=(), civics=(), religions=()):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = {
                order.LEADER_INFOS: "".join(f"<LeaderHeadInfo><Type>{t}</Type><Description>{k}</Description></LeaderHeadInfo>\n" for t, k in leaders),
                order.CIV_INFOS: "".join(f"<CivilizationInfo><Type>{t}</Type><Description>TXT_KEY_X</Description><ShortDescription>{k}</ShortDescription></CivilizationInfo>\n" for t, k in civs),
                order.CIVIC_INFOS: "".join(f"<CivicInfo><Type>{t}</Type><CivicOptionType>{o}</CivicOptionType><TechPrereq>{p}</TechPrereq></CivicInfo>\n" for t, o, p in civics),
                order.RELIGION_INFOS: "".join(f"<ReligionInfo><Type>{t}</Type><TechPrereq>{p}</TechPrereq></ReligionInfo>\n" for t, p in religions),
                order.TECH_INFOS: "".join(f"<TechInfo><Type>{t}</Type><iGridX>{x}</iGridX></TechInfo>\n" for t, x in TECHS),
                order.TEXT_DIR + "/AdvCiv-SAS_main.xml": "<Civ4GameText>" + "".join(f"<TEXT><Tag>{k}</Tag><English>{n}</English></TEXT>" for k, n in TEXTS) + "</Civ4GameText>",
            }
            for rel_path, content in files.items():
                (root / rel_path).parent.mkdir(parents=True, exist_ok=True)
                (root / rel_path).write_text(content, encoding="utf-8")
            return order.check(root)

    def test_shown_names_in_order_pass(self):
        self.assertEqual(self.run_check(leaders=[("LEADER_BARBARIAN", "TXT_KEY_B"), ("LEADER_LINCOLN", "TXT_KEY_C"), ("LEADER_MANSA_MUSA", "TXT_KEY_A"), ("LEADER_CHINESE_LEADER", "TXT_KEY_B")]), [])

    def test_type_order_instead_of_name_order_fails(self):
        self.assertEqual(len(self.run_check(leaders=[("LEADER_CHINESE_LEADER", "TXT_KEY_B"), ("LEADER_LINCOLN", "TXT_KEY_C"), ("LEADER_MANSA_MUSA", "TXT_KEY_A")])), 1)

    def test_civilizations_follow_short_names(self):
        self.assertEqual(self.run_check(civs=[("CIVILIZATION_ARABIA", "TXT_KEY_ARABIA"), ("CIVILIZATION_AMERICA", "TXT_KEY_USA"), ("CIVILIZATION_BARBARIAN", "TXT_KEY_ARABIA")]), [])
        self.assertEqual(len(self.run_check(civs=[("CIVILIZATION_AMERICA", "TXT_KEY_USA"), ("CIVILIZATION_ARABIA", "TXT_KEY_ARABIA")])), 1)

    def test_civics_follow_tech_column_within_each_category(self):
        legal = "CIVICOPTION_LEGAL"
        self.assertEqual(self.run_check(civics=[("CIVIC_BARBARISM", legal, "NONE"), ("CIVIC_VASSALAGE", legal, "TECH_PHILOSOPHY"), ("CIVIC_BUREAUCRACY", legal, "TECH_CIVIL_SERVICE"), ("CIVIC_TRIBALISM", "CIVICOPTION_LABOR", "NONE")]), [])
        self.assertEqual(len(self.run_check(civics=[("CIVIC_BUREAUCRACY", legal, "TECH_CIVIL_SERVICE"), ("CIVIC_VASSALAGE", legal, "TECH_PHILOSOPHY")])), 1)

    def test_religions_follow_tech_column(self):
        self.assertEqual(self.run_check(religions=[("RELIGION_PAGANISM", "TECH_PHILOSOPHY"), ("RELIGION_ISLAM", "TECH_CIVIL_SERVICE")]), [])
        self.assertEqual(len(self.run_check(religions=[("RELIGION_ISLAM", "TECH_CIVIL_SERVICE"), ("RELIGION_PAGANISM", "TECH_PHILOSOPHY")])), 1)


if __name__ == "__main__":
    unittest.main()
