import runpy
from pathlib import Path
import unittest
from unittest.mock import patch
from types import SimpleNamespace


class SidebarMascotTests(unittest.TestCase):
    def test_new_opencode_initializes_ascii_and_title_with_silent_cli(self):
        ns = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'bin/herdr-tab-titles'))
        function = ns['refresh_sidebar_mascots']
        tabs = [{'tab_id': 't', 'workspace_id': 'w'}]
        agent = {'tab_id': 't', 'pane_id': 'p', 'agent': 'opencode', 'terminal_title_stripped': 'OpenCode'}
        with patch.object(function.__globals__['subprocess'], 'run', return_value=SimpleNamespace(stdout='', returncode=0)) as run:
            function(tabs, [agent])
            args = run.call_args.args[0]
            self.assertIn('t1=1 OpenCode', args)
            self.assertIn('m1=' + ns['MASCOT']['opencode'][0], args)
            self.assertIn('m2=' + ns['MASCOT']['opencode'][1], args)
            self.assertTrue(all(len(row) == 9 for row in ns['MASCOT']['opencode']))
            agent.update(display_agent=ns['LOGOS']['opencode'], tokens={
                't1': 'Existing title', 'm1': ns['MASCOT']['opencode'][0], 'm2': ns['MASCOT']['opencode'][1]})
            run.reset_mock()
            function(tabs, [agent])
            run.assert_not_called()
