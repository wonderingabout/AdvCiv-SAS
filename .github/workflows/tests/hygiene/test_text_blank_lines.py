# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production check; tempfile/subprocess isolate real Git ranges and unittest verifies cleanup versus newly introduced spacing without altering repository history. (GPT-6.1-Sol) -->
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/hygiene"))
# <!-- custom: Exercise the supplementary checker and its shared literal-aware ancestry through the same implementations used by workflow/source checks. (GPT-6.1-Sol) -->
import text_blank_lines as check
from blank_lines import blank_line_errors, long_blank_runs


class TextBlankLineTests(unittest.TestCase):
    def test_formats_and_existing_check_ownership(self):
        for name in ('.gitattributes', '.gitignore', 'x.ini', 'x.cfg', 'x.toml', 'x.yml', 'x.yaml', 'x.json', 'x.jsonc', 'x.txt'):
            self.assertEqual(check.policy(name)[1], 1)
        for name in ('Makefile', 'Makefile.project', 'x.inl', 'x.rc', 'x.ps1', 'x.sh', 'x.bat', 'x.cmd', 'x.def'):
            self.assertEqual(check.policy(name)[1], 2)
        for name in ('x.py', 'x.cpp', 'x.xml', 'x.md', 'Assets/Art/example/ReadMe.txt', '_1_AdvCiv-SAS/Docs/git_logs/example.txt'):
            self.assertIsNone(check.policy(name))

    def test_new_runs_block_deletions_and_inherited_cleanup(self):
        old = 'first\n\nremove\n\nlast\n'
        joined = 'first\n\n\nlast\n'
        self.assertTrue(blank_line_errors('x.ini', old, joined, '.ini', 1))
        self.assertEqual(blank_line_errors('x.ini', joined, joined, '.ini', 1), [])
        self.assertEqual(blank_line_errors('x.ini', joined, joined.replace('\n\n\n', '\n\n'), '.ini', 1), [])
        self.assertTrue(blank_line_errors('x.ini', '', 'first\n\n \nlast\n', '.ini', 1))

    def test_literal_regions_and_ordinary_neighbors(self):
        cases = {
            '.yml': 'run: |\n  first\n\n\n  last\nnext: value\n',
            '.toml': 'value = """first\n\n\nlast"""\n',
            '.ps1': '$value = @"\nfirst\n\n\nlast\n"@\n',
            '.sh': "cat <<'END'\nfirst\n\n\nlast\nEND\n",
            'makefile': 'define VALUE\nfirst\n\n\nlast\nendef\n',
            '.txt': '----- Comment #1 -----\nquoted\n\n\ntext\n',
            '.inl': '/* quoted\n\n\ntext */\n',
        }
        for suffix, literal in cases.items():
            with self.subTest(suffix=suffix):
                self.assertEqual(long_blank_runs(literal, suffix, 1), [])
                self.assertEqual(len(long_blank_runs('before\n\n\n' + literal, suffix, 1)), 1)

    def test_audit_and_changed_only_with_legacy_encoding(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=repo, stderr=subprocess.DEVNULL).decode().strip()
            git('init', '-q')
            git('config', 'user.name', 'CI fixture')
            git('config', 'user.email', 'fixture@example.invalid')
            git('config', 'commit.gpgsign', 'false')
            (repo / 'x.ini').write_bytes(b'# inherited \x92quote\n\n\nlast\n')
            git('add', '.')
            git('commit', '-qm', 'baseline')
            base = git('rev-parse', 'HEAD')
            self.assertEqual(check.check(repo, base)[0], [])
            self.assertEqual(len(check.check(repo, audit=True)[0]), 1)
            (repo / 'x.ini').write_bytes(b'# inherited \x92quote\n\nlast\n')
            self.assertEqual(check.check(repo, audit=True)[0], [])
            (repo / 'new.cfg').write_text('first\n\n\nlast\n')
            git('add', 'new.cfg')
            self.assertEqual(len(check.check(repo, base)[0]), 1)


if __name__ == '__main__':
    unittest.main()
