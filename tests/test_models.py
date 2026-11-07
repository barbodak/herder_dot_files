import json
from pathlib import Path
import runpy
import sqlite3
import tempfile
import unittest
from contextlib import closing, contextmanager


@contextmanager
def database(path):
    with closing(sqlite3.connect(path)) as db:
        with db:
            yield db


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.ns = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'bin/herdr-tab-titles'))
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)

    def test_claude_latest_assistant_not_subagent_or_synthetic(self):
        path = self.home / '.claude/projects/-project/session.jsonl'
        path.parent.mkdir(parents=True)
        rows = [{'type': 'assistant', 'message': {'model': 'claude-sonnet-5-5'}},
                {'type': 'assistant', 'message': {'model': 'claude-opus-5-5'}},
                {'type': 'assistant', 'message': {'model': '<synthetic>'}},
                {'type': 'user', 'message': {'model': 'ignore'}}]
        path.write_text('\n'.join(json.dumps(row) for row in rows))
        agent = dict(agent='claude', cwd='/project', agent_session={'value': 'session'})
        self.assertEqual(self.ns['session_model'](agent, self.home), 'claude-opus-5-5')
        with path.open('a') as f:
            f.write('\n' + json.dumps({'type': 'assistant', 'message': {'model': 'claude-sonnet-5-5'}}))
        self.assertEqual(self.ns['session_model'](agent, self.home), 'claude-sonnet-5-5')

    def test_codex_exact_name_and_cwd_match_no_ambiguous_guess(self):
        path = self.home / '.codex/state_5.sqlite'
        path.parent.mkdir(parents=True)
        with database(path) as db:
            db.execute('create table threads(id text, name text, title text, cwd text, model text, archived integer)')
            db.execute("insert into threads values ('one', 'Review sidebar', 'original', '/project', 'gpt-6.1-sol', 0)")
        agent = dict(agent='codex', cwd='/project', terminal_title_stripped='⠴ Review sidebar | project')
        self.assertEqual(self.ns['session_model'](agent, self.home), 'gpt-6.1-sol')
        with database(path) as db:
            db.execute("insert into threads values ('two', 'Review sidebar', 'other', '/project', 'different', 0)")
        self.assertEqual(self.ns['session_model'](agent, self.home), '')
        agent['agent_session'] = {'value': 'one'}
        self.assertEqual(self.ns['session_model'](agent, self.home), 'gpt-6.1-sol')

    def test_opencode_unique_session_or_explicit_id(self):
        path = self.home / '.local/share/opencode/opencode.db'
        path.parent.mkdir(parents=True)
        with database(path) as db:
            db.execute('create table session_v2(id text, directory text, model text, parent_id text, time_archived integer)')
            db.execute('insert into session_v2 values (?, ?, ?, null, null)',
                       ('one', '/project', json.dumps({'id': 'nemotron-3.5-super-vl-free'})))
        agent = dict(agent='opencode', cwd='/project')
        self.assertEqual(self.ns['session_model'](agent, self.home), 'nemotron-3.5-super-vl-free')
        with database(path) as db:
            db.execute('insert into session_v2 values (?, ?, ?, null, null)',
                       ('two', '/project', json.dumps({'id': 'other'})))
        self.assertEqual(self.ns['session_model'](agent, self.home), '')
        agent['agent_session'] = {'value': 'one'}
        self.assertEqual(self.ns['session_model'](agent, self.home), 'nemotron-3.5-super-vl-free')

    def test_missing_data_does_not_use_global_default(self):
        for kind in ('claude', 'codex', 'opencode'):
            self.assertEqual(self.ns['session_model']({'agent': kind}, self.home), '')

    def test_compact_names_preserve_versions_and_variants(self):
        cases = {'claude-opus-5-5': 'Opus 5.5', 'claude-sonnet-4-20250514': 'Sonnet 4',
                 'gpt-6.1-sol': 'GPT-6.1 Sol', 'vendor/model-x': 'model-x',
                 'nemotron-3.5-super-vl-free': 'Nemotron 3.5-SVL Free'}
        for raw, expected in cases.items():
            self.assertEqual(self.ns['compact_model_name'](raw), expected)
