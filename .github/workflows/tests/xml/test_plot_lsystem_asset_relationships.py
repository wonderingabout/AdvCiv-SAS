# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; tempfile isolates minimal PlotLSystem, BonusInfo and ImprovementInfo fixtures; unittest pins the active bonus/improvement relationship rule. (ChatGPT-5.6-Sol) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Exercise the real PlotLSystem and ImprovementInfos scans rather than duplicating them. (Claude code Opus 5.5) -->
import plot_lsystem_asset_relationships as plot_rel


BONUS_XML = """<Root>
<BonusInfo><Type>BONUS_WINE</Type></BonusInfo>
</Root>"""
IMPROVEMENT_XML = """<Root>
<ImprovementInfo><Type>IMPROVEMENT_FARM</Type><BonusTypeStructs/></ImprovementInfo>
<ImprovementInfo><Type>IMPROVEMENT_PLANTATION</Type><BonusTypeStructs><BonusTypeStruct><BonusType>BONUS_WINE</BonusType></BonusTypeStruct></BonusTypeStructs></ImprovementInfo>
</Root>"""


class PlotLSystemAssetRelationshipTests(unittest.TestCase):
    def run_check(self, improvement, bonus="BONUS_WINE"):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = {
                plot_rel.BONUS_INFOS_REL_PATH: BONUS_XML,
                plot_rel.IMPROVEMENT_INFOS_REL_PATH: IMPROVEMENT_XML,
                plot_rel.PLOT_LSYSTEM_REL_PATH: """<LSystemInfos xmlns=\"x-schema:CIV4LSystemSchema.xml\"><LProduction From=\"Node\"><Attribute Class=\"Improvement\">%s</Attribute><Attribute Class=\"Bonus\">%s</Attribute></LProduction></LSystemInfos>""" % (improvement, bonus),
            }
            for rel_path, content in files.items():
                path = root / rel_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            return plot_rel.check(root)

    def test_current_relationship_passes(self):
        self.assertEqual(self.run_check("IMPROVEMENT_PLANTATION"), [])

    def test_stale_relationship_fails(self):
        failures = self.run_check("IMPROVEMENT_FARM")
        self.assertEqual(len(failures), 1)
        self.assertIn("IMPROVEMENT_FARM + BONUS_WINE", failures[0])

    def test_unused_graphical_bonus_is_ignored(self):
        self.assertEqual(self.run_check("IMPROVEMENT_FARM", "BONUS_COTTON"), [])

    def test_negated_selector_does_not_assert_relationship(self):
        self.assertEqual(self.run_check("!IMPROVEMENT_FARM"), [])

    # <!-- custom: The 2026-11-04 Grapes fix left BLeaf_4x3's goal ArtRef on Farm while only Plantation productions reached it. See KI#1074. (Claude code Opus 5.5) -->
    def test_art_unreachable_by_incoming_improvements_fails(self):
        def tree(art_improvement):
            return plot_rel.ET.ElementTree(plot_rel.ET.fromstring(f"""<LSystemInfos><LProduction From="Node"><Attribute Class="Improvement">IMPROVEMENT_PLANTATION</Attribute><To Name="Leaf"/></LProduction><LNode Name="Leaf"><ArtRef Name="goal"><Attribute Class="Improvement">{art_improvement}</Attribute></ArtRef></LNode></LSystemInfos>"""))
        self.assertEqual(plot_rel.check_unreachable_art(tree("IMPROVEMENT_PLANTATION")), [])
        self.assertEqual(len(plot_rel.check_unreachable_art(tree("IMPROVEMENT_FARM"))), 1)


if __name__ == "__main__":
    unittest.main()
