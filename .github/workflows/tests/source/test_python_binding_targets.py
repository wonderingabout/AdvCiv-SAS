# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and tempfile build a small DLL source tree, sys makes the checker importable and unittest checks each rule. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

# <!-- custom: Import the same source helper used by checks-source.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
import python_binding_targets as checker

HEADER = """
ENUM_START(Task, TASK)
	TASK_HURRY,
	TASK_CONSCRIPT,
ENUM_END(Task, TASK)
enum PlotStyleTypes { NO_PLOT_STYLE = -1, PLOT_STYLE_RIVER };
class CvInfoBase { int getText(); };
class CvEventInfo : public CvInfoBase { int getNumUnits(); };
class CvEventTriggerInfo : public CvInfoBase {
	int getBonusRequired();
	int getReligionRequired();
	//int getRetired();
	int pyGetWorldNews();
	int getWorldNews();
};
"""


class PythonBindingTargetsTests(unittest.TestCase):
    def errors(self, bindings):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "CvGameCoreDLL").mkdir()
            (root / "CvGameCoreDLL/CvEnums.h").write_text(HEADER, encoding="utf-8")
            path = root / "CvGameCoreDLL/CyTestInterface.cpp"
            path.write_text(bindings, encoding="utf-8")
            enumerators, classes, bases = checker.header_facts(root)
            return checker.binding_errors(path, "CyTestInterface.cpp", enumerators, classes, bases)

    def test_enum_bound_to_a_neighbour_fails(self):
        self.assertEqual(len(self.errors('.value("TASK_CONSCRIPT", TASK_HURRY)\n')), 1)
        self.assertEqual(self.errors('.value("TASK_CONSCRIPT", TASK_CONSCRIPT)\n'), [])

    def test_enum_rename_without_its_own_enumerator_passes(self):
        self.assertEqual(self.errors('.value("PLOT_STYLE_NONE", NO_PLOT_STYLE)\n'), [])

    def test_method_bound_past_its_own_namesake_fails_but_wrappers_and_retired_names_pass(self):
        owner = 'python::class_<CvEventTriggerInfo>("CvEventTriggerInfo")\n'
        self.assertEqual(len(self.errors(owner + '.def("getReligionRequired", &CvEventTriggerInfo::getBonusRequired, "int ()")\n')), 1)
        self.assertEqual(self.errors(owner + '.def("getWorldNews", &CvEventTriggerInfo::pyGetWorldNews, "int ()")\n'), [])
        self.assertEqual(self.errors(owner + '.def("getRetired", &CvEventTriggerInfo::getBonusRequired, "int ()")\n'), [])

    def test_method_of_an_unrelated_class_fails_but_a_base_class_passes(self):
        owner = 'python::class_<CvEventInfo, python::bases<CvInfoBase> >("CvEventInfo")\n'
        self.assertEqual(len(self.errors(owner + '.def("getNumUnits", &CvEventTriggerInfo::getBonusRequired, "int ()")\n')), 1)
        self.assertEqual(self.errors(owner + '.def("getText", &CvInfoBase::getText, "int ()")\n'), [])

    def test_commented_bindings_are_ignored(self):
        self.assertEqual(self.errors('//.value("TASK_CONSCRIPT", TASK_HURRY)\n'), [])


if __name__ == "__main__":
    unittest.main()
