#!/usr/bin/env python3
"""Install Herdr dotfiles, backing up existing files before replacing them."""
import argparse
from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import tomllib


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=Path.home(), help='Destination home; useful for a dry install')
    parser.add_argument('--reload', action='store_true', help='Reload the running Herdr server after installation')
    args = parser.parse_args()
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


if __name__ == '__main__':
    main()
