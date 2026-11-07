# Herdr dotfiles

Personal terminal UI configuration for **Herdr TUI 0.9.5**, with a Rose Pine theme, tmux-style Ctrl+S prefix, custom agent mascots, and English conversation titles.

![Ghost sidebar](screenshots/sidebar-ghost.png)

## Included

- `herdr/config.toml`: theme, pane/window shortcuts, sidebar rows, and a fixed 36-column sidebar.
- `bin/herdr-tab-titles`: full sidebar titles, numbered Nerd Font logos in the top bar and host OS icons beside shell names, two-line wrapping at 32 text columns, tab-number labels, prompt recency, and agent mascots.
- `install.py`: installs both files with timestamped backups.
- `screenshots/`: before and after screenshots supplied during customization.
- [ICONS.md](ICONS.md): all 20 icon options from the design session.

Claude keeps its orange pixel mascot. Codex uses the mint Ghost, occupying the same 9-column × 2-row footprint:

```text
 ▗█████▖
 █ ▪ ▪ █
```

OpenCode uses a light-gray, two-row block outline based on its logo:

```text
  █▀▀█
  █▄▄█
```

Its top-tab marker is the ordinary Unicode symbol **▣** (U+25A3), a compact substitute rather than an official Nerd Font logo. No custom font is needed. Agent mascots and an initial sidebar title are populated automatically for newly detected agents, including OpenCode.

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

To update tab numbers and icons while preserving the existing sidebar text:

```sh
herdr-tab-titles --labels-only
# Keep numbers and icons current as tabs change:
herdr-tab-titles --labels-only --watch
```

Claude tabs use **Nerd Fonts `cod-claude` (U+EC82)**, and Codex tabs use **`cod-openai` (U+EC81)**. OpenCode uses the Unicode block symbol ▣. These are monochrome text glyphs, not emoji. Every tab begins with its position number followed by a dot (for example, `1.`) in its workspace, matching Ctrl+S → 1–9. Ordinary terminals display `number. + OS icon + name`: Apple for macOS, Ubuntu for Ubuntu, and Linux for other Linux distributions. The OS icon replaces the old terminal symbol. Tabs containing both agent kinds show both logos; unknown kinds fall back to a braille blank. Agent tabs still occupy Herdr's minimum eight-column tab slots; shell tabs retain their names after the number and terminal icon. Mixed agent/shell tabs also retain their names. Before blanking, original names are saved locally in `~/.config/herdr/saved-tab-labels.json`. That file is not part of this repository. If an agent exits, the next watcher pass displays the old name with its OS icon unless you manually renamed the tab.

Stop the watcher before restoring all names:

```sh
herdr-tab-titles --restore-tabs
```

A watcher started in the foreground can be stopped with Ctrl+C. The live label-only watcher started during setup runs in the background; its PID is recorded in `~/.config/herdr/tab-label-watcher.pid` and its output goes to `~/.config/herdr/tab-label-watcher.log`. It lasts until stopped or the machine restarts. After restarting, run the watcher again from a Herdr pane. The installer itself does not create a startup service.

The reporter reads Claude/Codex local history to derive prompt times. Persian titles are translated with the locally installed `claude -p --model haiku` command and cached under `~/.config/herdr/title-cache.json`; that optional translation makes a model call. Failed translations fall back to the existing tab label. Conversation titles are reported only to sidebar metadata; the top agent labels use numbers and compact logos. No histories or caches are included in this repository.

## Font support

A font containing U+EC81 and U+EC82 is required. The installed **Symbols Nerd Font Mono 3.5.1** contains both, and Ghostty's font lookup selects it automatically. No Ghostty font change was needed. Check your setup with:

```sh
ghostty +show-face --cp=0xec82
ghostty +show-face --cp=0xec81
ghostty +show-face --cp=0xf489
```

Expected: the logos report `Symbols Nerd Font Mono`; the terminal icon reports `Symbols Nerd Font`. On other terminals, configure that font as a fallback if the icons appear as missing-glyph boxes.

## SSH host icons

The watcher checks the foreground process of shell tabs. Local macOS shells use the Apple logo (U+F179). When the foreground program is OpenSSH, a short, read-only SSH probe runs `uname -s` and reads the distribution ID from `/etc/os-release`. Confirmed Ubuntu hosts use U+F31B; other Linux hosts use U+F17C; remote macOS uses Apple. An unknown or unreachable SSH host uses a globe (U+F0AC), rather than guessing its OS from its hostname. Agent tabs retain their Claude/OpenAI logos.

Successful OS checks are cached for ten minutes in watcher memory; failed checks for one minute. The probe uses the existing destination and connection options, including ports, keys, SSH config files, and jump hosts. It is noninteractive, requires an already trusted host key, disables forwarding and local commands, and has a five-second process timeout. It never sends a command into the terminal you are using. Password-only sessions can show the globe because the separate probe cannot ask for a password. Unsupported SSH command forms also use the globe.

Changes appear on the next watcher pass. Exiting SSH restores the local OS icon. For split shell tabs, the currently focused pane is used when available, otherwise the first pane. No SSH configuration or remote dotfiles are changed, and no host details or caches are committed here.

The local Apple icon was verified live. Ubuntu/macOS/Linux probe responses, failures, SSH argument handling, and icon transitions are covered by mocked tests; no live remote SSH session was open during setup.

References: [OpenSSH command options](https://man.openbsd.org/ssh.1), [OpenSSH configuration](https://man.openbsd.org/ssh_config.5).

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

**The stock-Herdr workaround now replaces agent tab names with logo glyphs while keeping full sidebar titles.** Removing the remaining agent tab slots and adding the second prefix layer are not implemented. Herdr 0.9.5 provides `keys.focus_agent` for visible agent order, but has no configuration option to hide agent tabs from the top bar or define a second prefix key layer. Removing the tab slots and adding the second prefix layer require a custom TUI build. The current script's numbers refer to tab order, not the sidebar's priority order.

References: [configuration](https://herdr.dev/tui/docs/configuration/), [configuration reference](https://herdr.dev/tui/docs/config-reference/), [Herdr source](https://github.com/herdrdev/herdr/tree/v0.9.5).

## Restore

The installer prints the location of every backup. Copy the desired `.bak-<timestamp>` file back over its original destination and run `herdr server reload-config`. No server restart is required for the configuration changes here.

## Screenshots

[Original terminal-box icon and narrow title wrapping](screenshots/sidebar-before.png) · [Ghost icon and wider title wrapping](screenshots/sidebar-ghost.png)

## Validation

```sh
python3 -m unittest discover -s tests -v
```

Tests cover numbered agent logos, terminal names, repeated updates, restoration after agent exit, explicit restore, manual names starting with numbers, migration from blank labels, tab reordering, and numbering independently in each workspace. The live session was also checked through the Herdr API: every tab had its position number, agents had their correct logos, and the shell tab retained its name beside the local Apple icon.
