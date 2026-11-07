# Herdr dotfiles

Personal terminal UI configuration for **Herdr TUI 0.9.5**, with a Rose Pine theme, tmux-style Ctrl+S prefix, custom agent mascots, and English conversation titles.

![Ghost sidebar](screenshots/sidebar-ghost.png)

## Included

- `herdr/config.toml`: theme, pane/window shortcuts, sidebar rows, and a fixed 36-column sidebar.
- `bin/herdr-tab-titles`: full sidebar titles, orange Claude and green Codex markers in the top bar, two-line wrapping at 32 text columns, tab-number labels, prompt recency, and agent mascots.
- `install.py`: installs both files with timestamped backups.
- `screenshots/`: before and after screenshots supplied during customization.
- [ICONS.md](ICONS.md): all 20 icon options from the design session.

Claude keeps its orange pixel mascot. Codex uses the mint Ghost, occupying the same 9-column × 2-row footprint:

```text
 ▗█████▖
 █ ▪ ▪ █
```

The script pads both rows to nine cells with braille blanks so Herdr preserves their alignment.

## Install

Requires Herdr 0.9.5 on PATH and Python 3.11+. The screenshots use macOS; these dotfiles do not install or update Herdr.

```sh
python3 install.py --reload
export PATH="$HOME/.local/bin:$PATH"
herdr-tab-titles
```

Run title reporting from inside a Herdr pane. To keep titles and recency fresh, leave the watcher running in a shell terminal:

```sh
herdr-tab-titles --watch
```

To color-code agent tab labels while preserving the existing sidebar text:

```sh
herdr-tab-titles --labels-only
# Keep new agent tabs color-coded and restore labels when agents exit:
herdr-tab-titles --labels-only --watch
```

Claude tabs use 🟧; Codex tabs use 🟩. Tabs containing both kinds use both markers. Unknown agents use a blank braille character (U+2800). Agent tabs still occupy Herdr's hardcoded minimum eight-column tab slots; stock configuration cannot halve that minimum or set per-agent tab background colors. The emoji markers supply color without changing Herdr. Shell tabs retain their names. Tabs containing both an agent and a normal shell are left named. Before blanking, original names are saved locally in `~/.config/herdr/saved-tab-labels.json`. That file is not part of this repository. If an agent exits, the next watcher pass restores the old name unless you manually renamed the tab.

Stop the watcher before restoring all names:

```sh
herdr-tab-titles --restore-tabs
```

A watcher started in the foreground can be stopped with Ctrl+C. The live label-only watcher started during setup runs in the background; its PID is recorded in `~/.config/herdr/tab-label-watcher.pid` and its output goes to `~/.config/herdr/tab-label-watcher.log`. It lasts until stopped or the machine restarts. After restarting, run the watcher again from a Herdr pane. The installer itself does not create a startup service.

The reporter reads Claude/Codex local history to derive prompt times. Persian titles are translated with the locally installed `claude -p --model haiku` command and cached under `~/.config/herdr/title-cache.json`; that optional translation makes a model call. Failed translations fall back to the existing tab label. Conversation titles are reported only to sidebar metadata; the top agent labels stay compact and colored. No histories or caches are included in this repository.

## Existing shortcuts

Press Ctrl+S, release it, then press the key shown.

| Keys after Ctrl+S | Action |
| --- | --- |
| `1`–`9` | Select tab in tab order |
| `c` | New tab |
| `n` / `p` | Next / previous tab |
| `,` | Rename tab |
| `%` or `v` | Split right |
| `"` or `-` | Split down |
| `h` / `j` / `k` / `l` | Focus pane |
| `z` | Zoom pane |
| `b` | Toggle sidebar |
| `d` | Detach |

## Requested next layout

The target is to show agents only in the sidebar, shell terminals only in the top bar, number agents by their visible sidebar order, and use Ctrl+S → Space → number for shell terminals.

**The stock-Herdr workaround now replaces agent tab names with colored markers while keeping full sidebar titles.** Removing the remaining empty tab slots and adding the second prefix layer are not implemented. Herdr 0.9.5 provides `keys.focus_agent` for visible agent order, but has no configuration option to hide agent tabs from the top bar or define a second prefix key layer. Removing the tab slots and adding the second prefix layer require a custom TUI build. The current script's numbers refer to tab order, not the sidebar's priority order.

References: [configuration](https://herdr.dev/tui/docs/configuration/), [configuration reference](https://herdr.dev/tui/docs/config-reference/), [Herdr source](https://github.com/herdrdev/herdr/tree/v0.9.5).

## Restore

The installer prints the location of every backup. Copy the desired `.bak-<timestamp>` file back over its original destination and run `herdr server reload-config`. No server restart is required for the configuration changes here.

## Screenshots

[Original terminal-box icon and narrow title wrapping](screenshots/sidebar-before.png) · [Ghost icon and wider title wrapping](screenshots/sidebar-ghost.png)

## Validation

```sh
python3 -m unittest discover -s tests -v
```

Tests cover blanking agent-only tabs, preserving normal and mixed tabs, repeated updates, restoration after agent exit, explicit restore, and manual shell renames. The live session was also checked through the Herdr API: eight agent tabs had matching orange/green markers, the shell tab kept its label, and all sidebar title tokens remained populated.
