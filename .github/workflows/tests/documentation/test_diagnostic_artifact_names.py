# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Check the two real filename-construction forms and hidden/sample-only mentions; do not mirror the current list of generated artifacts in a second schema. (GPT-6.1-Sol) -->
# <!-- custom: pathlib/sys locate the production documentation helper; unittest exercises extraction and visible-path matching without game/build dependencies. (GPT-6.1-Sol) -->
from pathlib import Path
import sys
import unittest

# <!-- custom: Import the real scoped checker rather than duplicating its discovery logic in this fixture. (GPT-6.1-Sol) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/documentation"))
import diagnostic_artifact_names as names


class DiagnosticArtifactNameTests(unittest.TestCase):
    def test_native_and_concatenated_names_preserve_extension(self):
        self.assertEqual(names.runtime_paths('"SASRuntimeStatus.json"; "SASRuntimeHistory_%s.jsonl"'),
                         {"Logs/SASRuntimeStatus.json", "Logs/SASRuntimeHistory_*.jsonl"})
        self.assertEqual(names.runtime_paths("'SASRuntimeExit_' + $runId + '.json'"), {"Logs/SASRuntimeExit_*.json"})
        self.assertEqual(names.runtime_paths('"settings.json"'), set())

    def test_samples_or_bare_filename_do_not_replace_visible_location(self):
        path = "Logs/SASRuntimeExit_*.json"
        for text in ('```text\n`' + path + '`\n```', '<!-- `' + path + '` -->', '`SASRuntimeExit_*.json`'):
            self.assertEqual(names.missing_paths({path}, text), [path])
        self.assertEqual(names.missing_paths({path}, "Output: `" + path + "`."), [])


if __name__ == "__main__":
    unittest.main()
