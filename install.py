#!/usr/bin/env python3
"""Install Herdr dotfiles, backing up existing files before replacing them."""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import tomllib


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=Path.home(), help='Destination home; useful for a dry install')
    parser.add_argument('--reload', action='store_true', help='Reload the running Herdr server after installation')
    parser.add_argument('--autostart', action='store_true', help='Register the native Herdr startup plugin and start one watcher')
    args = parser.parse_args()
    if args.autostart and (os.environ.get('HERDR_ENV') != '1' or args.home.resolve() != Path.home().resolve()):
        parser.error('--autostart must run in Herdr using your actual home directory.')
    root = Path(__file__).resolve().parent
    tomllib.loads((root / 'herdr/config.toml').read_text())
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    for source, target in (
        (root / 'herdr/config.toml', args.home / '.config/herdr/config.toml'),
        (root / 'bin/herdr-tab-titles', args.home / '.local/bin/herdr-tab-titles'),
    ):
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            backup = target.with_name(target.name + '.bak-' + stamp)
            shutil.copy2(target, backup)
            print(f'Backed up {target} to {backup}')
        # Replace a symlink itself, not the source it points at.
        if target.is_symlink():
            target.unlink()
        shutil.copy2(source, target)
        print(f'Installed {target}')
    if args.reload:
        subprocess.run(['herdr', 'server', 'reload-config'], check=True)
    if args.autostart:
        plugin = args.home / '.config/herdr/mission-control-plugin'
        plugin.mkdir(parents=True, exist_ok=True)
        controller = plugin / 'watcher-control.py'
        if controller.exists():
            shutil.copy2(controller, controller.with_name(controller.name + '.bak-' + stamp))
        shutil.copy2(root / 'plugin/watcher-control.py', controller)
        manifest = (root / 'plugin/herdr-plugin.toml').read_text()
        # Resolve the interpreter at install time; don't depend on a future server's PATH.
        manifest = manifest.replace('["python3", "watcher-control.py",',
                                    '[' + json.dumps(sys.executable) + ', ' + json.dumps(str(plugin / 'watcher-control.py')) + ',')
        tomllib.loads(manifest)
        target = plugin / 'herdr-plugin.toml'
        if target.exists():
            shutil.copy2(target, target.with_name(target.name + '.bak-' + stamp))
        target.write_text(manifest)
        subprocess.run(['herdr', 'plugin', 'link', str(plugin)], check=True)
        subprocess.run(['herdr', 'plugin', 'action', 'invoke', 'start-watcher', '--plugin', 'mission-control'], check=True)


if __name__ == '__main__':
    main()
