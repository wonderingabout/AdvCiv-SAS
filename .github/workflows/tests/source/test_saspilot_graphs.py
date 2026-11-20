# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Exercise SASPilot command module with small Civ4 API substitutes.
# The live DLL supplies these getters in game, but Linux CI can still verify the JSON relationships and the player-specific projections. (GPT-6.1-Sol) -->
from pathlib import Path
import runpy
import sys
from types import ModuleType, SimpleNamespace
# <!-- custom: unittest runs the graph tests, patch stands in for the game's modules, such as CvPythonExtensions, and ElementTree reads the XML the graphs are checked against. (Claude code Opus 5.5) -->
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[4]
COMMANDS = ROOT / "SASPilot/game/SASPilotCommands.py"


def infos(relative_path, element):
    return ET.parse(ROOT / "Assets/XML" / relative_path).getroot().findall(".//" + element)


def getter(rows, index):
    return SimpleNamespace(getType=lambda: rows[index].findtext("Type"), getDescription=lambda: rows[index].findtext("Type"))


class PilotGraphTests(unittest.TestCase):
    def setUp(self):
        extension = ModuleType("CvPythonExtensions")
        extension.CyGlobalContext = lambda: None
        extension.AutomateTypes = object()
        extension.TradeableItems = SimpleNamespace(TRADE_TECHNOLOGIES=1, TRADE_RESOURCES=2, TRADE_CIVIC=3, TRADE_RELIGION=4)
        with patch.dict(sys.modules, {"CvPythonExtensions": extension, "CvScreensInterface": ModuleType("CvScreensInterface")}):
            commands = runpy.run_path(str(COMMANDS))
        self.scope = commands["cmd_graph"].__globals__

    def test_tech_graph_preserves_all_and_any_prerequisites_from_xml(self):
        rows = infos("Technologies/CIV4TechInfos.xml", "TechInfo")
        names = [row.findtext("Type") for row in rows]
        groups = ("AndPreReqs", "OrPreReqs")

        def tech_info(index):
            row = rows[index]
            obj = getter(rows, index)
            for suffix, group in zip(("And", "Or"), groups):
                values = [names.index(value.text) for value in row.findall(group + "/PrereqTech") if value.text in names]
                setattr(obj, "getPrereq" + suffix + "Techs", lambda i, values=values: values[i] if i < len(values) else -1)
            obj.getResearchCost = lambda: int(row.findtext("iCost"))
            obj.getEra = lambda: -1
            obj.getGridX = lambda: int(row.findtext("iGridX"))
            obj.getGridY = lambda: int(row.findtext("iGridY"))
            obj.isDisable = obj.isRepeat = obj.isTrade = lambda: False
            return obj

        self.scope["gc"] = SimpleNamespace(getNumTechInfos=lambda: len(rows), getTechInfo=tech_info, getEraInfo=None,
            getNUM_AND_TECH_PREREQS=lambda: max(len(row.findall("AndPreReqs/PrereqTech")) for row in rows),
            getNUM_OR_TECH_PREREQS=lambda: max(len(row.findall("OrPreReqs/PrereqTech")) for row in rows))
        nodes = self.scope["_techNodes"]()
        for row, node in zip(rows, nodes):
            self.assertEqual(row.findtext("Type"), node["type"])
            for group, key in zip(groups, ("all", "any")):
                self.assertEqual(sorted({value.text for value in row.findall(group + "/PrereqTech") if value.text in names}), node["requires"][key])
        self.assertIs(self.scope["_techNodes"](), nodes)

    def test_promotion_graph_keeps_the_third_or_prerequisite_and_reverse_links(self):
        names = ["PROMOTION_ROOT", "PROMOTION_LEFT", "PROMOTION_MIDDLE", "PROMOTION_RIGHT", "PROMOTION_TARGET"]

        def promotion(index):
            prereqs = [-1, -1, -1, -1] if index != 4 else [0, 1, 2, 3]
            return SimpleNamespace(getType=lambda: names[index], getDescription=lambda: names[index],
                getPrereqPromotion=lambda: prereqs[0], getPrereqOrPromotion1=lambda: prereqs[1],
                getPrereqOrPromotion2=lambda: prereqs[2], getPrereqOrPromotion3=lambda: prereqs[3],
                getTechPrereq=lambda: -1, getStateReligionPrereq=lambda: -1, isLeader=lambda: False)

        self.scope["gc"] = SimpleNamespace(getNumPromotionInfos=lambda: len(names), getPromotionInfo=promotion,
            getNumUnitCombatInfos=lambda: 0, getTechInfo=None, getReligionInfo=None, getUnitCombatInfo=None)
        graph = self.scope["_checkedHandler"]("graph", {"kind": "promotions", "type": names[4]})
        self.assertEqual({"all": [names[0]], "any": sorted(names[1:4])},
            graph({"kind": "promotions", "type": names[4]})["nodes"][0]["requires"])
        self.assertEqual([{"type": names[4], "group": "any"}], graph({"kind": "promotions", "type": names[3]})["requiredBy"])

    def test_upgrade_graph_resolves_targets_for_each_civilization(self):
        names = ["UNIT_SCOUT", "UNIT_EXPLORER", "UNIT_UNIQUE_EXPLORER"]
        civs = [SimpleNamespace(getCivilizationUnits=lambda i: i),
            SimpleNamespace(getCivilizationUnits=lambda i: (0, 2)[i])]

        def unit(index):
            return SimpleNamespace(getType=lambda: names[index], getDescription=lambda: names[index],
                getPrereqBuilding=lambda: -1, getPrereqCorporation=lambda: -1, getUnitClassType=lambda: min(index, 1),
                getUpgradeUnitClass=lambda target: index == 0 and target == 1)

        self.scope["_assetRequirements"] = lambda info, kind: {"techAll": []}
        self.scope["gc"] = SimpleNamespace(getCivilizationInfo=lambda i: civs[i], getNumUnitClassInfos=lambda: 2,
            getUnitInfo=unit, getBuildingInfo=None, getCorporationInfo=None, getUnitClassInfo=lambda i: SimpleNamespace(getType=lambda: str(i)))
        self.assertEqual([names[1]], self.scope["_upgradeNodes"](0)[0]["upgradesTo"])
        self.assertEqual([names[2]], self.scope["_upgradeNodes"](1)[0]["upgradesTo"])

    def test_relations_graph_dispatch_and_directed_vassalage(self):
        self.scope["cmd_relations"] = lambda args: {"viewer": args["player"], "graphRequested": args["graph"]}
        result = self.scope["cmd_graph"]({"kind": "relations", "player": 1})
        self.assertEqual({"viewer": 1, "graphRequested": True, "kind": "relations"}, result)
        master = SimpleNamespace(getID=lambda: 0, isVassal=lambda i: False, isOpenBorders=lambda i: True, isDefensivePact=lambda i: False)
        vassal = SimpleNamespace(getID=lambda: 1, isVassal=lambda i: i == 0, isOpenBorders=lambda i: True, isDefensivePact=lambda i: False)
        edge = {}
        self.scope["_addRelationLink"](edge, vassal, master)
        self.assertEqual({"sameTeam": False, "vassalOfTarget": True, "openBorders": True, "defensivePact": False}, edge)
        self.scope["_addRelationLink"](edge, master, vassal)
        self.assertFalse(edge["vassalOfTarget"])

    def test_history_respects_contact_and_demographics(self):
        viewer = SimpleNamespace(getTeam=lambda: 0, canSeeDemographics=lambda i: i == 1,
            hasEverSeenDemographics=lambda i: i in (1, 2))
        team = SimpleNamespace(isHasMet=lambda i: i < 4, getHasMetTurn=lambda i: 27)
        self.scope["gc"] = SimpleNamespace(getTeam=lambda i: team)
        start = self.scope["_historyStart"]

        def rival(i):
            return SimpleNamespace(getTeam=lambda: i, getID=lambda: i)

        self.assertEqual(10, start(viewer, rival(1), "power", 10, 45, True, True))
        self.assertIsNone(start(viewer, rival(2), "power", 10, 45, True, True))
        self.assertEqual(10, start(viewer, rival(2), "score", 10, 45, True, False))
        self.assertIsNone(start(viewer, rival(3), "score", 10, 31, True, True))
        self.assertEqual(27, start(viewer, rival(3), "score", 10, 32, True, True))
        self.assertIsNone(start(viewer, rival(4), "score", 10, 45, True, True))

    def test_grid_links_wrap_and_only_join_tiles_in_the_snapshot(self):
        kmap = SimpleNamespace(getGridWidth=lambda: 6, getGridHeight=lambda: 5,
            isWrapX=lambda: True, isWrapY=lambda: False)
        self.assertEqual((0, 0, 5, 4), self.scope["_gridBounds"](kmap, {}))
        self.assertEqual((2, 1, 5, 4), self.scope["_gridBounds"](kmap, {"box": [2, 1, 5, 4]}))
        with self.assertRaises(ValueError):
            self.scope["_gridBounds"](kmap, {"box": [2, 1, 6, 4]})
        plot = SimpleNamespace(isTradeNetworkConnected=lambda other, team: team == 3)
        result = self.scope["_gridTradeLinks"](kmap, {(0, 2): plot, (5, 2): plot, (2, 2): plot}, 3)
        self.assertEqual([{"from": [5, 2], "to": [0, 2], "step": [1, 0]}], result)

    def test_grid_hides_unseen_current_state_and_trade_links(self):
        class Info:
            def getType(self):
                return "SAMPLE"

        def info(_):
            return Info()

        def plot(x, y):
            def to_fail():
                raise AssertionError("hidden current state was read")
            return SimpleNamespace(isRevealed=lambda team, debug: x == 0, isVisible=lambda team, debug: False,
                getRevealedOwner=lambda team, debug: -1, getRevealedImprovementType=lambda team, debug: 0,
                getRevealedRouteType=lambda team, debug: -1, getTerrainType=lambda: 0,
                isHills=lambda: True, isPeak=lambda: False, isWater=lambda: False, getOwner=to_fail,
                getImprovementType=to_fail, getRouteType=to_fail, getFeatureType=lambda: 0, getBonusType=lambda team: -1, isCity=to_fail,
                isTradeNetwork=lambda team: to_fail())

        player = SimpleNamespace(getTeam=lambda: 3, getID=lambda: 0)
        kmap = SimpleNamespace(getGridWidth=lambda: 2, getGridHeight=lambda: 1, isWrapX=lambda: False,
            isWrapY=lambda: False, plot=plot)
        game = SimpleNamespace(getGameTurn=lambda: 10)
        self.scope.update({"_player": lambda args: player, "_requireOwnTeamUnderFog": lambda *unused: None,
            "_fogTeam": lambda args: 3, "gc": SimpleNamespace(getGame=lambda: game, getMap=lambda: kmap,
                getBonusInfo=info, getTerrainInfo=info, getImprovementInfo=info, getRouteInfo=info)})
        # <!-- custom: Feature and resource are given off sight too, as the window draws them on fogged plots (Claude code Opus 5.5, 2026-11-14); owner, improvement and route stay the remembered ones. (GPT-6.1-Sol + Claude code Opus 5.5) -->
        self.scope["gc"].getFeatureInfo = info
        reply = self.scope["cmd_grid"]({})
        self.assertEqual([{"x": 0, "y": 0, "visible": False, "owner": -1, "feature": "SAMPLE", "bonus": None, "terrain": "SAMPLE", "hill": True,
            "peak": False, "water": False, "improvement": "SAMPLE", "route": None}], reply["tiles"])
        self.assertEqual([], reply["tradeLinks"])

    def test_grid_fog_edge_gives_only_water_of_unrevealed_neighbors(self):
        # <!-- custom: The fog edge gives land or water for an unrevealed plot beside a revealed one, as the coastline art shows, and nothing for one two plots away; nothing else of it is read. (Claude code Opus 5.5) -->
        def plot(x, y):
            def to_fail(*unused):
                raise AssertionError("hidden state other than water was read")
            return SimpleNamespace(isRevealed=lambda team, debug: x == 0, isVisible=lambda team, debug: False,
                getRevealedOwner=lambda team, debug: -1, getRevealedImprovementType=lambda team, debug: -1,
                getRevealedRouteType=lambda team, debug: -1, getTerrainType=lambda: -1,
                isHills=lambda: False, isPeak=lambda: False, isWater=lambda: x == 1,
                getFeatureType=lambda: (x == 0 and -1) or to_fail(), getBonusType=lambda team: (x == 0 and -1) or to_fail(), getOwner=to_fail)

        kmap = SimpleNamespace(getGridWidth=lambda: 3, getGridHeight=lambda: 1, isWrapX=lambda: False,
            isWrapY=lambda: False, plot=plot)
        game = SimpleNamespace(getGameTurn=lambda: 2)
        self.scope.update({"_player": lambda args: SimpleNamespace(getTeam=lambda: 0, getID=lambda: 0),
            "_requireOwnTeamUnderFog": lambda *unused: None, "_fogTeam": lambda args: 0,
            "_typeOrNone": lambda getter, value: None,
            "gc": SimpleNamespace(getGame=lambda: game, getMap=lambda: kmap, getBonusInfo=None,
                getTerrainInfo=None, getImprovementInfo=None, getRouteInfo=None, getFeatureInfo=None)})
        self.assertEqual([{"x": 1, "y": 0, "water": True}], self.scope["cmd_grid"]({})["fogEdge"])
        self.assertEqual([], self.scope["cmd_grid"]({"edge": 0})["fogEdge"])

    def test_plot_query_uses_a_unit_anchor_and_preserves_the_fog_argument(self):
        self.scope["_player"] = lambda args: "owner"
        with patch.dict(self.scope, {"_requireOwnTeamUnderFog": lambda args, player, what: self.assertEqual("owner", player),
                "_unit": lambda args: SimpleNamespace(plot=lambda: SimpleNamespace(getX=lambda: 4, getY=lambda: 9)),
                "_fogTeam": lambda args: 2, "_plotsJson": lambda x, y, radius, team: str((x, y, radius, team))}):
            self.assertEqual("(4, 9, 2, 2)", self.scope["cmd_plots"]({"unit": 7, "radius": 2}).text)
            with self.assertRaises(ValueError):
                self.scope["cmd_plots"]({"unit": 7, "x": 4, "y": 9})
