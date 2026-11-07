# Set this up with your agent

Give your coding agent the repository URL and the prompt below. It can inspect your current setup and apply this preset without maintaining a Herdr fork.

## Copy-and-paste setup prompt

```text
Set up https://github.com/barbodak/herder_dot_files for my Herdr terminal.

Read README.md, AGENTS.md, and docs/AGENT_SETUP.md first. The goal is clarity:
keep full agent conversations, status, mascots, and model labels in the sidebar;
keep agent tabs compact so named local/SSH terminals are easy to find at the top.

Use the repository's Rose Pine theme, mascot layouts, numbered top labels, OS
icons, and suggested Ctrl+S keybindings. Preserve unrelated settings and make
backups before changing existing files. Use the supported dotfile/script route;
do not replace Herdr with a custom build or restart my running agents.

Check the installed Herdr version and fonts. Install the reporter, reload the
config, and start exactly one watcher from inside this Herdr session. Explain
which watcher mode you chose, how to stop it, and what I must run after a reboot.
Run the tests and verify the labels/metadata with the local Herdr API. Report any
feature my local versions cannot provide rather than guessing model/OS values.
```

The GitHub repository currently requires access to its private repository. The setup agent must use an account that can read it. Do not give the agent an access token in a prompt; use the user's existing Git authentication.

## 1. Inspect the environment

Read the repository documentation before editing. Check `herdr --version` and Python's version; this preset was tested with Herdr 0.9.5 and requires Python 3.11+. Find the user's actual terminal, Herdr config location, and installed fonts rather than assuming Ghostty/macOS paths on every machine.

For live session work, verify `HERDR_ENV=1`. Then read `herdr --skill` and the installed CLI's relevant help. If outside Herdr, prepare files only and have the user run the final reporter/watcher commands inside a Herdr pane. Do not target another client's focused session.

The current model readers support the local storage formats documented in the README. Unsupported versions leave model labels blank; a global default is not evidence of a session's current model.

## 2. Fetch and validate

Clone the repository to a location the user owns:

```sh
git clone https://github.com/barbodak/herder_dot_files.git
cd herder_dot_files
python3 -m unittest discover -s tests -v
```

Do not put the user's session data or screenshots into a new upstream commit as part of installation.

## 3. Apply the preset with backups

For a full-preset installation:

```sh
python3 install.py --reload
export PATH="$HOME/.local/bin:$PATH"
```

The installer copies the full config, making timestamped backups first. When the user already has settings to retain, merge the relevant `[keys]`, theme, sidebar, and status entries into their config instead of discarding unrelated values. Copy `bin/herdr-tab-titles` to `~/.local/bin/herdr-tab-titles` and retain its executable permission. Do not overwrite another unrelated executable with the same name without resolving that conflict.

The preset starts the sidebar collapsed; Ctrl+S → b expands it. A user who prefers it visible at startup can set `ui.sidebar_start_collapsed = false`.

## 4. Apply these suggested keybindings

These are the maintainer's preferred keys, and they are already included in `herdr/config.toml`. Apply them together so the top numbers and navigation agree. Ctrl+S is a prefix: press and release it before the next key.

| Key | Action |
| --- | --- |
| Ctrl+S → `1`–`9` | Select the matching top-tab position in the current space |
| Ctrl+S → `c` | New tab |
| Ctrl+S → `n` / `p` | Next / previous tab |
| Ctrl+S → `,` / `&` | Rename / close tab |
| Ctrl+S → `v` or `%` | Split right |
| Ctrl+S → `-` or `"` | Split down |
| Ctrl+S → `h` / `j` / `k` / `l`, or arrows | Focus panes |
| Ctrl+S → `o` or Tab | Cycle panes |
| Ctrl+S → `;` | Last pane |
| Ctrl+S → `z` | Zoom pane |
| Ctrl+S → `x` | Close pane |
| Ctrl+S → `{` / `}` | Swap panes |
| Ctrl+S → `[` | Copy mode |
| Ctrl+S → `s` or `w` | Space picker |
| Ctrl+S → `$` | Rename space |
| Ctrl+S → Shift+P | Rename pane |
| Ctrl+S → Shift+S | Settings |
| Ctrl+S → `b` | Toggle sidebar |
| Ctrl+S → `d` | Detach |
| Ctrl+Arrow | Resize panes directly, without the prefix |

Do not bind plain prefix numbers to `focus_agent` while leaving the top numbers as tab positions: the two would disagree when the sidebar is sorted by priority. Ctrl+S → Space → number is not part of this preset.

If Ctrl+S freezes output because the terminal uses software flow control, inspect that terminal's setup and disable flow control there if needed. Do not replace the user's entire shell startup file to add one setting.

## 5. Verify font support

Claude and OpenAI use Nerd Font private-use glyphs, while OpenCode's top mark uses standard Unicode `▣`. The mascots use block characters. Use the README's codepoint table and the terminal's own font diagnostics.

For Ghostty:

```sh
ghostty +show-face --cp=0xec82
ghostty +show-face --cp=0xec81
ghostty +show-face --cp=0x25a3
ghostty +show-face --cp=0xf179
ghostty +show-face --cp=0xf31b
```

Reuse a working installed font/fallback. If one is missing, configure an appropriate Nerd Font through the terminal's supported settings. Changing the terminal's main text font is not necessary when a fallback works.

## 6. Start one watcher inside Herdr

Choose a mode explicitly:

- **Full mode:** refresh conversation titles and prompt recency as well as mascots, models, and top labels. Persian-title translation uses the Claude CLI and makes model calls.
- **Labels-only mode:** preserve existing sidebar conversation titles/recency; initialize missing mascot/title metadata; refresh models, top numbers, and OS logos. This is the mode used for the screenshot setup.

For an initial labels-only update:

```sh
herdr-tab-titles --labels-only
```

For a foreground watcher:

```sh
herdr-tab-titles --labels-only --watch
```

Stop a foreground watcher with Ctrl+C. To refresh titles and recency continuously, omit `--labels-only`.

A setup agent may start a background watcher from the current Herdr pane environment:

```sh
mkdir -p "$HOME/.config/herdr"
nohup "$HOME/.local/bin/herdr-tab-titles" --labels-only --watch \
  >> "$HOME/.config/herdr/tab-label-watcher.log" 2>&1 < /dev/null &
echo "$!" > "$HOME/.config/herdr/tab-label-watcher.pid"
```

First check for an existing watcher and reuse it, or stop only the verified reporter process before replacing it. Do not kill a process based solely on a stale PID file. Never stop the Herdr server to restart this reporter.

This repository does not install an automatic login/startup service. Explain that the watcher must be started again from a Herdr pane after a reboot. Do not create a startup service unless the user asks for it; it needs the correct session environment.

## 7. Verify the actual result

Check `herdr server reload-config` for diagnostics, then inspect tabs, agents, and spaces through the API. Use IDs returned by the CLI, not screenshot sample IDs. Confirm:

- Top numbers match current tab positions and restart in each space.
- Claude/Codex/OpenCode agent-only tabs have compact marks.
- Shell tabs keep readable names and the appropriate host OS icon.
- Sidebar titles remain readable; mascot art and model labels are present when supported.
- The space name completes before the trailing model is clipped.
- The watcher stays running and its log has no repeating errors.

Use a visible screenshot only when available through permitted UI tools; do not claim visual verification from API data alone. The README screenshot contains an explicitly temporary OpenCode demo title/time. Never hardcode that demo data into a user's live session.

SSH OS detection uses a separate noninteractive read-only connection. Explain the globe fallback for password-only sessions or failed probes. No remote shell commands should be typed into an active terminal to test this feature.

## 8. Handoff and restoration

Tell the user which config was backed up, which font provides the glyphs, which watcher mode is running, and how to restart it after reboot. Point out the stock-Herdr limits in the README.

To restore undecorated tab names, stop the verified watcher and run:

```sh
herdr-tab-titles --restore-tabs
```

To restore the previous appearance/keybindings, copy back the desired installer backup and reload Herdr's configuration. Do not stop agents or destroy panes/tabs to undo a presentation change.
