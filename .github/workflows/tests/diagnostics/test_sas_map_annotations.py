# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Exercise the production annotation observer with isolated engine/config fixtures including disabled logging, hidden-state identity, caption edits and viewer isolation. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
import builtins
import importlib.util
from pathlib import Path
import sys
import types
# <!-- custom: unittest runs isolated production-observer cases without a Civ4 process. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
import unittest


REPO_ROOT = Path(__file__).resolve().parents[4]
ACTIONS_PATH = REPO_ROOT / "Assets" / "Python" / "SASGameRecordActions.py"


class FakePlot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def isNone(self):
        return False

    def getX(self):
        return self.x

    def getY(self):
        return self.y


class FakeSign:
    def __init__(self, x, y, owner, caption):
        self.plot = FakePlot(x, y)
        self.owner = owner
        self.caption = caption

    def getPlot(self):
        return self.plot

    def getPlayerType(self):
        return self.owner

    def getCaption(self):
        return self.caption


class FakeEngine:
    def __init__(self):
        self.signs = []

    def getNumSigns(self):
        return len(self.signs)

    def getSignByIndex(self, index):
        return self.signs[index]


class FakeGame:
    def __init__(self):
        self.viewer = 0
        self.summaries = []
        self.details = []

    def isFinalInitialized(self):
        return True

    def getActivePlayer(self):
        return self.viewer

    def logSASGameRecordMapAnnotationSummary(self, *args):
        self.summaries.append(args)

    def logSASGameRecordMapAnnotation(self, *args):
        self.details.append(args)


class MapAnnotationTests(unittest.TestCase):
    def setUp(self):
        self.old_unicode = getattr(builtins, "unicode", None)
        builtins.unicode = str
        self.saved_modules = {}
        for name in ("CvPythonExtensions", "SASGameRecordConfig", "SASPopupChoices"):
            self.saved_modules[name] = sys.modules.get(name)

        self.engine = FakeEngine()
        self.game = FakeGame()

        cv = types.ModuleType("CvPythonExtensions")
        cv.CyEngine = lambda: self.engine
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

        spec = importlib.util.spec_from_file_location("SASGameRecordActions_annotation_test", ACTIONS_PATH)
        self.actions = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.actions)

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

    def test_disabled_recorder_skips_engine_enumeration(self):
        self.actions.SASGameRecordConfig.getLogLevel = lambda: 0
        self.actions.CyEngine = lambda: (_ for _ in ()).throw(AssertionError("disabled observer enumerated signs"))
        self.actions.observeMapAnnotations([], "DISABLED")
        self.assertEqual(self.game.summaries, [])
        self.assertEqual(self.game.details, [])

    def test_hidden_cache_is_same_logical_annotation(self):
        self.engine.signs = [FakeSign(3, 4, 0, "road")]
        self.actions.observeMapAnnotations([], "BASE")
        self.assertEqual(len(self.game.summaries), 1)
        self.assertEqual(self.game.summaries[0][0], "SNAPSHOT")
        self.assertEqual(self.game.summaries[0][5:8], (0, 0, 0))  # <!-- custom: baseline totals are not add/edit/remove deltas (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->

        # <!-- custom: SAS hide/show removes the engine billboard but retains the same logical sign in its hidden cache. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
        self.engine.signs = []
        self.actions.observeMapAnnotations([(3, 4, 0, "road")], "HIDDEN")
        self.assertEqual(len(self.game.summaries), 1)
        self.assertEqual(len(self.game.details), 1)

    def test_caption_edit_emits_one_edit_without_text_by_default(self):
        self.engine.signs = [FakeSign(3, 4, 0, "road")]
        self.actions.observeMapAnnotations([], "BASE")
        self.engine.signs = [FakeSign(3, 4, 0, "river")]
        self.actions.observeMapAnnotations([], "TURN_BEGIN")

        self.assertEqual(len(self.game.summaries), 2)
        summary = self.game.summaries[-1]
        self.assertEqual(summary[0], "CHANGE")
        self.assertEqual(summary[6], 1)  # <!-- custom: edited (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->

        detail = self.game.details[-1]
        self.assertEqual(detail[0], "EDIT")
        self.assertEqual(detail[2:5], (0, 3, 4))
        self.assertTrue(detail[-1])  # <!-- custom: native bridge will serialize caption text as WITHHELD (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->

    def test_caption_opt_in_passes_utf8_bytes_to_native_bridge(self):
        self.actions.SASGameRecordConfig.getMapAnnotationTextEnabled = lambda: True
        self.engine.signs = [FakeSign(5, 6, 0, u"caf\u00e9")]
        self.actions.observeMapAnnotations([], "BASE")

        detail = self.game.details[-1]
        self.assertEqual(detail[0], "SNAPSHOT")
        self.assertEqual(detail[-2], "caf\u00e9".encode("utf-8"))
        self.assertFalse(detail[-1])

    def test_active_viewers_have_independent_baselines(self):
        self.engine.signs = [FakeSign(1, 2, 0, "a")]
        self.actions.observeMapAnnotations([], "PLAYER_0")
        self.game.viewer = 1
        self.engine.signs = []
        self.actions.observeMapAnnotations([], "PLAYER_1")

        self.assertEqual([row[0] for row in self.game.summaries], ["SNAPSHOT", "SNAPSHOT"])
        self.assertEqual(self.game.summaries[1][2], 0)  # <!-- custom: total, not a false REMOVE (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->

    def test_player_signs_are_filtered_to_active_viewer_but_landmarks_are_shared(self):
        self.engine.signs = [
            FakeSign(1, 1, 0, "mine"),
            FakeSign(2, 2, 1, "other"),
            FakeSign(3, 3, -1, "landmark"),
        ]
        self.actions.observeMapAnnotations([], "PLAYER_0")

        self.assertEqual(self.game.summaries[-1][2], 2)
        self.assertEqual(sorted((row[2], row[3], row[4]) for row in self.game.details), [(-1, 3, 3), (0, 1, 1)])


if __name__ == "__main__":
    unittest.main()
