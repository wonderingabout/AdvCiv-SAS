# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Run the orphan image check on temporary files: named, %20-encoded, self-only, generated-corpus-only and binary-only references. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

# <!-- custom: Import the actual documentation checker; fixtures pass their own root and file list. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/documentation"))
import orphan_images


class OrphanImageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.files = {}

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
        self.files[name] = path

    def orphans(self):
        return orphan_images.orphan_images(self.root, orphan_images.repository_files(self.root))

    def test_named_and_encoded_references_pass(self):
        self.write("Images/a.png", b"img")
        self.write("Images/b (1).JPG", b"img")
        self.write("README.md", '<img src="/Images/b%20(1).JPG" alt="b (1).JPG" width="250">')
        self.write("tool.py", 'SHOT = "a.png"')
        self.assertEqual(self.orphans(), [])

    def test_unreferenced_image_fails(self):
        self.write("Images/a.png", b"img")
        self.write("README.md", "no images here")
        self.assertEqual(self.orphans(), ["Images/a.png"])

    def test_generated_corpus_and_binary_mentions_do_not_count(self):
        self.write("Images/a.png", b"img")
        self.write("LLM_Helpers/context/commit_diffs/x.diff", "+a.png")
        self.write("LLM_Helpers/outputs/review.md", "a.png")
        self.write("Assets/art.dds", b"a.png")
        self.write("blob.bin", b"a.png\0")
        self.assertEqual(self.orphans(), ["Images/a.png"])

    def test_svg_naming_itself_is_not_a_reference(self):
        self.write("Images/icon.svg", "<svg><title>icon.svg</title></svg>")
        self.assertEqual(self.orphans(), ["Images/icon.svg"])


if __name__ == "__main__":
    unittest.main()
