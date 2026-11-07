# Agent instructions: Herdr Mission Control dotfiles

This repository configures stock Herdr TUI. Read `README.md` and `docs/AGENT_SETUP.md` before installing or changing anything.

The product goal is clarity: readable conversation/activity details in the sidebar, compact agent marks at the top, and named local/SSH terminals that are easy to find. Keep that distinction when making changes. Keep the stock Herdr binary; do not introduce a custom fork to work around presentation limits.

When someone asks you to set this repository up:

- Follow `docs/AGENT_SETUP.md`, including the maintainer's suggested keybindings.
- Preserve unrelated local configuration and make timestamped backups before replacing files. If the user requested the complete preset, `install.py` provides backups and copies the full config.
- Do not copy the screenshot's sample titles, project names, times, models, or session IDs into the user's configuration.
- Before controlling a live Herdr session, verify `HERDR_ENV=1`, run `herdr --skill`, and follow the installed version's instructions. Outside Herdr, prepare dotfiles and give the user the commands to run inside a pane; do not inspect/control their focused live session from outside it.
- Use `install.py --reload --autostart` for the native startup plugin when setting up this preset. Keep one watcher per session using its file lock; verify the plugin action and registration. Preserve the current pane/session environment when starting it manually. Do not stop the Herdr server or restart running agents to install these dotfiles.
- Never read, publish, or commit credentials, private session databases/transcripts, SSH configuration, caches, or logs to this repository. Model lookup happens locally in read-only mode.
- Verify font glyphs, reload the configuration, and check live labels/metadata. A successful config reload alone does not prove the watcher works.

For repository changes, run `python3 -m unittest discover -s tests -v` when code changes. For documentation/media-only changes, verify local links, image paths, code fences, and crop readability. Do not claim screenshots demonstrate behavior that is not implemented. Do not publish repository changes unless the user requested it.
