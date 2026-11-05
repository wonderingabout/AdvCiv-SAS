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
    # <!-- custom: run_check takes leaders, civilizations, civics, religions, units and buildings separately, since the check covers all of them; omitted lists are written empty, except religions, which default to the GameFont order. (Claude code Opus 5.5) -->
    def run_check(self, leaders=(), civs=(), civics=(), religions=None, units="", buildings=""):
        if religions is None:
            religions = [(religion, "NONE") for religion in order.GAMEFONT_RELIGION_ORDER]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = {
                order.LEADER_INFOS: "".join(f"<LeaderHeadInfo><Type>{t}</Type><Description>{k}</Description></LeaderHeadInfo>\n" for t, k in leaders),
                order.CIV_INFOS: "".join(f"<CivilizationInfo><Type>{t}</Type><Description>TXT_KEY_X</Description><ShortDescription>{k}</ShortDescription></CivilizationInfo>\n" for t, k in civs),
                order.CIVIC_INFOS: "".join(f"<CivicInfo><Type>{t}</Type><CivicOptionType>{o}</CivicOptionType><TechPrereq>{p}</TechPrereq></CivicInfo>\n" for t, o, p in civics),
                order.RELIGION_INFOS: "".join(f"<ReligionInfo><Type>{t}</Type><TechPrereq>{p}</TechPrereq></ReligionInfo>\n" for t, p in religions),
                order.UNIT_INFOS: "<Root>" + units + "</Root>",
                order.BUILDING_INFOS: "<Root>" + buildings + "</Root>",
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

    # <!-- custom: Religions keep their historical GameFont order, so a later founding tech must not force a reorder. (Claude code Opus 5.5) -->
    def test_religion_tech_columns_are_not_enforced(self):
        religions = [(religion, "TECH_CIVIL_SERVICE" if index == 0 else "TECH_PHILOSOPHY") for index, religion in enumerate(order.GAMEFONT_RELIGION_ORDER)]
        self.assertEqual(self.run_check(religions=religions), [])

    # <!-- custom: Religion icons come from GameFont.tga slots in XML order, so a reordered religion file must fail until the glyphs are moved too. (Claude code Opus 5.5) -->
    def test_religions_follow_gamefont_order(self):
        religions = [(religion, "NONE") for religion in order.GAMEFONT_RELIGION_ORDER]
        self.assertEqual(self.run_check(religions=religions), [])
        swapped = [religions[1], religions[0]] + religions[2:]
        self.assertTrue(any("GameFont glyph order" in failure for failure in self.run_check(religions=swapped)))

    # <!-- custom: Missionaries, religion buildings, executives and headquarters follow their religion or corporation order. (Claude code Opus 5.5) -->
    def test_linked_assets_follow_religion_and_corporation_order(self):
        religions = [(religion, "NONE") for religion in order.GAMEFONT_RELIGION_ORDER]
        def unit(info_type, tag, link):
            return f"<UnitInfo><Type>{info_type}</Type><{tag}>{link}</{tag}></UnitInfo>"
        units = unit("UNIT_PAGAN_MISSIONARY", "PrereqReligion", "RELIGION_PAGANISM") + unit("UNIT_HINDU_MISSIONARY", "PrereqReligion", "RELIGION_HINDUISM") + unit("UNIT_EXECUTIVE_1", "PrereqCorporation", "CORPORATION_1") + unit("UNIT_EXECUTIVE_2", "PrereqCorporation", "CORPORATION_2")
        buildings = "<BuildingInfo><Type>BUILDING_CORPORATION_2</Type><FoundsCorporation>CORPORATION_2</FoundsCorporation></BuildingInfo><BuildingInfo><Type>BUILDING_CORPORATION_1</Type><FoundsCorporation>CORPORATION_1</FoundsCorporation></BuildingInfo>"
        self.assertEqual(self.run_check(religions=religions, units=units), [])
        swapped_units = unit("UNIT_HINDU_MISSIONARY", "PrereqReligion", "RELIGION_HINDUISM") + unit("UNIT_PAGAN_MISSIONARY", "PrereqReligion", "RELIGION_PAGANISM")
        self.assertEqual(len(self.run_check(religions=religions, units=swapped_units)), 1)
        self.assertEqual(len(self.run_check(religions=religions, buildings=buildings)), 1)


if __name__ == "__main__":
    unittest.main()
