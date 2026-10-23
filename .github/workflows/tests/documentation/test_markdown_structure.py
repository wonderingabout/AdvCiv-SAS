# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
from pathlib import Path
import sys
import unittest

# <!-- custom: Restore blocking checks in the automated subject folders; regression fixtures import those same helpers. (GPT-6.1-Sol) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/documentation"))
import markdown_structure as markdown
# <!-- custom: Exercise root-anchored destinations through the production link checker, including external and same-page exceptions. (GPT-6.1-Sol) -->
import markdown_links as links

class MarkdownTests(unittest.TestCase):
    def test_repository_root_link_policy(self):
        for destination in ('/README.md', '/Assets/XML/GlobalDefines_advciv_sas.xml#setting', '#menu', 'https://example.org/a', 'mailto:dev@example.org', '//example.org/a'):
            self.assertIsNone(links.root_link_error(destination), destination)
        for destination in ('README.md', '../README.md', 'revisions/SASRuntime.md#revision-6'):
            self.assertIn('repository-root', links.root_link_error(destination))

    # <!-- custom: Reproduce the missing-menu gap independently of the Inventory filename; exemptions require an explicit documented path/category. (GPT-6.1-Sol) -->
    def test_menu_required_unless_explicitly_exempt(self):
        text = '# Guide\n\nIntroduction.\n\n## First\n\nBody.\n\n### Detail\n\nMore.\n'
        self.assertTrue(markdown.menu_errors(text, document="new/place/guide.md"))
        self.assertTrue(markdown.menu_errors('# Short\n', document="new.md"))
        # <!-- custom: Reproduce the overbroad folder exemptions that hid missing menus in maintained migration/example guides. (GPT-6.1-Sol) -->
        for path in ("_1_AdvCiv-SAS/Docs/Deprecated/global_define_names.md", "_1_AdvCiv-SAS/Docs/Deprecated/new.md", "_1_AdvCiv-SAS/Docs/examples/runtime_status/README.md"):
            self.assertTrue(markdown.menu_errors(text, document=path))
        for path in ("LICENSE.md", ".github/workflows/build/README.md", "_1_AdvCiv-SAS/Docs/revisions/log.md"):
            self.assertEqual(markdown.menu_errors(text, document=path), [])
            self.assertEqual(markdown.render_menu(text, document=path), text)
        refreshed = markdown.render_menu(text, document="new/place/guide.md")
        self.assertEqual(markdown.menu_errors(refreshed, document="new/place/guide.md"), [])
        self.assertIn('Introduction.\n\n## Menu\n', refreshed)
        self.assertIn('- [First](#first)\n  - [Detail](#detail)', refreshed)
        self.assertTrue(refreshed.endswith('## First\n\nBody.\n\n### Detail\n\nMore.\n'))
        self.assertEqual(markdown.render_menu(refreshed, document="new/place/guide.md"), refreshed)
        malformed = refreshed.replace('- [First](#first)\n', '')
        self.assertTrue(markdown.menu_errors(malformed, document="LICENSE.md"))

    def test_menu_missing_title_and_hierarchy(self):
        valid = '# Doc\n\n## Menu\n\n[A](#a)\\\n&emsp;[B](#b)\n\n## A\n\n### B\n'
        self.assertEqual(markdown.menu_errors(valid), [])
        for broken in (valid.replace('&emsp;[B](#b)\n', ''), valid.replace('[A]', '[Wrong]'), valid.replace('&emsp;', ''), valid.replace('### B', '### C')):
            self.assertTrue(markdown.menu_errors(broken))

    def test_ki_stable_anchor_and_internal_subsections(self):
        valid = '# Issues\n## Menu\n[KI#457 - title](#ki-457)\n\n<a id="ki-457"></a>\n\n## KI#457 - title\n### Internal investigation\n'
        self.assertEqual(markdown.menu_errors(valid, True), [])
        self.assertIn('<a id="ki-457"></a>', markdown.render_menu(valid, True))
        self.assertTrue(markdown.menu_errors(valid.replace('[KI#457 - title](#ki-457)\n', ''), True))

    def test_explicit_html_anchor_policy(self):
        self.assertEqual(markdown.explicit_anchor_errors('<a id="ki-457"></a>\n## KI#457 - title\n', True), [])
        self.assertEqual(markdown.explicit_anchor_errors("<a name='ki-457.2'></a>\n## KI#457.2 - title\n", True), [])
        for text, known in (
            ('<a id="custom"></a>\n## Custom\n', False),
            ('<a name="custom"></a>\n## Custom\n', False),
            ('<a id="ki-457"></a>\n## Not known issues\n', False),
            ('<a id="not-a-ki"></a>\n## Known issues\n', True),
        ):
            with self.subTest(text=text, known=known):
                self.assertTrue(markdown.explicit_anchor_errors(text, known))
        self.assertEqual(markdown.explicit_anchor_errors('`<a id="example"></a>`\n\n```html\n<a id="example"></a>\n```\n'), [])

    def test_refresh_preserves_external_links_prose_and_body(self):
        text = '# D\n## Menu\nHere you go:\n[A](#a)\n[Guide](guide.md)\n\n## A\nBody.\n### B\n'
        refreshed = markdown.render_menu(text)
        self.assertIn('Here you go:', refreshed)
        self.assertIn('[Guide](guide.md)', refreshed)
        self.assertTrue(refreshed.endswith('## A\nBody.\n### B\n'))
        self.assertEqual(markdown.menu_errors(refreshed), [])
        self.assertEqual(markdown.render_menu(refreshed), refreshed)

    def test_other_document_fragment_does_not_satisfy_menu_coverage(self):
        text = '# D\n## Menu\n[A](other.md#a)\n\n## A\n'
        self.assertTrue(markdown.menu_errors(text, document='README.md'))
        refreshed = markdown.render_menu(text, document='README.md')
        self.assertIn('[A](other.md#a)', refreshed)
        self.assertEqual(markdown.menu_errors(refreshed, document='README.md'), [])

    def test_bold_code_comments_and_multiline(self):
        valid = '**good**\n\n`**code`\n\n<!-- **comment -->\n\n```python\n**code\n```\n\n**multi\nline**'
        self.assertEqual(markdown.bold_errors(valid), [])
        self.assertTrue(markdown.bold_errors('Intro\n\n**unclosed'))
        self.assertEqual(markdown.bold_errors(r'\*\*literal'), [])

    def test_redundant_final_hard_break_and_menu_refresh(self):
        redundant = '# D\n\n## Menu\n\n[A](#a)\\\n\n## A\n'
        self.assertTrue(markdown.redundant_hard_break_errors(redundant))
        refreshed = markdown.render_menu(redundant)
        self.assertEqual(markdown.redundant_hard_break_errors(refreshed), [])
        self.assertIn('[A](#a)\n\n## A\n', refreshed)

    def test_hard_break_escapes_and_inline_code_content(self):
        for count in (1, 2, 3, 4):
            text = 'Literal or break: ' + '\\' * count + '\n\n'
            with self.subTest(backslashes=count):
                self.assertEqual(bool(markdown.redundant_hard_break_errors(text)), count % 2 == 1)
        for text in ('First line\\\n`second line`\n', '`inline backslash: \\`\n\n', 'First line\\`code`\n\n', '```text\nbackslash\\\n\n```\n', '<!-- backslash\\\n\n-->\n', 'First line\\ \n\n'):
            with self.subTest(text=text):
                self.assertEqual(markdown.redundant_hard_break_errors(text), [])
        self.assertTrue(markdown.redundant_hard_break_errors('Final line\\'))


if __name__ == "__main__":
    unittest.main()
