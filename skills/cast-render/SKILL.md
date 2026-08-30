---
license: MIT
name: cast-render
description: Converts an existing asciinema .cast recording into a themed GIF or MP4 via agg, gifsicle and ffmpeg - trim, speed and idle control, shrinking an oversized gif to a size budget. Use when a recording already exists and the user asks to convert, render, trim, speed up, shrink or embed it. Not for scripting a demo from scratch, capturing a session, or screen-recording video.
---

# cast-render

Turn an existing asciicast `.cast` recording into publishable artifacts: a
themed GIF (agg → gifsicle) and/or an MP4 (ffmpeg), sized for GitHub READMEs.
All presentation decisions — trim, speed, idle caps, theme — happen at render
time; the source cast is never modified.

## When NOT to use

- No recording exists and the goal is a scripted demo → `tape-demo`.
- Capturing a session in the first place → `cast-record`.
- Secrets/paths in the recording → `cast-redact` (and do it **before**
  rendering — ask/check if the cast was scanned).
- Generic video editing (screen recordings, mov files) — this consumes
  asciicast only.

## Workflow

1. **Precondition:** the cast is sanitized (`cast-redact --scan` exits clean)
   or contains nothing sensitive by construction.
2. **Render the GIF** (agg accepts asciicast v1, v2, and v3):
   ```bash
   agg --theme github-dark --font-size 16 --fps-cap 24 --idle-time-limit 3 demo.cast demo.gif
   ```
   - Pacing: `--speed 1.5` (playback multiplier), `--idle-time-limit N`
     (cap dead air, default 5s), `--last-frame-duration 3`.
   - Trim at render time: `--select 5..30s`, `--select 10%..90%`, or
     marker-based `--select marker:build..marker:test` (times are on the
     adjusted timeline, after idle/speed).
   - Geometry: `--cols 100 --rows 30` overrides the recorded size.
3. **Optimize the GIF:**
   ```bash
   gifsicle -O3 --lossy=80 --colors 128 demo.gif -o demo.opt.gif
   ```
   Report the final size; GitHub renders README images (incl. GIFs, which
   browsers autoplay/loop) up to the 10 MB image budget.
4. **MP4 when asked** (verified pipeline — ffmpeg cannot read `.cast`
   directly, so convert the rendered GIF):
   ```bash
   ffmpeg -i demo.gif -c:v libx264 -an -movflags +faststart -pix_fmt yuv420p \
     -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" demo.mp4
   ```
   `yuv420p` + even dimensions are required for broad player compatibility;
   `+faststart` moves metadata up for streaming; `-an` marks it explicitly
   audio-less. Verify: `ffprobe -v error -select_streams v:0 -show_entries
   stream=codec_name,pix_fmt,width,height -of json demo.mp4` — expect h264,
   yuv420p, even dimensions. Note: a GIF-derived MP4 inherits the GIF's
   256-color quantization — it wins on size/delivery, not color fidelity.
   For true-color MP4, render natively from a tape (`tape-demo`).
5. **Embed guidance:**
   - GIF: plain `![demo](docs/demo.gif)` — autoplays inline.
   - MP4: upload as an attachment on github.com (drag into a README editor,
     issue, PR, or release) — renders as a click-to-play player. Limits:
     `.mp4`/`.mov`/`.webm`, 10 MB on free plans, 100 MB on paid.
   - Dark/light parity: render two GIFs with matching themes and serve via
     `<picture><source media="(prefers-color-scheme: dark)" …>` (officially
     supported on GitHub).
   - Git limits if committing artifacts: warning >50 MiB, block >100 MiB —
     never commit files that big; regenerate instead.

## Theming (templateable look & feel)

- **Neutral default:** `--theme github-dark`. Built-ins: asciinema, dracula
  (agg's default), github-dark, github-light, gruvbox-dark, kanagawa,
  kanagawa-dragon, kanagawa-light, monokai, nord, solarized-dark,
  solarized-light.
- **Project brand:** comma-separated hex values (no `#`):
  `--theme bg,fg,color0..color7[,color8..color15]`, e.g.
  `--theme 29283b,b3b0d6,535178,ef6487,5eca89,fdd877,65aef7,aa7ff0,43c1be,ffffff`.
  Same palette as a VHS JSON theme, flattened (tape-demo documents the VHS
  side of this contract).

## Output spec

- Artifacts rendered from an unmodified, sanitized cast; sizes reported
  against the 10 MB README budget; MP4 (if produced) is yuv420p H.264 with
  even dimensions and faststart.

## Gotchas

- agg embeds JetBrains Mono plus Noto emoji/CJK and Nerd Font symbols — no
  font installation needed; add custom fonts with `--font-dir`/`--font-family`.
- GIF is 256 colors/frame: rich palettes dither, and that quantization carries
  into any MP4 converted from the GIF. Counter with a lower `--fps-cap` and
  `gifsicle --colors`; for true-color video use a native MP4 render.
- `--select` ranges use the **adjusted** timeline (after `--idle-time-limit`
  and `--speed`) — trim after you've settled pacing.
- The recorded terminal size drives pixel size: a 200-col cast makes a huge,
  blurry-when-scaled GIF. Prefer re-rendering with `--cols/--rows` (or
  re-record at ~100×30).
- Markers (`m` events) enable semantic trims; add them at record time.
- agg is the successor to the deprecated asciicast2gif. Verified against
  agg 1.9.0; install via prebuilt binaries/`brew install agg`/
  `cargo install --git https://github.com/asciinema/agg`.

Full flag list and source links: `references/render-reference.md`.
