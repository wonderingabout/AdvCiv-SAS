# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Keep the selective SAS GlobalDefines promotion source-derived: names live only in CvGlobals.h, and CI verifies that promoted settings really have shared enum-backed consumers instead of drifting back to string/local caches. (ChatGPT-5.6-Sol) -->
# <!-- custom: re extracts macro/getter tokens, Counter counts references, pathlib reads current source, and unittest checks the source-derived invariants without maintaining a second define inventory. (GPT-6.1-Sol) -->
import re
from collections import Counter
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[4]
CPP_ROOT = REPO_ROOT / "CvGameCoreDLL"
GLOBALS_HEADER = CPP_ROOT / "CvGlobals.h"


def _cpp_sources():
    for path in sorted(CPP_ROOT.iterdir()):
        if path.suffix.lower() in (".cpp", ".h"):
            yield path


def _shared_define_names():
    source = GLOBALS_HEADER.read_text(encoding="latin-1")
    match = re.search(
        r"#define\s+DO_FOR_EACH_SAS_SHARED_GLOBAL_DEFINE\(DO\)\s+\\\s*\n(.*?)\n\s*#define\s+DO_FOR_EACH_GLOBAL_DEFINE\(DO\)",
        source,
        re.S,
    )
    if not match:
        raise AssertionError("Could not find DO_FOR_EACH_SAS_SHARED_GLOBAL_DEFINE")
    return re.findall(r"\bDO\((SAS_[A-Z0-9_]+)\)", match.group(1))


class SASSharedGlobalDefineCacheTests(unittest.TestCase):
    def test_shared_define_macro_is_nonempty_unique_and_included_once(self):
        names = _shared_define_names()
        self.assertTrue(names)
        self.assertEqual(len(names), len(set(names)), "duplicate shared SAS GlobalDefine")

        source = GLOBALS_HEADER.read_text(encoding="latin-1")
        self.assertEqual(
            source.count("DO_FOR_EACH_SAS_SHARED_GLOBAL_DEFINE(DO)"),
            2,
            "shared SAS macro should appear once in its definition and once in AdvCiv's DO_FOR_EACH_GLOBAL_DEFINE",
        )

    def test_promoted_defines_have_multiple_enum_backed_consumers(self):
        counts = Counter()
        pattern = re.compile(r"\bGC\.getDefine(?:INT|BOOL)\(CvGlobals::(SAS_[A-Z0-9_]+)\)")
        for path in _cpp_sources():
            counts.update(pattern.findall(path.read_text(encoding="latin-1")))
        failures = [
            "%s has only %d enum-backed consumer(s)" % (name, counts[name])
            for name in _shared_define_names() if counts[name] < 2
        ]
        self.assertEqual(failures, [], "\n".join(failures))

    def test_promoted_defines_do_not_keep_string_or_local_static_caches(self):
        names = set(_shared_define_names())
        source = "\n".join(path.read_text(encoding="latin-1") for path in _cpp_sources())
        string_names = set(re.findall(r"\bGC\.getDefine(?:INT|BOOL)\(\s*[\"'](SAS_[A-Z0-9_]+)[\"']", source))
        static_names = set(re.findall(
            r"\bstatic\b[^;\n]*\bGC\.getDefine(?:INT|BOOL)\(CvGlobals::(SAS_[A-Z0-9_]+)\)", source
        ))
        failures = []
        for name in sorted(names & string_names):
            failures.append("%s still has a string-backed getter" % name)
        for name in sorted(names & static_names):
            failures.append("%s wraps the shared enum cache in another local static" % name)
        self.assertEqual(failures, [], "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
