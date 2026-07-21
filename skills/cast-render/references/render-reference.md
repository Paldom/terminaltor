# Render pipeline reference (verified 2026-07-21)

Verified against agg 1.9.0 (`agg --help` on a local install + official docs),
gifsicle 1.96 man page, ffmpeg docs, and docs.github.com.

**Contents:** [agg flags](#agg-flags) · [Custom themes](#custom-themes) ·
[gifsicle](#gifsicle) · [GIF to MP4](#gif-to-mp4) ·
[GitHub embedding rules](#github-embedding-rules) · [Sources](#sources)

## agg flags

| Flag | Default | Purpose |
| --- | --- | --- |
| `--theme <name-or-hex-list>` | dracula | color theme (see below) |
| `--font-size <px>` | 16 | glyph size (drives output pixel size) |
| `--font-family <list>` | — | full chain override (must start monospace) |
| `--text-font-family` / `--emoji-font-family` | JetBrains Mono… / platform emoji | partial overrides |
| `--font-dir <dir>` | — | extra font directories (repeatable) |
| `--line-height <n>` | 1.4 | typography |
| `--speed <n>` | 1 | playback speed multiplier |
| `--fps-cap <n>` | 30 | frame-rate ceiling (lower = smaller GIF) |
| `--idle-time-limit <secs>` | 5 | cap pauses at render time |
| `--last-frame-duration <secs>` | 3 | hold the final frame |
| `--select <selector>` | — | trim: `5..30s`, `10%..90%`, `marker:a..marker:b`, `markers`, `event:100` |
| `--cols <n>` / `--rows <n>` | recorded | override terminal geometry |
| `--no-loop` | loops | disable GIF looping |
| `--bold-is-bright` | off | render bold with bright colors |
| `--renderer swash\|resvg` | swash | rendering backend |
| `--font-antialiasing` / `--font-hinting` | on | glyph rendering |

Input: asciicast **v1, v2, v3**, from a path or URL. agg embeds JetBrains
Mono, Noto Color Emoji/Emoji, Noto Sans CJK JP, and Symbols Nerd Font — Nerd
Font glyphs render with no font install (agg ≥1.8).

## Custom themes

`--theme` accepts a built-in name (asciinema, dracula, github-dark,
github-light, gruvbox-dark, kanagawa, kanagawa-dragon, kanagawa-light,
monokai, nord, solarized-dark, solarized-light) or a custom palette as
comma-separated hex triplets **without `#`**:

```
--theme <background>,<foreground>,<color0>,…,<color7>[,<color8>,…,<color15>]
```

Example (10-value form, verified locally):

```bash
agg --theme 29283b,b3b0d6,535178,ef6487,5eca89,fdd877,65aef7,aa7ff0,43c1be,ffffff demo.cast demo.gif
```

VHS side of the same contract: a JSON object with named keys
(`background`, `foreground`, `black`…`brightWhite`) — see the tape-demo skill.

## gifsicle

```bash
gifsicle -O3 --lossy=80 --colors 128 demo.gif -o demo.opt.gif
```

- `-O3`: tries several optimization methods (slower, usually best).
- `--lossy[=N]`: lossy LZW compression; higher N = smaller + more artifacts
  (default lossiness 20; 30–100 is the practical range).
- `--colors N`: quantize to N colors (2–256) — biggest lever on size.

## GIF to MP4

ffmpeg cannot read `.cast`; convert the rendered GIF (or use VHS's native MP4
output for scripted demos):

```bash
ffmpeg -i demo.gif -movflags +faststart -pix_fmt yuv420p \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" demo.mp4
```

- `-pix_fmt yuv420p` — without it x264 may emit 4:4:4, which QuickTime and
  many players can't decode.
- `scale=trunc(iw/2)*2:trunc(ih/2)*2` — x264 + yuv420p require even
  dimensions; this rounds down safely.
- `-movflags +faststart` — moves the moov atom to the front for instant
  playback start.
- Add `-c:v libx264` to be explicit (it is the default for `.mp4`).
- Result is silent video (terminal recordings have no audio track).

## GitHub embedding rules

Per docs.github.com ("Attaching files", "About large files on GitHub",
"Basic writing and formatting syntax") and the GFM spec:

- Images incl. GIFs: attach/reference up to **10 MB**; GIFs referenced with
  `![alt](path.gif)` animate inline (browser-native `<img>` GIF behavior).
- Videos: `.mp4`, `.mov`, `.webm` as **uploaded attachments** (drag into a
  README editor, issue, PR, discussion, or release) — rendered as a
  click-to-play player. **10 MB** on free plans, **100 MB** on paid.
- Raw `<script>`, `<iframe>`, `<style>` are filtered by the GFM tagfilter —
  the asciinema web player cannot be embedded in a README.
- Theme-aware images are official: `<picture>` +
  `<source media="(prefers-color-scheme: dark)" srcset="dark.gif">`.
- Committing artifacts to the repo: Git warns >50 MiB and blocks >100 MiB;
  browser uploads cap at 25 MiB.

## Sources

- agg usage/install: <https://docs.asciinema.org/manual/agg/> ·
  <https://github.com/asciinema/agg> (releases: v1.9.0, 2026-05-29)
- asciicast2gif deprecation: <https://github.com/asciinema/asciicast2gif>
- gifsicle: <https://www.lcdf.org/gifsicle/man.html>
- ffmpeg: <https://ffmpeg.org/ffmpeg-formats.html> (faststart),
  <https://ffmpeg.org/ffmpeg-filters.html#scale-1>, <https://ffmpeg.org/ffmpeg-utils.html>
- GitHub: <https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files>,
  <https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github>,
  <https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax>,
  <https://github.github.com/gfm/#disallowed-raw-html-extension->
