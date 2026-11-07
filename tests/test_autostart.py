import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
import tomllib


ROOT = Path(__file__).resolve().parents[1]


class AutostartTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.reporter = self.home / '.local/bin/herdr-tab-titles'
        self.reporter.parent.mkdir(parents=True)
        shutil.copy2(ROOT / 'bin/herdr-tab-titles', self.reporter)
        fake = self.reporter.parent / 'herdr'
        fake.write_text('#!' + sys.executable + '\nimport json,sys\n'
                        'key={"tab":"tabs","agent":"agents","workspace":"workspaces"}[sys.argv[1]]\n'
                        'print(json.dumps({"result":{key:[]}}))\n')
        fake.chmod(0o755)
        self.env = dict(os.environ, HOME=str(self.home), HERDR_ENV='1',
                        HERDR_SOCKET_PATH=str(self.home / '.config/herdr/herdr.sock'),
                        PATH=str(self.reporter.parent) + os.pathsep + os.environ['PATH'])
        self.env.pop('HERDR_BIN_PATH', None)
        self.addCleanup(self.stop)

    def command(self, action):
        return [sys.executable, str(ROOT / 'plugin/watcher-control.py'), action, '--reporter', str(self.reporter)]

    def control(self, action):
        result = subprocess.run(self.command(action), env=self.env, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def stop(self):
        subprocess.run(self.command('stop'), env=self.env, capture_output=True, text=True, timeout=10)

    def test_start_twice_is_one_process_and_stop_releases_lock(self):
        first = self.control('start')
        second = self.control('start')
        self.assertEqual(first['status'], 'started')
        self.assertEqual(second['status'], 'already-running')
        self.assertEqual(first['pid'], second['pid'])
        self.assertEqual(self.control('status')['status'], 'running')
        self.assertEqual(self.control('stop')['status'], 'stopped')
        self.assertEqual(self.control('status')['status'], 'stopped')
        # A stale PID file must not prevent the next startup.
        third = self.control('start')
        self.assertEqual(third['status'], 'started')
        self.assertNotEqual(third['pid'], first['pid'])

    def test_concurrent_start_hooks_do_not_duplicate(self):
        children = [subprocess.Popen(self.command('start'), env=self.env, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True) for _ in range(2)]
        results = []
        for child in children:
            stdout, stderr = child.communicate(timeout=10)
            self.assertEqual(child.returncode, 0, stderr)
            results.append(json.loads(stdout))
        self.assertEqual({r['status'] for r in results}, {'started', 'already-running'})
        self.assertEqual(len({r['pid'] for r in results}), 1)

    def test_manual_watch_cannot_create_second_worker(self):
        first = self.control('start')
        result = subprocess.run([sys.executable, str(self.reporter), '--watch', '--labels-only'],
                                env=self.env, capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('already running', result.stdout)
        self.assertEqual(self.control('status')['pid'], first['pid'])

    def test_startup_hook_and_start_action_use_identical_launcher(self):
        manifest = tomllib.loads((ROOT / 'plugin/herdr-plugin.toml').read_text())
        startup = manifest['startup'][0]['command']
        action = next(item for item in manifest['actions'] if item['id'] == 'start-watcher')
        self.assertEqual(startup, action['command'])
        self.assertEqual(startup[-1], 'start')

    def test_socket_scoped_state_keeps_sessions_separate(self):
        ns = runpy.run_path(str(ROOT / 'bin/herdr-tab-titles'))
        paths = ns['watcher_paths'](self.home, str(self.home / '.config/herdr/herdr.sock'))
        other = ns['watcher_paths'](self.home, str(self.home / '.config/herdr/named.sock'))
        self.assertEqual(paths['pid'], self.home / '.config/herdr/tab-label-watcher.pid')
        for key in paths:
            self.assertNotEqual(paths[key], other[key])
