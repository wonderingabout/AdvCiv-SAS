# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Exercise production local-image validation with temporary files, including filename/width regressions, reference syntax, encoded paths and literal examples. (GPT-6.1-Sol) -->
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

# <!-- custom: Import the actual documentation checker; fixtures replace only its repository root so no real images are changed. (GPT-6.1-Sol) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/documentation"))
import markdown_images as images


class ImageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        (self.root / "shot.png").write_bytes(b"fixture")
        self.root_patch = patch.object(images, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def check(self, text):
        return images.image_errors(self.root / "guide.md", text)

    def test_valid_html_widths_and_attribute_forms(self):
        for text in (
            '<img src="/shot.png" alt="shot.png" width="250"></img>',
            "<img WIDTH='640' ALT='shot.png' SRC='/shot.png' />",
            '<img\n width="320" alt="shot.png"\n src="/shot.png">',
        ):
            with self.subTest(text=text):
                self.assertEqual(self.check(text), ([], 1))

    def test_filename_decoding_and_html_entities(self):
        (self.root / "0.291_map & text (1).PNG").write_bytes(b"fixture")
        self.assertEqual(self.check('<img src="/0.291_map%20%26%20text%20(1).PNG?preview=1#top" alt="0.291_map &amp; text (1).PNG" width="250">'), ([], 1))

    def test_missing_descriptive_and_stale_alt_fail(self):
        for alt in ('', ' alt="a useful screenshot"', ' alt="old.png"', ' alt="/shot.png"', ' alt="shot.PNG"'):
            with self.subTest(alt=alt):
                errors, count = self.check('<img src="/shot.png" width="250"' + alt + '>')
                self.assertEqual(count, 1)
                self.assertTrue(any("alt must equal filename" in error for error in errors), errors)

    def test_missing_and_nonpositive_width_fail(self):
        for width in ('', ' width=""', ' width="0"', ' width="-1"', ' width="50%"', ' width="250px"'):
            with self.subTest(width=width):
                errors, _ = self.check('<img src="/shot.png" alt="shot.png"' + width + '>')
                self.assertTrue(any("positive pixel width" in error for error in errors), errors)

    def test_inline_and_reference_markdown_images_fail(self):
        for text in (
            '![shot.png](/shot.png)',
            '![shot.png][photo]\n\n[photo]: /shot.png',
            '![shot.png][]\n\n[shot.png]: /shot.png',
            '![shot.png]\n\n[shot.png]: /shot.png',
        ):
            with self.subTest(text=text):
                errors, count = self.check(text)
                self.assertEqual(count, 1)
                self.assertTrue(any("instead of Markdown image syntax" in error for error in errors), errors)

    def test_missing_and_escaping_files_still_fail(self):
        errors, _ = self.check('<img src="/missing.png" alt="missing.png" width="250">')
        self.assertTrue(any("missing local image" in error for error in errors), errors)
        errors, _ = self.check('<img src="/../outside.png" alt="outside.png" width="250">')
        self.assertTrue(any("escapes repository" in error for error in errors), errors)

    def test_code_comments_remote_images_and_ordinary_links_are_ignored(self):
        self.assertEqual(self.check('```html\n<img src="/missing.png">\n```\n`![literal](/missing.png)`\n<!-- <img src="/missing.png"> -->\n![badge](https://example.org/status)\n<img src="https://example.org/image">\n[ordinary link](/shot.png)'), ([], 0))

    def test_html_parser_keeps_attributes_after_quoted_greater_than(self):
        errors, _ = self.check('<img src="/shot.png" alt="description > filename" width="250">')
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("alt must equal filename", errors[0])


if __name__ == "__main__":
    unittest.main()
