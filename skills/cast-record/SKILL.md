---
license: MIT
name: cast-record
description: Records real terminal sessions to asciicast .cast files with asciinema 3.x - interactive or headless/scripted capture with clean-environment hygiene so machine details and secrets stay out. Use when the user asks to record, capture, or rec a terminal session, command run, or shell activity. Not for authoring scripted demo tapes/gifs, redacting, or rendering casts.
---

# cast-record

Capture a real terminal session — authentic output, colors, and timing — into
an asciicast `.cast` file (newline-delimited JSON) with asciinema 3.x. The
cast is the text-native source of truth: replayable in the terminal, diffable,
and renderable later. Recording is local-first: nothing uploads unless you
explicitly run `asciinema upload`.

## When NOT to use

- A polished, scripted README demo with simulated typing → `tape-demo`
  (nothing real needs capturing).
- Turning an existing `.cast` into GIF/MP4 → `cast-render`.
- Removing sensitive data from a recording → `cast-redact`.
- Hosting, streaming, or embedding the asciinema web player → out of scope.

## Workflow

1. **Prepare a leak-resistant session** (prevention reduces risk; redaction
   still gates publishing):
   - Work in a fresh temp directory; consider `HOME=$(mktemp -d)` for demos
     that print paths, or a stripped environment
     (`env -i HOME=$TMP PATH=/usr/bin:/bin TERM=xterm-256color bash`) —
     inherited variables like `SSH_AUTH_SOCK` or cloud creds otherwise remain
     reachable by whatever you record.
   - Fake credentials only; set a generic prompt (`PS1='$ '`) if your prompt
     shows `user@host`.
   - The `-c` command string and captured env are stored **in the cast
     header** — never put a secret in the command line.
2. **Record.**
   - Scripted/agent-driven (reproducible, no TTY needed):
     ```bash
     asciinema rec --headless --window-size 100x30 -i 2 \
       -c ./demo.sh --overwrite demo.cast
     ```
   - Interactive (you drive): `asciinema rec demo.cast` — end with `ctrl+d`
     or `exit`; `ctrl+\` pauses/resumes capture mid-session.
   - Flags that matter: `--window-size COLSxROWS` fixes dimensions
     (3.x replaced the old `--cols/--rows`); `-i/--idle-time-limit 2` caps
     dead air; `-t "Title"` labels the recording.
   - Treat the recorded command like any executable code: review scripts
     before recording them, and don't record with production credentials in
     the environment.
3. **Verify.** `head -1 demo.cast` must be a JSON header
   (`{"version":3,"term":{"cols":100,"rows":30,...}}`). Replay with
   `asciinema play demo.cast` to check content and pacing.
4. **Pick the format.** 3.x writes asciicast **v3** by default (relative
   timestamps, easiest to edit). For tools that only read v2:
   `asciinema rec -f asciicast-v2 …` or later
   `asciinema convert -f asciicast-v2 demo.cast demo-v2.cast`.
   `asciinema convert demo.cast demo.txt` exports plain text for docs.
5. **Quarantine, then hand off.** Keep the raw cast out of git (e.g. name it
   `*.raw.cast` and gitignore that pattern) until it has been secret-scanned —
   run `cast-redact` before publishing, then `cast-render` for GIF/MP4.

## Output spec

- A `.cast` file with a valid JSON header line and NDJSON events, at the
  agreed dimensions, idle-capped, replayable with `asciinema play`.
- No upload happened; raw cast not committed until scanned/redacted.

## Gotchas

- `-I/--capture-input` records **every keystroke, including passwords typed
  with echo off**. It is off by default; enable only when keystrokes are the
  point, and say so.
- `-i/--idle-time-limit` stores a limit in metadata for players to honor —
  captured timing is unchanged (agg applies its own idle cap at render time).
- Header leaks: `command`, `title`, and captured env (`SHELL` by default,
  more via `--capture-env`) all land in the header — mind what they contain.
- Overwrite/append: asciinema refuses to overwrite existing files without
  `--overwrite`; `-a/--append` continues a previous recording instead.
- No Windows support (GNU/Linux, macOS, FreeBSD). Verified against asciinema
  3.1.0; 3.x line current as of mid-2026 (3.2.1).
- Everything printed to the terminal is in the cast — including text later
  cleared or backspaced over. Assume the file contains more than the final
  screen showed.
