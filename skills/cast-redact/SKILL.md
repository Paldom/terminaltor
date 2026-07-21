---
license: MIT
name: cast-redact
description: Scrubs secrets, tokens, usernames, and machine paths from asciicast .cast recordings before publishing - scan and rewrite via a bundled script that catches secrets split across events and in headers. Use when the user wants to redact, sanitize, scrub, mask, or scan a terminal recording for leaked credentials. Not for editing .env files, trimming casts, or rendering.
---

# cast-redact

Remove sensitive data from an asciicast `.cast` recording before it is
rendered, committed, or shared. Upstream asciinema has no redact command (its
official answer is "edit the NDJSON yourself"), and naive `sed` misses the
worst case: a secret typed during recording echoes **one character per
event**, so no single line contains it. The bundled script matches patterns on
the joined per-channel stream, scrubs header fields too, and verifies its own
output.

## Threat model (be honest about it)

- **Catches:** known secret shapes (GitHub/AWS/Stripe/Slack/Google tokens,
  JWTs, private-key blocks, `KEY=value` assignments), user-supplied regexes,
  known literal values, home-directory paths — including matches split across
  events, hidden in cleared/backspaced output, or sitting in the header's
  `command`/`title`/`env` fields.
- **Does not catch:** secrets with no recognizable shape that you don't
  declare, and secrets whose characters are interleaved with ANSI/OSC control
  sequences or cursor-movement rewrites (styled TUI output can break a token
  across escape codes). A clean scan means "no configured rule matches" —
  it is not proof the file is safe. Pattern-based best effort, not magic.
- **Non-negotiable:** a real credential that was recorded is compromised no
  matter how well it is scrubbed — rotate it.

## When NOT to use

- Secrets in source files (`.env`, configs) — that's not a recording.
- Trimming, speeding up, or restyling a cast → `cast-render`.
- Preventing leaks at capture time (clean env, fake values) → `cast-record`.
- PDFs, images, videos — this operates on asciicast NDJSON only.

## Workflow

Never load the raw cast into the model context (that re-leaks the secret to
logs/telemetry). Work through the script; it prints rule names, counts, and
line numbers — never payloads.

1. **Scan** (read-only; exit 1 = findings, 0 = clean):
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/redact_cast.py" --scan demo.cast
   ```
2. **Extend the rules when needed:**
   - `--paths` — also rewrite `/Users/<name>` and `/home/<name>` to a demo user.
   - `--pattern 'REGEX'` or `--pattern 'REGEX=>replacement'` — extra shapes
     (hostnames, internal domains). Regexes only; never a literal secret on
     the command line (argv leaks into shell history and process lists).
   - `--replace-file secrets.map` — known literal values, one
     `literal=>replacement` per line; keep this file **gitignored**.
   - `--drop-input` — delete all input (`"i"`) events outright.
3. **Apply to a NEW file** (the source is never modified; the script re-scans
   its own output and fails if anything survived):
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/redact_cast.py" demo.cast demo.redacted.cast --paths
   ```
4. **Verify + publish path.** Confirm `--scan demo.redacted.cast` exits 0,
   and for known literals verify independently of the script's own scanner
   (locally, e.g. `grep -qF <literal> demo.redacted.cast` — never in shared
   logs). Spot-check with `asciinema play demo.redacted.cast`, then render via
   `cast-render`. Keep the raw cast out of git (`git check-ignore` to confirm);
   commit only the sanitized one.
5. **Rotate** any real credential that appeared, and say so explicitly.

## Output spec

- `*.redacted.cast`: valid asciicast (same version, event count, and timing
  as the source — except `--drop-input`, which removes input events while
  carrying their v3 intervals forward so cumulative timing is preserved),
  zero remaining rule matches, replacements shown as `[REDACTED:<rule>]`.
- The original file untouched; scan output contains no secret text.

## Gotchas

- Split-across-events is the norm, not the edge case — every echoed keystroke
  is its own event. That's why `sed` per line is not enough and why the script
  joins each channel before matching.
- The header is a leak surface: `-c` command strings, titles, and captured env
  values are scrubbed too (a token passed as a CLI argument lands there).
- Replacement changes text width, so cursor-positioned TUI output may look
  slightly off at the redacted spot — cosmetic; timing is untouched.
- Works on asciicast v2 and v3 (v1 unsupported: convert first with
  `asciinema convert`). Unknown event codes pass through untouched.
- `--self-test` runs the built-in verification suite (split-event, header,
  path, idempotency cases) — run it after modifying the script.
- Prevention beats cure: if the redacted artifact still feels risky,
  re-record with `cast-record` hygiene (fake values, clean HOME).
