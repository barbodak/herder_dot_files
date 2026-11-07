import runpy
from pathlib import Path
import tempfile
import unittest


class TabLabelTests(unittest.TestCase):
    def setUp(self):
        self.ns = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'bin/herdr-tab-titles'))
        self.globals = self.ns['update_tab_labels'].__globals__
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.globals['TAB_LABELS'] = Path(self.temp.name) / 'labels.json'
        self.calls = []
        self.globals['herdr'] = lambda *args: self.calls.append(args)
        self.tabs = [dict(tab_id='one', workspace_id='w1', label='Agent conversation', pane_count=1),
                     dict(tab_id='shell', workspace_id='w1', label='Server logs', pane_count=1),
                     dict(tab_id='mixed', workspace_id='w1', label='Mixed', pane_count=2)]
        self.agents = [dict(tab_id='one', agent='claude'), dict(tab_id='mixed', agent='codex')]

    def sync(self, agents=None, restore=False):
        self.calls.clear()
        self.ns['update_tab_labels'](self.tabs, self.agents if agents is None else agents, restore=restore)
        for _, _, key, label in self.calls:
            next(t for t in self.tabs if t['tab_id'] == key)['label'] = label

    def test_numbered_logos_and_terminal_names(self):
        self.sync()
        self.assertEqual([t['label'] for t in self.tabs], ['1. \uec82', '2. \uf489 Server logs', '3. \uf489 Mixed'])
        self.sync()
        self.assertEqual(self.calls, [])
        self.assertEqual(self.ns['saved_labels']()['shell'], 'Server logs')

    def test_agent_exit_restores_name_with_terminal_icon(self):
        self.sync()
        self.sync(agents=[])
        self.assertEqual(self.tabs[0]['label'], '1. \uf489 Agent conversation')

    def test_restore_removes_all_decorations(self):
        self.sync()
        self.sync(restore=True)
        self.assertEqual([t['label'] for t in self.tabs], ['Agent conversation', 'Server logs', 'Mixed'])
        self.assertEqual(self.ns['saved_labels'](), {})

    def test_old_blank_migration_keeps_original_name(self):
        self.ns['save_labels']({'one': 'Agent conversation'})
        self.tabs[0]['label'] = self.ns['BLANK_TAB']
        self.sync()
        self.assertEqual(self.tabs[0]['label'], '1. \uec82')
        self.agents[0]['agent'] = 'codex'
        self.sync()
        self.assertEqual(self.tabs[0]['label'], '1. \uec81')
        self.assertEqual(self.ns['saved_labels']()['one'], 'Agent conversation')

    def test_manual_rename_preserves_number_in_real_name(self):
        self.sync()
        self.tabs[1]['label'] = '2026 deployment'
        self.sync()
        self.assertEqual(self.tabs[1]['label'], '2. \uf489 2026 deployment')
        self.sync(restore=True)
        self.assertEqual(self.tabs[1]['label'], '2026 deployment')

    def test_reordering_and_workspace_numbering(self):
        self.sync()
        self.tabs.reverse()
        self.sync()
        self.assertEqual(self.tabs[0]['label'], '1. \uf489 Mixed')
        self.assertEqual(self.tabs[2]['label'], '3. \uec82')
        self.tabs[2]['workspace_id'] = 'w2'
        self.sync()
        self.assertEqual(self.tabs[2]['label'], '1. \uec82')


if __name__ == '__main__':
    unittest.main()
