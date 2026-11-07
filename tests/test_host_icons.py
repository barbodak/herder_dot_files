import runpy
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


class HostIconTests(unittest.TestCase):
    def setUp(self):
        self.ns = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'bin/herdr-tab-titles'))
        self.globals = self.ns['remote_os_icon'].__globals__

    def test_ssh_arguments_keep_connection_but_drop_forwards_and_remote_command(self):
        args = ['ssh', '-vt', '-p2222', '-i', '/keys/work key', '-J', 'jump',
                '-L', '8000:localhost:80', '-R9000:localhost:90', '-o', 'IdentitiesOnly=yes',
                'user@server', 'sudo', 'reboot']
        self.assertEqual(self.ns['ssh_connection_args'](args),
                         ['-p', '2222', '-i', '/keys/work key', '-J', 'jump',
                          '-o', 'IdentitiesOnly=yes', 'user@server'])

    def test_unsupported_and_incomplete_commands(self):
        for args in (['scp', 'a', 'b'], ['ssh', '-i'], ['ssh', '-G', 'host'],
                     ['ssh', '-O', 'exit', 'host'], ['ssh', '-W', 'host:22', 'jump']):
            self.assertIsNone(self.ns['ssh_connection_args'](args))

    def test_confirmed_ubuntu_and_cached_probe(self):
        response = SimpleNamespace(returncode=0, stdout='banner\n__HERDR_OS__\nLinux\n"ubuntu"\n')
        with patch.object(self.globals['subprocess'], 'run', return_value=response) as run:
            self.assertEqual(self.ns['remote_os_icon'](['host']), self.ns['OS_ICONS']['ubuntu'])
            self.assertEqual(self.ns['remote_os_icon'](['host']), self.ns['OS_ICONS']['ubuntu'])
            self.assertEqual(run.call_count, 1)
            args = run.call_args.args[0]
            for required in ['BatchMode=yes', 'StrictHostKeyChecking=yes', 'ClearAllForwardings=yes',
                             'ForwardAgent=no', 'PermitLocalCommand=no', 'RemoteCommand=none']:
                self.assertIn(required, args)
            self.assertIn('uname -s', args[-1])
            self.assertIn('/etc/os-release', args[-1])

    def test_remote_mac_linux_and_failure(self):
        for host, output, status, expected in [
            ('mac', '__HERDR_OS__\nDarwin\n', 0, 'darwin'),
            ('linux', '__HERDR_OS__\nLinux\ndebian\n', 0, 'linux'),
            ('failed', '', 255, 'remote'),
        ]:
            with patch.object(self.globals['subprocess'], 'run', return_value=SimpleNamespace(returncode=status, stdout=output)):
                self.assertEqual(self.ns['remote_os_icon']([host]), self.ns['OS_ICONS'][expected])

    def test_switching_shell_os_preserves_real_name(self):
        # Strip old terminal and all host logos, but leave ordinary user numbers intact.
        for icon in self.ns['SHELL_ICONS']:
            self.assertEqual(self.ns['undecorated_label'](f'9. {icon} 2026 work'), '2026 work')
        self.assertEqual(self.ns['undecorated_label']('2026 work'), '2026 work')

    def test_foreground_ssh_selects_remote_icon_without_using_titles(self):
        def api(*args):
            if args == ('pane', 'list'):
                return {'panes': [{'tab_id': 't1', 'pane_id': 'p1'}]}
            return {'process_info': {'foreground_processes': [{'argv': ['ssh', 'prod']}]}}
        self.globals['herdr'] = api
        self.globals['remote_os_icon'] = lambda connection: self.ns['OS_ICONS']['ubuntu']
        self.assertEqual(self.ns['terminal_icons']([{'tab_id': 't1', 'pane_count': 1}], []),
                         {'t1': self.ns['OS_ICONS']['ubuntu']})

    def test_foreground_shell_selects_local_os(self):
        def api(*args):
            if args == ('pane', 'list'):
                return {'panes': [{'tab_id': 't1', 'pane_id': 'p1'}]}
            return {'process_info': {'foreground_processes': [{'argv': ['-zsh']}]}}
        self.globals['herdr'] = api
        self.globals['local_os_icon'] = lambda: self.ns['OS_ICONS']['darwin']
        self.assertEqual(self.ns['terminal_icons']([{'tab_id': 't1', 'pane_count': 1}], []),
                         {'t1': self.ns['OS_ICONS']['darwin']})
