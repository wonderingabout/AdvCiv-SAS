# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; tempfile isolates minimal unit, leader and civilization XML; unittest exercises both Barbarian balance rules. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Exercise the real XML readers and audits rather than duplicating them. (Claude code Opus 5.5) -->
import barbarian_balance as balance


def unit(unit_type, work_rate, unit_ai="UNITAI_WORKER", domain="DOMAIN_LAND"):
    return "<UnitInfo><Type>%s</Type><Domain>%s</Domain><DefaultUnitAI>%s</DefaultUnitAI><iWorkRate>%d</iWorkRate></UnitInfo>" % (unit_type, domain, unit_ai, work_rate)


def leader(leader_type, unit_prob):
    return "<LeaderHeadInfo><Type>%s</Type><iBuildUnitProb>%d</iBuildUnitProb></LeaderHeadInfo>" % (leader_type, unit_prob)


CIV_XML = """<Root>
<CivilizationInfo><Type>CIVILIZATION_BARBARIAN</Type><Units>
<Unit><UnitClassType>UNITCLASS_WORKER</UnitClassType><UnitType>UNIT_BARBARIAN_WORKER</UnitType></Unit>
</Units><Leaders><Leader><LeaderName>LEADER_BARBARIAN</LeaderName><bLeaderAvailability>1</bLeaderAvailability></Leader></Leaders></CivilizationInfo>
<CivilizationInfo><Type>CIVILIZATION_MAYA</Type><Units>
<Unit><UnitClassType>UNITCLASS_WORKER</UnitClassType><UnitType>UNIT_MAYA_QUICK_WORKER</UnitType></Unit>
</Units><Leaders><Leader><LeaderName>LEADER_PACAL</LeaderName><bLeaderAvailability>1</bLeaderAvailability></Leader></Leaders></CivilizationInfo>
</Root>"""


class BarbarianBalanceTests(unittest.TestCase):
    def repo(self, units_xml, leaders_xml):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        for path, text in ((balance.UNITS_PATH, "<Root>" + units_xml + "</Root>"), (balance.LEADERS_PATH, "<Root>" + leaders_xml + "</Root>"), (balance.CIVILIZATIONS_PATH, CIV_XML)):
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_text(text, encoding="utf-8")
        return root

    def workers(self, barbarian_rate, maya_rate, extra=""):
        root = self.repo(unit("UNIT_WORKER", 100) + unit("UNIT_MAYA_QUICK_WORKER", maya_rate) + unit("UNIT_BARBARIAN_WORKER", barbarian_rate) + extra, "")
        return balance.audit_barbarian_workers(root)

    def leaders(self, barbarian_prob, other_prob):
        root = self.repo("", leader("LEADER_BARBARIAN", barbarian_prob) + leader("LEADER_PACAL", other_prob))
        return balance.audit_barbarian_leaders(root)

    def test_worker_faster_than_every_worker_passes(self):
        self.assertEqual(self.workers(175, 125), ([], 1))

    def test_worker_equal_to_a_civ_specific_worker_fails(self):
        failures, _count = self.workers(125, 125)
        self.assertEqual(len(failures), 1)
        self.assertIn("UNIT_MAYA_QUICK_WORKER", failures[0])

    def test_worker_slower_than_generic_worker_fails(self):
        failures, _count = self.workers(90, 80)
        self.assertTrue(any("UNIT_WORKER iWorkRate 100" in failure for failure in failures))

    def test_work_boat_and_non_workers_are_ignored(self):
        extra = unit("UNIT_WORKBOAT", 500, unit_ai="UNITAI_WORKER_SEA", domain="DOMAIN_SEA") + unit("UNIT_SETTLER", 500, unit_ai="UNITAI_SETTLE")
        self.assertEqual(self.workers(175, 125, extra), ([], 1))

    def test_leader_unit_prob_higher_than_every_leader_passes(self):
        self.assertEqual(self.leaders(70, 50), ([], 1))

    def test_leader_unit_prob_equal_fails(self):
        failures, _count = self.leaders(50, 50)
        self.assertEqual(len(failures), 1)
        self.assertIn("LEADER_PACAL", failures[0])

    def test_missing_barbarian_leader_info_fails(self):
        root = self.repo("", leader("LEADER_PACAL", 50))
        failures, _count = balance.audit_barbarian_leaders(root)
        self.assertIn("LEADER_BARBARIAN has no LeaderHeadInfo", failures[0])


if __name__ == "__main__":
    unittest.main()
