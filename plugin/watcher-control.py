#!/usr/bin/env python3
"""Start/stop one Mission Control reporter per Herdr socket."""
import argparse
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import runpy
import signal
import subprocess
import sys
import time


@contextmanager
def locked(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield


def running(paths):
    with paths['lock'].open('a+') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        return False


def verified_pid(paths, reporter):
    try:
        pid = int(paths['pid'].read_text())
        result = subprocess.run(['ps', '-p', str(pid), '-o', 'command='], capture_output=True, text=True)
        if result.returncode == 0 and str(reporter) in result.stdout and '--watch' in result.stdout:
            return pid
    except (OSError, ValueError):
        pass
    return None


def stop(paths, reporter):
    pid = verified_pid(paths, reporter)
    if pid is None:
        if running(paths):
            raise RuntimeError('Watcher lock is held, but its PID could not be verified; left untouched.')
        return {'status': 'stopped'}
    os.kill(pid, signal.SIGTERM)
    for _ in range(40):
        if verified_pid(paths, reporter) is None and not running(paths):
            return {'status': 'stopped', 'pid': pid}
        time.sleep(0.05)
    raise RuntimeError('Watcher did not stop; no replacement was started.')


def start(paths, reporter):
    if running(paths):
        return {'status': 'already-running', 'pid': verified_pid(paths, reporter)}
    # Migrate the old manually launched reporter, which predates the singleton lock.
    if verified_pid(paths, reporter) is not None:
        stop(paths, reporter)
    env = os.environ.copy()
    binary = env.get('HERDR_BIN_PATH')
    if binary:
        env['PATH'] = str(Path(binary).parent) + os.pathsep + env.get('PATH', '')
    with paths['log'].open('a') as log:
        child = subprocess.Popen([sys.executable, str(reporter), '--watch', '--labels-only'],
                                 stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                 env=env, start_new_session=True)
    for _ in range(60):
        if running(paths):
            return {'status': 'started', 'pid': verified_pid(paths, reporter)}
        if child.poll() is not None:
            raise RuntimeError(f'Watcher exited with code {child.returncode}; see {paths["log"]}.')
        time.sleep(0.05)
    child.terminate()
    raise RuntimeError('Watcher failed to acquire its lock; startup was cancelled.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('start', 'stop', 'status'))
    parser.add_argument('--reporter', type=Path, default=Path.home() / '.local/bin/herdr-tab-titles')
    args = parser.parse_args()
    if os.environ.get('HERDR_ENV') != '1':
        parser.error('Run inside Herdr, or through its Mission Control plugin.')
    reporter = args.reporter.resolve()
    namespace = runpy.run_path(str(reporter))
    paths = namespace['watcher_paths']()
    paths['lock'].parent.mkdir(parents=True, exist_ok=True)
    with locked(paths['launch_lock']):
        if args.action == 'start':
            result = start(paths, reporter)
        elif args.action == 'stop':
            result = stop(paths, reporter)
        else:
            active = running(paths)
            result = {'status': 'running' if active else 'stopped',
                      'pid': verified_pid(paths, reporter) if active else None}
    print(json.dumps(result))


if __name__ == '__main__':
    main()
