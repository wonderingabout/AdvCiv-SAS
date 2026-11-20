# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Check that removing a real observer's registration or enabling its shipping control fails; this tests the new discovery policy without copying its whole inventory. (GPT-6.1-Sol) -->
# <!-- custom: pathlib/sys import the production checker; tempfile isolates the real-named observer/owner fixture, while unittest/mock temporarily remove its registration. (GPT-6.1-Sol) -->
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

# <!-- custom: Exercise the actual default-control inventory helper, not a second parser in the test. (GPT-6.1-Sol) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/diagnostics"))
import runtime_status


class RuntimeObserverControlTests(unittest.TestCase):
    def test_registration_and_disabled_control_are_required(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "Assets").mkdir()
            (root / "CvGameCoreDLL").mkdir()
            name = "SASRuntimeExitObserver.ps1"
            (root / "Assets" / name).write_text("# disposable fixture", encoding="utf-8")
            (root / "CvGameCoreDLL/SASRuntimeStatus.cpp").write_text('L"' + name + '"', encoding="utf-8")
            defines = {"SAS_RUNTIME_STATUS_ON": 0}
            # <!-- custom: Scope registration to the real component represented by this disposable repository. (GPT-6.1-Sol) -->
            patcher = mock.patch.object(runtime_status, "RUNTIME_COMPONENT_CONTROLS", {name: runtime_status.RUNTIME_COMPONENT_CONTROLS[name]})
            patcher.start()
            self.addCleanup(patcher.stop)
            self.assertEqual(runtime_status.observer_control_errors(root, defines), [])
            self.assertTrue(runtime_status.observer_control_errors(root, {"SAS_RUNTIME_STATUS_ON": 1}))
            with mock.patch.object(runtime_status, "RUNTIME_COMPONENT_CONTROLS", {}):
                self.assertTrue(runtime_status.observer_control_errors(root, defines))
            # <!-- custom: Renaming the same companion outside the old Observer suffix must not bypass discovery. (GPT-6.1-Sol) -->
            renamed = root / "Assets/ExitWatcher.ps1"
            (root / "Assets" / name).rename(renamed)
            self.assertTrue(runtime_status.observer_control_errors(root, defines))
            renamed.rename(root / "Assets" / name)
            (root / "CvGameCoreDLL/SASRuntimeStatus.cpp").write_text('// "' + name + '"', encoding="utf-8")
            self.assertTrue(runtime_status.observer_control_errors(root, defines))


if __name__ == "__main__":
    unittest.main()
