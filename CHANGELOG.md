# Changelog

All notable changes to this repository's skills are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning: [SemVer](https://semver.org) on the plugin manifest
(breaking skill-interface change → major, new skill → minor, fix → patch).

## [Unreleased]

### Added
- `tape-demo`: scripted VHS `.tape` terminal demos rendered to GIF/MP4 —
  reproducible demo-as-code with theming (named or brand JSON), `Hide`/`Env`
  secret hygiene, `Wait`-based pacing, and a starter template.
- `cast-record`: real terminal-session capture to asciicast `.cast` with
  asciinema 3.x — headless/agent-driven or interactive, clean-environment
  checklist, v3/v2 format guidance.
- `cast-redact`: secret scrubbing for `.cast` files via a bundled
  scan/apply script that matches across event boundaries and header fields,
  with a built-in self-test and an explicit threat model.
- `cast-render`: `.cast` → themed GIF (agg + gifsicle) and MP4 (ffmpeg)
  with render-time trimming (`--select`), pacing, custom hex themes, and
  GitHub README embedding rules.
- `docs/setup-prompt.md`: paste-ready `/goal` that orchestrates the four
  skills into a record → redact → render pipeline.
- README walkthrough GIF (`docs/demo/demo.gif`) rendered from the committed
  `docs/demo/demo.tape` — the pipeline demoing itself, regenerable with
  `vhs docs/demo/demo.tape`.
- Repository scaffolded from the skills template.
