# VHS tape reference (verified 2026-07-21)

Verified against the official README (<https://github.com/charmbracelet/vhs>)
and a local VHS v0.10.0 install; latest release v0.11.0 (2026-03-10).

**Contents:** [CLI](#cli) · [Outputs](#outputs) · [Settings](#settings) ·
[Actions](#actions) · [Waiting](#waiting) · [Hide-Show and secrets](#hide-show-and-secrets) ·
[Theming contract](#theming-contract) · [CI](#ci) · [Sources](#sources)

## CLI

| Command | Purpose |
| --- | --- |
| `vhs demo.tape` | Render every `Output` in the tape |
| `vhs validate demo.tape` | Parse-check tape(s) without executing |
| `vhs new demo.tape` | Create a documented example tape |
| `vhs record > cassette.tape` | Generate a tape from live keystrokes (exit shell to stop) |
| `vhs themes` | List all bundled theme names (~348) |
| `vhs publish demo.gif` | Upload GIF to vhs.charm.sh for a shareable URL |

Install: `brew install vhs` (macOS; pulls `ttyd` + `ffmpeg`) or
`go install github.com/charmbracelet/vhs@latest` (then install ttyd/ffmpeg
yourself). Linux, macOS, and Windows binaries exist (`winget install
charmbracelet.vhs`, `scoop install vhs`). Rendering drives a headless
Chromium via go-rod — this is why only system-installed fonts work.

## Outputs

`Output <path>` — repeatable; format by extension: `.gif`, `.mp4`, `.webm`,
a directory path for PNG frames, and `.txt`/`.ascii` for golden-file text
output (documented under the README's CI section).

## Settings

All `Set` lines belong at the top. Official rule (README, verbatim):
"Setting must be administered at the top of the tape file. Any setting
(except `TypingSpeed`) applied after a non-setting or non-output command
will be ignored."

| Setting | Example | Notes |
| --- | --- | --- |
| Shell | `Set Shell "bash"` | avoid personal shell config |
| FontSize | `Set FontSize 18` | px |
| FontFamily | `Set FontFamily "JetBrains Mono"` | must be system-installed |
| Width / Height | `Set Width 1200` / `Set Height 600` | px, locks aspect |
| Padding / Margin | `Set Padding 20` / `Set Margin 20` | px |
| MarginFill | `Set MarginFill "#674EFF"` | color or image behind terminal |
| WindowBar | `Set WindowBar Colorful` | macOS-style chrome |
| WindowBarSize | `Set WindowBarSize 40` | implemented; not in README docs |
| BorderRadius | `Set BorderRadius 8` | rounded corners |
| LineHeight / LetterSpacing | `Set LineHeight 1.4` | typography |
| TypingSpeed | `Set TypingSpeed 50ms` | the one setting changeable mid-tape |
| Theme | `Set Theme "GitHub Dark"` or inline JSON | see contract below |
| Framerate | `Set Framerate 30` | drop to 5–10 for small GIFs |
| PlaybackSpeed | `Set PlaybackSpeed 2` | speed up final render |
| LoopOffset | `Set LoopOffset 60%` | start GIF loop mid-way |
| CursorBlink | `Set CursorBlink false` | steadier stills |
| WaitTimeout | `Set WaitTimeout 30s` | default `Wait` timeout is 15s |

`Require <program>` lines (also top-of-tape) abort the render if a binary is
missing.

## Actions

- `Type "text"` — quotes inside: switch quote style or backticks;
  `Type@250ms "slow"` overrides speed for one command.
- Keys: `Enter`, `Backspace`, `Tab`, `Space`, `Escape`, `Up`/`Down`/`Left`/`Right`
  (repeat count: `Up 3`), `PageUp`/`PageDown`, `ScrollUp`/`ScrollDown` (v0.11+),
  `Ctrl[+Alt][+Shift]+<key>` (arrow combos v0.11+). Keys accept `@time` and counts.
- `Sleep 500ms` / `Sleep 2s` / bare seconds (`Sleep 2`).
- `Screenshot shot.png` — still frame at that point.
- `Copy "text"` / `Paste` — clipboard.
- `Source setup.tape` — include another tape (composition).
- `Env KEY "value"` — set an environment variable for the session.

## Waiting

`Wait` blocks until a regex matches, replacing brittle `Sleep` for
variable-duration commands:

- `Wait` — default pattern `/>$/` (a prompt), scope `Line`, timeout 15s.
- `Wait /Compiled successfully/` — match on the last line.
- `Wait+Screen /error|done/` — match anywhere on screen.
- `Wait@30s /pattern/` — per-wait timeout override.

## Hide-Show and secrets

`Hide` stops frame capture; `Show` resumes. Hidden commands still execute —
use for `git clone`, builds, `clear`. **Hide is presentation, not security**:
values set while hidden persist in the session and could be printed later by
any visible command. Therefore: fake values only (`Env API_TOKEN
"demo-token-123"`), clean working directory, never production credentials.
Treat any tape like a shell script before running it — it is one.

## Theming contract

Named: `Set Theme "GitHub Dark"` — any name from `vhs themes` / THEMES.md.
Custom (project brand) — inline JSON on one line; keys verified from README:

```
Set Theme { "name": "Brand", "background": "#…", "foreground": "#…", "black": "#…", "red": "#…", "green": "#…", "yellow": "#…", "blue": "#…", "magenta": "#…", "cyan": "#…", "white": "#…", "brightBlack": "#…", "brightRed": "#…", "brightGreen": "#…", "brightYellow": "#…", "brightBlue": "#…", "brightMagenta": "#…", "brightCyan": "#…", "brightWhite": "#…", "cursor": "#…", "selection": "#…" }
```

Mapping to agg custom themes (for the `.cast` pipeline): agg takes
`bg,fg,color0..7[,color8..15]` hex values without `#` — same palette, flat
list (see the cast-render skill).

## CI

```yaml
- uses: actions/checkout@v4
- uses: charmbracelet/vhs-action@v2   # latest major: v2 (v2.1.0); pin to a commit SHA in hardened repos
  with:
    path: demo.tape
# pair with an auto-commit or PR action so README assets never drift
```

Tapes execute commands: run PR-triggered renders with read-only permissions,
no secrets in the job env, and never via `pull_request_target`.

The action installs JetBrains Mono by default; set `install-fonts: true` for
extra fonts.

## Sources

- README + command reference: <https://github.com/charmbracelet/vhs>
- Themes list: <https://github.com/charmbracelet/vhs/blob/main/THEMES.md>
- Releases: <https://github.com/charmbracelet/vhs/releases>
- CI action: <https://github.com/charmbracelet/vhs-action>
