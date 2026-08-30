<p align="center">
  <img src="assets/icon.svg" alt="terminaltor icon" width="128"/>
</p>

# Terminaltor

[![CI](https://github.com/Paldom/terminaltor/actions/workflows/ci.yml/badge.svg)](https://github.com/Paldom/terminaltor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![skills.sh](https://skills.sh/b/Paldom/terminaltor)](https://skills.sh/Paldom/terminaltor)

Agent Skills for recording, sanitizing, and rendering terminal session demos - capture real command walkthroughs with agents, redact sensitive output, and render polished casts for READMEs and docs.

Agent Skills for [Claude Code](https://code.claude.com/docs/en/skills) (and any
[Agent Skills](https://agentskills.io)-compatible tool). Each skill is a folder under
[`skills/`](skills/) with a single-purpose `SKILL.md`, trigger evals, and optional
scripts/references — validated on every write, commit, and PR.

## Demo

The pipeline demoing itself — record a session that "leaks" a fake token, scan
it, scrub it, render the sanitized cast:

![Walkthrough: asciinema records a session, the bundled redact script finds and scrubs a leaked token, agg renders the sanitized cast to a GIF](docs/demo/demo.gif)

This demo is itself demo-as-code: regenerate it from the repo root with
`vhs docs/demo/demo.tape` (see the [tape-demo](skills/tape-demo/) skill).

## Quick start

Install with the [skills CLI](https://skills.sh) — auto-detects 70+ agents
(Claude Code, Codex, Cursor, Copilot, pi, …):

```bash
npx skills add Paldom/terminaltor                  # all detected agents
npx skills add Paldom/terminaltor -a codex -a pi   # or target specific agents
```

Or with the [GitHub CLI](https://cli.github.com/manual/gh_skill_install) (≥ 2.90),
including version-pinned installs from releases:

```bash
gh skill install Paldom/terminaltor
gh skill install Paldom/terminaltor <skill> --pin <tag>
```

Or as a Claude Code plugin:

```
/plugin marketplace add Paldom/terminaltor
/plugin install terminaltor@terminaltor
```

Or copy a single skill into a project:

```bash
git clone https://github.com/Paldom/terminaltor.git
cp -r terminaltor/skills/<skill-name> your-project/.claude/skills/
```

Then just describe the task — the skill activates on its description — or invoke it
explicitly with `/<skill-name>`.

## Skills

| Skill | Description |
| --- | --- |
| [tape-demo](skills/tape-demo/) | Creates polished terminal demo GIFs/MP4s as code with VHS `.tape` scripts — simulated typing, themed terminal, hidden setup, reproducible re-renders for READMEs and docs. |
| [cast-record](skills/cast-record/) | Records real terminal sessions to asciicast `.cast` files with asciinema 3.x — interactive or headless/scripted capture with clean-environment hygiene. |
| [cast-redact](skills/cast-redact/) | Scrubs secrets, tokens, usernames, and machine paths from `.cast` recordings before publishing — bundled script catches secrets split across events and in headers. |
| [cast-render](skills/cast-render/) | Renders `.cast` recordings into themed GIFs and MP4s with agg, gifsicle, and ffmpeg — trimming, pacing, brand/neutral themes, README embedding. |

**Which skill?** No recording exists and you want a polished demo → `tape-demo`
(demo-as-code, deterministic). Need the *real* session captured → `cast-record`.
Have a `.cast` with sensitive content → `cast-redact`. Have a clean `.cast` and
want a GIF/MP4 → `cast-render`. The capture pipeline composes:
record → redact → render; a paste-ready orchestration prompt lives in
[docs/setup-prompt.md](docs/setup-prompt.md).

## Repository structure

```
skills/                  # distributed skills, one folder per skill (SKILL.md + evals/ + scripts/)
docs/                    # skill-authoring guide, eval methodology, deployment guide
scripts/                 # deterministic validator used by hooks and CI
skills.sh.json           # skills.sh repo-page customization (groupings)
.claude/                 # agentic dev setup: hooks + bundled add-skill / publish-repo skills
.claude-plugin/          # plugin + marketplace manifests (makes this repo installable)
.local/                  # gitignored working area: sources, research, PROMPT.md (see below)
```

## Working on this repo with an agent

This repo is agent-native: canonical agent instructions live in
[AGENTS.md](AGENTS.md) (CLAUDE.md imports it), hooks validate every `SKILL.md` on
write, `make check` runs the full validator, and CI enforces the same gate on every
PR. The bundled `add-skill` skill walks the eval-first authoring workflow described
in [docs/skill-authoring.md](docs/skill-authoring.md). Maintainers drive sessions
with their own (gitignored, personal) `.local/PROMPT.md` goal prompt.

## Contributing

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for the skill-proposal
process, the authoring workflow, and the PR checklist. Please note the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Support

Questions, ideas, or something not working? Start with [SUPPORT.md](SUPPORT.md) —
bugs and skill proposals have [issue templates](../../issues/new/choose), and
security concerns go through [SECURITY.md](SECURITY.md) (never a public issue).

## License

[MIT](LICENSE) © 2026 Paldom
