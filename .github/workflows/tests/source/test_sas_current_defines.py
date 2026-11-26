# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib finds the game module, sys and types stand in for the engine and the bridge, unittest runs the cases. See KI#128.5. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import types
import unittest

REPO_ROOT = Path(__file__).resolve().parents[4]
MODULE = REPO_ROOT / "Assets" / "Python" / "SASCurrentDefines.py"


class FakeGlobals:
	def __init__(self, values):
		self.values = values
		self.reads = 0

	def getDefineINT(self, name):
		self.reads += 1
		return self.values[name]


def load(values, bridge):
	# <!-- custom: Compiled from its text in memory with stand-in modules, so no .pyc lands in Assets and no engine is needed. (Claude code Opus 5.5) -->
	engine = types.ModuleType("CvPythonExtensions")
	fake = FakeGlobals(values)
	engine.CyGlobalContext = lambda: fake
	saved = {name: sys.modules.get(name) for name in ("CvPythonExtensions", "SASLiveDefineOverridesBridge")}
	sys.modules["CvPythonExtensions"] = engine
	sys.modules["SASLiveDefineOverridesBridge"] = bridge
	try:
		module = types.ModuleType("SASCurrentDefines_test")
		exec(compile(MODULE.read_text(encoding="utf-8"), str(MODULE), "exec"), module.__dict__)
	finally:
		for name, previous in saved.items():
			if previous is None:
				sys.modules.pop(name, None)
			else:
				sys.modules[name] = previous
	return module, fake


class SASCurrentDefinesTests(unittest.TestCase):
	def setUp(self):
		self.bridge = types.ModuleType("SASLiveDefineOverridesBridge")
		self.listeners = []
		self.bridge.addChangeListener = self.listeners.append
		self.values = {"SAS_A": 3}
		self.module, self.fake = load(self.values, self.bridge)

	def test_reads_once_while_nothing_changes(self):
		self.assertEqual([self.module.getInt("SAS_A") for _ in range(3)], [3, 3, 3])
		self.assertEqual(self.fake.reads, 1)

	def test_override_change_rereads(self):
		# <!-- custom: The bridge pushes an override, then calls its listeners; the next read must see the new value without the reader doing anything.
		# Since KI#128.9 the bridge calls the module rather than the module asking the change count at each read. (Claude code Opus 5.5) -->
		self.assertEqual(self.module.getInt("SAS_A"), 3)
		self.values["SAS_A"] = 4
		self.assertEqual(self.module.getInt("SAS_A"), 3)
		self.assertEqual(len(self.listeners), 1)
		for function in self.listeners:
			function()
		self.assertEqual(self.module.getInt("SAS_A"), 4)
		self.assertEqual(self.fake.reads, 2)


if __name__ == "__main__":
	unittest.main()
