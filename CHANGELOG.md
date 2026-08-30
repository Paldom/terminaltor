# Changelog

All notable changes to this repository's skills are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning: [SemVer](https://semver.org) on the plugin manifest
(breaking skill-interface change → major, new skill → minor, fix → patch).

## [Unreleased]

## [0.2.0] - 2026-08-31

### Added
- Adopted the current skillskit gate: executed trigger evals (`make evals`),
  a security scan over skill content and bundled scripts, ruff lint/format,
  README-shape validation, pre-commit hooks and a write-time lint hook.

### Changed
- `cast-render` and `cast-redact` descriptions rewritten after the new eval
  gate showed `cast-render` ranking last on three of its own trigger prompts,
  beaten by `tape-demo`: converting an existing recording is now stated up
  front and distinguished from scripting a demo from scratch. Rank-1 routing
  accuracy 80.0% -> 86.7%.

### Fixed
- `cast-redact`: the asciicast writer chose JSON separators with a conditional
  whose branches were identical, plus an unused loop variable and an unused
  unpacked value. Found by the new lint gate.


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
