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
        self.tabs = [dict(tab_id='one', label='Agent conversation', pane_count=1),
                     dict(tab_id='shell', label='Server logs', pane_count=1),
                     dict(tab_id='mixed', label='Mixed', pane_count=2)]
        self.agents = [dict(tab_id='one'), dict(tab_id='mixed')]

    def test_blank_agents_only_and_restore_when_agent_exits(self):
        self.ns['update_tab_labels'](self.tabs, self.agents)
        self.assertEqual(self.calls, [('tab', 'rename', 'one', self.ns['BLANK_TAB'])])
        self.assertEqual(self.ns['saved_labels'](), {'one': 'Agent conversation'})
        self.tabs[0]['label'] = self.ns['BLANK_TAB']
        self.calls.clear()
        self.ns['update_tab_labels'](self.tabs, [])
        self.assertEqual(self.calls, [('tab', 'rename', 'one', 'Agent conversation')])
        self.assertEqual(self.ns['saved_labels'](), {})

    def test_explicit_restore_and_repeated_sync(self):
        self.ns['update_tab_labels'](self.tabs, self.agents)
        self.tabs[0]['label'] = self.ns['BLANK_TAB']
        self.calls.clear()
        self.ns['update_tab_labels'](self.tabs, self.agents)
        self.assertEqual(self.calls, [])
        self.ns['update_tab_labels'](self.tabs, self.agents, restore=True)
        self.assertEqual(self.calls, [('tab', 'rename', 'one', 'Agent conversation')])

    def test_manual_shell_rename_is_preserved(self):
        self.ns['update_tab_labels'](self.tabs, self.agents)
        self.tabs[0]['label'] = 'My new shell name'
        self.calls.clear()
        self.ns['update_tab_labels'](self.tabs, [])
        self.assertEqual(self.calls, [])
        self.assertEqual(self.ns['saved_labels'](), {})


if __name__ == '__main__':
    unittest.main()
