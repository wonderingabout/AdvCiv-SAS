# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Exercise the production DotMap observer with isolated player/marker fixtures, including disabled pre-gating, per-viewer baselines, add/edit/remove deltas and visibility-only changes. (ChatGPT-5.6-Sol) -->
import builtins
import importlib.util
from pathlib import Path
import sys
import types
# <!-- custom: unittest keeps the planning-marker comparison contract testable without loading Civ4/BUG. (ChatGPT-5.6-Sol) -->
import unittest


REPO_ROOT = Path(__file__).resolve().parents[4]
ACTIONS_PATH = REPO_ROOT / "Assets" / "Python" / "SASGameRecordActions.py"
STRATEGY_PATH = REPO_ROOT / "Assets" / "Python" / "Contrib" / "CvStrategyOverlay.py"
EVENT_INTERFACE_PATH = REPO_ROOT / "Assets" / "Python" / "EntryPoints" / "CvEventInterface.py"


class FakeCity:
    def __init__(self, x, y, color, layer):
        self.point = (x, y)
        self.color = color
        self.layer = layer


class FakeDotMap:
    def __init__(self):
        self.visible = True
        self.cities = {}

    def hasCities(self, player):
        return player in self.cities

    def iterCities(self, player):
        return iter(self.cities.get(player, {}).values())

    def setCity(self, player, x, y, color, layer):
        self.cities.setdefault(player, {})[(x, y)] = FakeCity(x, y, color, layer)

    def removeCity(self, player, x, y):
        del self.cities[player][(x, y)]


class FakeGame:
    def __init__(self):
        self.viewer = 0
        self.summaries = []
        self.details = []

    def isFinalInitialized(self):
        return True

    def getActivePlayer(self):
        return self.viewer

    def logSASGameRecordDotMapSummary(self, *args):
        self.summaries.append(args)

    def logSASGameRecordDotMapMarker(self, *args):
        self.details.append(args)


class DotMapMarkerTests(unittest.TestCase):
    def setUp(self):
        self.old_unicode = getattr(builtins, "unicode", None)
        builtins.unicode = str
        self.saved_modules = {}
        for name in ("CvPythonExtensions", "SASGameRecordConfig", "SASPopupChoices"):
            self.saved_modules[name] = sys.modules.get(name)

        self.game = FakeGame()
        cv = types.ModuleType("CvPythonExtensions")
        cv.CyEngine = lambda: None
        cv.CyGame = lambda: self.game
        cv.FeatTypes = object()
        cv.OrderTypes = object()
        sys.modules["CvPythonExtensions"] = cv

        config = types.ModuleType("SASGameRecordConfig")
        config.getLogLevel = lambda: 2
        config.getActionTraceEnabled = lambda: True
        config.getMapAnnotationTextEnabled = lambda: False
        sys.modules["SASGameRecordConfig"] = config
        sys.modules["SASPopupChoices"] = types.ModuleType("SASPopupChoices")

        spec = importlib.util.spec_from_file_location("SASGameRecordActions_dotmap_test", ACTIONS_PATH)
        self.actions = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.actions)
        self.dotmap = FakeDotMap()

    def tearDown(self):
        for name, value in self.saved_modules.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value
        if self.old_unicode is None:
            del builtins.unicode
        else:
            builtins.unicode = self.old_unicode

    def test_disabled_recorder_skips_marker_collection(self):
        self.actions.SASGameRecordConfig.getLogLevel = lambda: 0

        class ExplodingDotMap:
            visible = True
            def hasCities(self, player):
                raise AssertionError("disabled observer traversed DotMap state")

        self.actions.observeDotMapMarkers(ExplodingDotMap(), "DISABLED")
        self.assertEqual(self.game.summaries, [])
        self.assertEqual(self.game.details, [])

    def test_snapshot_records_only_active_viewer_markers(self):
        self.dotmap.setCity(0, 43, 26, 4, 20)
        self.dotmap.setCity(1, 50, 23, 7, 30)
        self.actions.observeDotMapMarkers(self.dotmap, "ON_LOAD")

        self.assertEqual(self.game.summaries, [("SNAPSHOT", "ON_LOAD", 1, True, 0, 0, 0)])
        self.assertEqual(self.game.details, [("SNAPSHOT", "ON_LOAD", 0, 43, 26, -1, -1, 4, 20)])

    def test_add_edit_remove_emit_final_applied_state(self):
        self.dotmap.setCity(0, 43, 26, 4, 20)
        self.actions.observeDotMapMarkers(self.dotmap, "BASE")

        self.dotmap.setCity(0, 50, 23, 7, 30)
        self.actions.observeDotMapMarkers(self.dotmap, "MOD_NET_MESSAGE")
        self.assertEqual(self.game.summaries[-1][4:7], (1, 0, 0))
        self.assertEqual(self.game.details[-1], ("ADD", "MOD_NET_MESSAGE", 0, 50, 23, -1, -1, 7, 30))

        self.dotmap.setCity(0, 50, 23, 9, 30)
        self.actions.observeDotMapMarkers(self.dotmap, "MOD_NET_MESSAGE")
        self.assertEqual(self.game.summaries[-1][4:7], (0, 1, 0))
        self.assertEqual(self.game.details[-1], ("EDIT", "MOD_NET_MESSAGE", 0, 50, 23, 7, 30, 9, 30))

        self.dotmap.removeCity(0, 43, 26)
        self.actions.observeDotMapMarkers(self.dotmap, "MOD_NET_MESSAGE")
        self.assertEqual(self.game.summaries[-1][4:7], (0, 0, 1))
        self.assertEqual(self.game.details[-1], ("REMOVE", "MOD_NET_MESSAGE", 0, 43, 26, 4, 20, -1, -1))

    def test_visibility_change_alone_is_not_marker_change(self):
        self.dotmap.setCity(0, 43, 26, 4, 20)
        self.actions.observeDotMapMarkers(self.dotmap, "BASE")
        self.dotmap.visible = False
        self.actions.observeDotMapMarkers(self.dotmap, "ACTIVE_PLAYER_TURN_BEGIN")
        self.assertEqual(len(self.game.summaries), 1)
        self.assertEqual(len(self.game.details), 1)

    def test_active_viewers_have_independent_planning_baselines(self):
        self.dotmap.setCity(0, 43, 26, 4, 20)
        self.dotmap.setCity(1, 50, 23, 7, 30)
        self.actions.observeDotMapMarkers(self.dotmap, "PLAYER_0")
        self.game.viewer = 1
        self.actions.observeDotMapMarkers(self.dotmap, "PLAYER_1")
        self.assertEqual([row[0] for row in self.game.summaries], ["SNAPSHOT", "SNAPSHOT"])
        self.assertEqual([row[2] for row in self.game.details], [0, 1])

    def test_reset_session_forces_fresh_baseline(self):
        self.dotmap.setCity(0, 43, 26, 4, 20)
        self.actions.observeDotMapMarkers(self.dotmap, "BASE")
        self.actions.resetSession()
        self.actions.observeDotMapMarkers(self.dotmap, "PYTHON_RELOAD")
        self.assertEqual([row[0] for row in self.game.summaries], ["SNAPSHOT", "SNAPSHOT"])

    def test_production_hooks_observe_after_apply_and_session_baselines(self):
        strategy = STRATEGY_PATH.read_text(encoding="utf-8")
        add_start = strategy.index("\tdef addCityMessage")
        add_end = strategy.index("\n\tdef addCity(", add_start)
        add_block = strategy[add_start:add_end]
        self.assertLess(add_block.index("self.addCity(ePlayer, city)"), add_block.index("observeDotMapMarkers"))

        remove_start = strategy.index("\tdef removeCityMessage")
        remove_end = strategy.index("\n\tdef removeCity(", remove_start)
        remove_block = strategy[remove_start:remove_end]
        self.assertLess(remove_block.index("self.removeCity"), remove_block.index("observeDotMapMarkers"))

        event_interface = EVENT_INTERFACE_PATH.read_text(encoding="utf-8")
        self.assertIn('observeDotMapMarkers(CvStrategyOverlay.getDotMap(), szSettingsReason)', event_interface)
        self.assertIn('observeDotMapMarkers(CvStrategyOverlay.getDotMap(), "PYTHON_RELOAD")', event_interface)


if __name__ == "__main__":
    unittest.main()
