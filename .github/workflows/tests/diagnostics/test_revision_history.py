# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: Locate the shared workflow library and exercise both accepted Markdown explanations and misleading metadata/example-only entries without involving a game build. (GPT-6.1-Sol) -->
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / '.github/workflows/lib'))
# <!-- custom: Test the production parser and explanation guard shared by both recorder checks, rather than duplicating their Markdown rules in the fixture. (GPT-6.1-Sol) -->
# <!-- custom: functional_errors and change_layout_errors added on 2026-11-25, beside change_errors, for the Functional label and entry layout tests below. (Claude code Opus 5.5) -->
from revision_history import change_errors, change_layout_errors, functional_errors, revision_entries


class RevisionExplanationTests(unittest.TestCase):
    def test_single_line_and_continued_explanations(self):
        for explanation in ('Fixed recorder timing.', '\n  Fixed recorder timing.', '\n\n  - Fixed recorder timing.'):
            with self.subTest(explanation=explanation):
                self.assertEqual(change_errors('### Revision 2\n- **Change:** ' + explanation), [])

    def test_metadata_empty_comments_and_empty_bullets_do_not_explain(self):
        for explanation in ('', '- **Change:** ', '- **Change:** <!-- later -->', '- **Change:**\n  - '):
            with self.subTest(explanation=explanation):
                text = '### Revision 2\n- **Date:** 2026-10-19\n' + explanation + '\n- **Git commit:** pending\n'
                self.assertEqual(change_errors(text), ['revision 2: missing nonempty Change explanation'])

    def test_neighboring_entry_and_template_do_not_supply_missing_text(self):
        text = '### Revision 2\n- **Change:**\n### Revision 1\n- **Change:** Earlier fix.\n## Maintenance\n```markdown\n### Revision 3\n- **Change:** Example only.\n```\n'
        self.assertEqual([number for number, _body in revision_entries(text)], [2, 1])
        self.assertEqual(change_errors(text, 2), ['revision 2: missing nonempty Change explanation'])
        self.assertEqual(change_errors(text, 3), ['revision 3: missing corresponding history entry'])
        self.assertEqual(change_errors(text, 1), [])

    def test_fenced_or_commented_entries_do_not_count(self):
        text = '<!--\n### Revision 4\n- **Change:** Hidden.\n-->\n~~~~markdown\n### Revision 3\n- **Change:** Fixture.\n~~~~\n### Revision 2\n- **Change:** Real explanation.\n'
        self.assertEqual([number for number, _body in revision_entries(text)], [2])
        self.assertEqual(change_errors(text), [])


# <!-- custom: The Functional label added on 2026-11-25: exactly one Yes or No line per entry, with an optional reason; the last three cases are Codex's reproductions against the first version (GPT-6.2-Sol). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
class FunctionalLabelTests(unittest.TestCase):
    ERROR = 'revision 2: needs exactly one "- **Functional:** Yes" or "- **Functional:** No (brief reason)" line'

    def test_yes_and_no_pass(self):
        for value in ('Yes', 'Yes (new rows)', 'No (comments only)'):
            with self.subTest(value=value):
                self.assertEqual(functional_errors('### Revision 2\n- **Functional:** ' + value + '\n- **Change:** Fix.\n'), [])

    def test_missing_or_other_value_fails(self):
        for line in ('', '- **Functional:**\n', '- **Functional:** Maybe\n', '- **Functional:** yes\n', '- **Functional:** Yes/No\n', '- **Functional:** No\n', '- **Functional:** Yes\n- **Functional:** No\n'):
            with self.subTest(line=line):
                self.assertEqual(functional_errors('### Revision 2\n' + line + '- **Change:** Fix.\n'), [self.ERROR])

    def test_a_history_with_no_labels_fails(self):
        self.assertEqual(len(functional_errors('### Revision 2\n- **Change:** Fix.\n### Revision 1\n- **Change:** Earlier.\n')), 2)

    def test_revision_filter_and_boundary(self):
        text = '### Revision 3\n- **Change:** New.\n### Revision 2\n- **Change:** Fix.\n### Revision 1\n- **Functional:** No (comments only)\n- **Change:** Comments.\n'
        self.assertEqual(functional_errors(text, 1), [])
        self.assertEqual(len(functional_errors(text)), 2)
        # <!-- custom: Revisions up to the boundary predate the label, so a commit is judged only on later ones. (Claude code Opus 5.5) -->
        self.assertEqual(functional_errors(text, above=3), [])
        self.assertEqual(len(functional_errors(text, above=2)), 1)


# <!-- custom: The entry layout rule added on 2026-11-25, after 193 loose paragraphs were found outside entries' lists. (Claude code Opus 5.5) -->
class ChangeLayoutTests(unittest.TestCase):
    def test_child_bullets_and_fields_pass(self):
        self.assertEqual(change_layout_errors('### Revision 2\n- **Change:** Lead.\n  - Detail.\n\n  - More.\n- **Note:** x\n'), [])

    def test_loose_paragraph_fails(self):
        self.assertEqual(change_layout_errors('### Revision 2\n- **Change:** Lead.\n  - Detail.\n\nLoose paragraph.\n'), ['revision 2: a loose paragraph follows the Change text; make it a child bullet ("  - ...")'])


if __name__ == '__main__':
    unittest.main()
