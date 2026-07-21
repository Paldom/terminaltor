---
license: MIT
name: tape-demo
description: Creates polished terminal demo GIFs/MP4s as code with VHS .tape scripts - simulated typing, themed terminal, hidden setup, reproducible re-renders for READMEs and docs. Use when the user wants to make, script, or fix a terminal demo, demo gif, or CLI showcase from scratch. Not for recording live sessions or converting existing .cast files.
---

# tape-demo

Produce a reproducible scripted terminal demo: write a VHS `.tape` file that
describes the session (settings, typed commands, pauses), then render it to
GIF/MP4 with `vhs`. The tape is source code — commit it next to the artifact so
the demo regenerates the same way after every CLI change (reproducible given
the same tool versions, fonts, and environment). No live recording, no typos,
no personal shell state on screen.

## When NOT to use

- Capturing a **real** session's authentic output/timing → `cast-record`.
- Converting or restyling an existing `.cast` recording → `cast-render`.
- Removing secrets from a recording → `cast-redact`.
- Browser/GUI walkthroughs — VHS drives a terminal only.

Decision rule: no recording exists yet and the goal is a polished README/docs
demo → this skill.

## Workflow

1. **Plan the story.** Pick 2–5 commands that showcase the tool; run them once
   yourself to know the real output and timing. Add `Require <program>` lines
   for every binary the demo needs.
2. **Write the tape.** Start from `${CLAUDE_SKILL_DIR}/assets/demo-template.tape`
   (neutral theme, README-friendly geometry) or `vhs new demo.tape`. Rules:
   - `Output demo.gif` (+ `Output demo.mp4` for both formats in one run).
   - All `Set` lines at the top: **any setting except `TypingSpeed` placed
     after a non-setting command is silently ignored.**
   - Type/act: `Type "cmd"`, `Enter`, `Sleep 500ms`, `Up`/`Down`, `Ctrl+C`,
     `Type@250ms "slow"` for per-command speed.
   - Variable-duration steps (installs, builds, network): use
     `Wait /pattern/` on expected output instead of guessing a `Sleep`.
     Default scope is the last line, default timeout 15s (`Set WaitTimeout 30s`
     to raise; `Wait+Screen /pattern/` matches the whole screen).
   - Setup/cleanup the viewer shouldn't see goes in a `Hide` … `Show` block
     (e.g. build the binary, `clear`).
3. **Secrets and safety.** A tape is executable code — review every command
   before rendering, and run in a clean directory. `Hide` only stops frame
   capture; the command still runs and its values persist in the session, so
   use obviously fake values (`Env API_TOKEN "demo-token-123"`), never real
   credentials, even hidden.
4. **Validate, then render.**
   ```bash
   vhs validate demo.tape   # parse check, no execution
   vhs demo.tape            # renders every Output
   ```
5. **Check the artifact.** Confirm outputs exist; keep README GIFs under
   GitHub's 10 MB image budget (shrink via `Set Framerate 10`, smaller
   `Width`/`Height`, or gifsicle — see `cast-render` for GIF optimization).
   Re-render after any tape edit; that's the point.
6. **Optional CI regeneration:** `charmbracelet/vhs-action@v2` re-renders tapes
   in GitHub Actions so demos never drift from the CLI.

## Theming (templateable look & feel)

- **Neutral default:** `Set Theme "GitHub Dark"` (or "Dracula",
  "Catppuccin Mocha", … — `vhs themes` lists all ~348 bundled names).
- **Project brand:** inline JSON theme with your palette:
  ```
  Set Theme { "background": "#29283b", "foreground": "#b3b0d6", "black": "#535178", "red": "#ef6487", "green": "#5eca89", "yellow": "#fdd877", "blue": "#65aef7", "magenta": "#aa7ff0", "cyan": "#43c1be", "white": "#ffffff", "brightBlack": "#535178", "brightRed": "#ef6487", "brightGreen": "#5eca89", "brightYellow": "#fdd877", "brightBlue": "#65aef7", "brightMagenta": "#aa7ff0", "brightCyan": "#43c1be", "brightWhite": "#ffffff", "cursor": "#b3b0d6", "selection": "#3d3c58" }
  ```
- Window chrome: `Set WindowBar Colorful`, `Set BorderRadius 8`,
  `Set Margin 20` + `Set MarginFill "#674EFF"` for a framed hero look.

## Output spec

- `demo.tape` committed in the repo (reviewable diff), artifacts (`.gif`/`.mp4`)
  regenerated from it — never hand-edited.
- `vhs validate` passes; render succeeds; GIF within size budget.
- No real credential, hostname, or personal path appears in the tape or render.

## Gotchas

- VHS renders in a headless browser (ttyd + Chromium): `Set FontFamily` only
  works for **system-installed** fonts; missing fonts fall back and can break
  spacing. `brew install ttyd ffmpeg` are required alongside `vhs`.
- GIF is capped at 256 colors — rich themes dither. Prefer MP4 for color-heavy
  demos, or drop `Set Framerate` to 5–10 and post-optimize.
- `vhs record > cassette.tape` bootstraps a tape from your real keystrokes —
  fastest way to discover the command sequence; clean it up afterwards.
- Multiple `Output` lines render all formats in one run; `.txt`/`.ascii`
  outputs give golden files for CI diffing.
- Shell matters: `Set Shell "bash"` avoids surprises from personal zsh/fish
  config; an unthemed prompt keeps the demo neutral.
- Verified against VHS v0.10.0–v0.11.0 (v0.11.0 added `ScrollUp`/`ScrollDown`).

Full verified command/setting reference: `references/tape-reference.md`.
Starter template: `assets/demo-template.tape`.
