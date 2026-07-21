# Setup prompt: terminal demos for your project

Paste the block below as one message into a Claude Code session in the project
you want to demo (terminaltor skills installed). It drives the full pipeline —
scripted demo and/or real capture → redaction → render — with verification
gates between stages. Adjust the bracketed bits first.

```
/goal Produce terminal demo assets for this project using the terminaltor skills, then stop. NEVER run git commit or git push - leave artifacts and sources in the working tree for me.

Deliverables: [a README hero GIF of the quickstart] [an MP4 of the same demo] [docs/demo/ as the asset directory].

Plan of record (ordering is a constraint):
1. DECIDE the path per asset. Polished showcase of known commands -> tape-demo (scripted, no live capture). Authentic run whose real output matters -> cast-record. Never mix paths for one asset.
2. SCRIPTED PATH (tape-demo): write the .tape (Set lines on top; neutral "GitHub Dark" theme unless I gave brand colors - then an inline Set Theme JSON), Hide/Show for setup, Wait /regex/ instead of long Sleeps, fake values only (Hide is presentation, not security). Gate: `vhs validate <tape>` passes, then `vhs <tape>` renders, artifact exists.
3. CAPTURE PATH (cast-record): clean temp dir, generic prompt, fake creds; `asciinema rec --headless --window-size 100x30 -i 2 -c <cmd> --overwrite <name>.raw.cast`. Gate: header line is valid JSON; `asciinema play` spot-check. The raw cast stays untracked.
4. REDACT (cast-redact) - required for every captured cast before it is rendered, committed, or shown to me: run the bundled redact_cast.py --scan first (never read the raw cast into context); apply to <name>.cast (new file); gate: rescan exits 0. If a real credential was recorded, tell me to rotate it.
5. RENDER (cast-render): `agg --theme github-dark --fps-cap 24 --idle-time-limit 3` (or brand hex list), then `gifsicle -O3 --lossy=80 --colors 128`; MP4 via the skill's ffmpeg command when asked. Gate: GIF <= 10 MB reported; MP4 verified with ffprobe/file.
6. EMBED: add the asset + regeneration source (.tape or .cast) under [docs/demo/], wire the README image reference, note MP4s must be uploaded as GitHub attachments (click-to-play).

Parallelism: multiple assets may run in parallel ONLY on disjoint files (different tapes/casts/outputs); redaction of a cast must finish before any render of that cast starts.
Verification bracket: before finishing, re-run every gate end to end (vhs validate + render, redact --scan on every published cast = clean, artifact sizes) and list each gate with its result.
Done when: every deliverable exists with its regeneration source, all gates pass, zero git commits were made, and your final summary lists created files + exact regeneration commands.
```

Notes

- The gates quote the skills' verified commands; if a flag looks unfamiliar,
  the skill bodies are the source of truth (`skills/*/SKILL.md`).
- Prerequisites: `brew install vhs asciinema agg gifsicle` (vhs pulls
  ttyd + ffmpeg). asciinema has no Windows build; VHS does.
- Keep raw captures out of git (the prompt enforces `*.raw.cast` untracked
  until redacted).
