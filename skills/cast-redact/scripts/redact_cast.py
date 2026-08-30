#!/usr/bin/env python3
"""Redact secrets from asciicast v2/v3 recordings (.cast).

Matches patterns on the JOINED per-channel stream, so secrets split across
events (e.g. typed characters echoed one event at a time) are still caught.
Also scrubs header fields (command, title, env values). Never prints matched
payload text. Never overwrites the input file.

Modes:
  --scan          report findings (names/counts/locations only); exit 1 if any
  <in> <out>      apply redactions, write sanitized cast to <out>; exit 0
  --self-test     run the built-in verification suite

Exit codes: 0 = success/clean, 1 = scan found matches, 2 = error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile

REPL = "[REDACTED:{}]"

BUILTIN_PATTERNS = [
    ("github-token", r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,255}"),
    ("github-pat", r"github_pat_[A-Za-z0-9_]{20,255}"),
    ("aws-key-id", r"AKIA[0-9A-Z]{16}"),
    ("stripe-key", r"sk_(?:live|test)_[A-Za-z0-9]{10,}"),
    ("sk-token", r"sk-[A-Za-z0-9_-]{20,}"),
    ("slack-token", r"xox[abprs]-[A-Za-z0-9-]{10,}"),
    ("google-api-key", r"AIza[0-9A-Za-z_-]{35}"),
    ("jwt", r"eyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
    (
        "private-key-block",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----",
    ),
    ("bearer-token", r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{16,}"),
    (
        "env-assignment",
        r"\b(?:API|SECRET|TOKEN|PASSWORD|PASSWD|ACCESS|PRIVATE)[A-Z_]*=\s?['\"]?[^\s'\"\[\]]{8,}",
    ),
]

# (?!demo\b) keeps the rules idempotent: the replacement never re-matches.
PATH_PATTERNS = [
    ("home-path-macos", r"/Users/(?!demo\b)[A-Za-z0-9._-]+", "/Users/demo"),
    ("home-path-linux", r"/home/(?!demo\b)[A-Za-z0-9._-]+", "/home/demo"),
]

# Every event code whose payload is a string gets scanned/redacted (o, i, m,
# and any unknown future codes); non-string payloads pass through untouched.


def compile_rules(args):
    rules = []  # (name, compiled_regex, replacement)
    for name, pat in BUILTIN_PATTERNS:
        rules.append((name, re.compile(pat), REPL.format(name)))
    if args.paths:
        for name, pat, repl in PATH_PATTERNS:
            rules.append((name, re.compile(pat), repl))
    for i, spec in enumerate(args.pattern or []):
        if "=>" in spec:
            pat, repl = spec.split("=>", 1)
        else:
            pat, repl = spec, REPL.format(f"custom-{i}")
        rules.append((f"custom-{i}", re.compile(pat), repl))
    if args.replace_file:
        with open(args.replace_file, encoding="utf-8") as f:
            for n, line in enumerate(f):
                line = line.rstrip("\n")
                if not line or line.startswith("#"):
                    continue
                if "=>" in line:
                    lit, repl = line.split("=>", 1)
                else:
                    lit, repl = line, REPL.format(f"literal-{n}")
                rules.append((f"literal-{n}", re.compile(re.escape(lit)), repl))
    return rules


def parse_cast(path):
    """Return (header_dict, lines) where lines are (kind, value):
    kind 'header' | 'event' (parsed list) | 'raw' (comments/blank, kept as-is)."""
    lines = []
    header = None
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            stripped = line.rstrip("\n")
            if header is None:
                if not stripped.strip():
                    raise ValueError("first line must be the JSON header")
                header = json.loads(stripped)
                if header.get("version") not in (2, 3):
                    raise ValueError(f"unsupported asciicast version: {header.get('version')!r}")
                lines.append(("header", header, lineno))
                continue
            if not stripped.strip() or stripped.lstrip().startswith("#"):
                lines.append(("raw", stripped, lineno))
                continue
            ev = json.loads(stripped)
            if not (isinstance(ev, list) and len(ev) == 3):
                raise ValueError(f"line {lineno}: not a [time, code, data] event")
            lines.append(("event", ev, lineno))
    if header is None:
        raise ValueError("empty file")
    return header, lines


def find_spans(joined, rules):
    """All (start, end, repl, name) matches of every rule, overlaps dropped."""
    spans = []
    for name, rx, repl in rules:
        for m in rx.finditer(joined):
            if m.start() != m.end():
                spans.append((m.start(), m.end(), repl, name))
    spans.sort(key=lambda s: (s[0], -(s[1])))
    kept, last_end = [], -1
    for s in spans:
        if s[0] >= last_end:
            kept.append(s)
            last_end = s[1]
    return kept


def channel_view(lines, code):
    """Joined text of one channel + per-event (line_index, start, end) map."""
    parts, index = [], []
    pos = 0
    for i, (kind, val, _lineno) in enumerate(lines):
        if kind == "event" and val[1] == code and isinstance(val[2], str):
            text = val[2]
            index.append((i, pos, pos + len(text)))
            parts.append(text)
            pos += len(text)
    return "".join(parts), index


def rebuild_event(ev_text, a, b, spans):
    """New text for an event covering joined[a:b), given global spans."""
    out, cursor = [], a
    for s, e, repl, _name in spans:
        if e <= a or s >= b:
            continue
        lo, hi = max(s, a), min(e, b)
        out.append(ev_text[cursor - a : lo - a])
        if s >= a:  # this event contains the span start -> emit replacement here
            out.append(repl)
        cursor = hi
    out.append(ev_text[cursor - a : b - a])
    return "".join(out)


def scrub_header(header, rules, findings):
    changed = False
    for key in ("command", "title"):
        v = header.get(key)
        if isinstance(v, str):
            new = v
            for name, rx, repl in rules:
                if rx.search(new):
                    findings.append((name, f"header.{key}", 1))
                    new = rx.sub(repl, new)
            if new != v:
                header[key] = new
                changed = True
    env = header.get("env")
    if isinstance(env, dict):
        for k, v in env.items():
            if isinstance(v, str):
                new = v
                for name, rx, repl in rules:
                    if rx.search(new):
                        findings.append((name, f"header.env.{k}", 1))
                        new = rx.sub(repl, new)
                if new != v:
                    env[k] = new
                    changed = True
    return changed


def drop_input_events(header, lines):
    """Remove "i" events. asciicast v3 intervals are relative, so each dropped
    event's interval is carried onto the next retained event to preserve
    cumulative timing; v2 timestamps are absolute and need no adjustment."""
    v3 = header.get("version") == 3
    out, carry = [], 0.0
    for kind, val, lineno in lines:
        if kind == "event" and val[1] == "i":
            if v3 and isinstance(val[0], (int, float)):
                carry += val[0]
            continue
        if v3 and carry and kind == "event":
            val = [round(val[0] + carry, 6), val[1], val[2]]
            carry = 0.0
        out.append((kind, val, lineno))
    return out


def process(path, rules, drop_input=False):
    """Return (lines, findings, replaced_count). findings = (rule, where, lineno)."""
    header, lines = parse_cast(path)
    findings = []
    scrub_header(lines[0][1], rules, findings)
    replaced = 0
    codes = {v[1] for k, v, _ in lines if k == "event" and isinstance(v[2], str)}
    for code in sorted(codes):
        joined, index = channel_view(lines, code)
        if not joined:
            continue
        spans = find_spans(joined, rules)
        for s, _e, _repl, name in spans:
            first_line = next(lines[i][2] for i, a, b in index if a <= s < b)
            findings.append((name, f'events "{code}"', first_line))
        replaced += len(spans)
        if spans:
            for i, a, b in index:
                ev = lines[i][1]
                ev[2] = rebuild_event(ev[2], a, b, spans)
    if drop_input:
        lines = drop_input_events(header, lines)
    return lines, findings, replaced


def write_cast(lines, out_path):
    d = os.path.dirname(os.path.abspath(out_path)) or "."
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".redact-", suffix=".cast")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            for kind, val, _lineno in lines:
                if kind == "raw":
                    f.write(val + "\n")
                else:
                    f.write(json.dumps(val, ensure_ascii=False, separators=(",", ":")) + "\n")
        os.replace(tmp, out_path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def report(findings):
    counts = {}
    for name, where, lineno in findings:
        counts.setdefault((name, where), [0, lineno])
        counts[(name, where)][0] += 1
    for (name, where), (n, first_line) in sorted(counts.items()):
        print(f"FOUND {name}: {n} match(es) in {where} (first near line {first_line})")


def self_test():
    secret = "sk_live_" + "ABCDEF1234567890"
    token = "ghp_" + "x" * 36
    header = {
        "version": 3,
        "term": {"cols": 80, "rows": 24},
        "command": f"deploy --token {token}",
        "env": {"SHELL": "/bin/bash", "API_KEY": secret},
    }
    events = [[0.1, "o", "starting up\r\n"]]
    events += [[0.05, "o", ch] for ch in secret]  # split across events
    events.append([0.2, "o", "\r\nls /Users/alice/proj\r\n"])
    events.append([0.1, "i", "hunter2-password-x"])
    events.append([0.1, "r", "100x30"])
    events.append([0.1, "o", "done\r\n"])
    with tempfile.TemporaryDirectory() as d:
        src, dst = os.path.join(d, "in.cast"), os.path.join(d, "out.cast")
        with open(src, "w", encoding="utf-8") as f:
            f.write(json.dumps(header) + "\n# a comment\n")
            for ev in events:
                f.write(json.dumps(ev) + "\n")
        ns = argparse.Namespace(paths=True, pattern=[r"hunter2[^\s]+"], replace_file=None)
        rules = compile_rules(ns)
        lines, findings, replaced = process(src, rules)
        write_cast(lines, dst)
        out_header, out_lines = parse_cast(dst)
        joined_o = "".join(v[2] for k, v, _ in out_lines if k == "event" and v[1] == "o")
        joined_i = "".join(v[2] for k, v, _ in out_lines if k == "event" and v[1] == "i")
        assert secret not in joined_o, "split secret survived in output stream"
        assert "hunter2" not in joined_i, "input-channel secret survived"
        assert token not in json.dumps(out_header), "header command secret survived"
        assert secret not in json.dumps(out_header), "header env secret survived"
        assert "/Users/alice" not in joined_o and "/Users/demo" in joined_o, "path rule failed"
        n_in = sum(1 for _ in events)
        n_out = sum(1 for k, _, _ in out_lines if k == "event")
        assert n_in == n_out, "event count changed"
        assert [v[0] for k, v, _ in out_lines if k == "event"] == [e[0] for e in events], (
            "timing changed"
        )
        _rescan_lines, rescan_findings, _ = process(dst, rules)
        assert not rescan_findings, f"re-scan of sanitized file not clean: {rescan_findings}"
        assert replaced >= 3 and findings, "expected findings on first pass"

        # --drop-input on v3: input events removed, cumulative timing preserved
        dropped, _f, _n = process(src, rules, drop_input=True)
        d_events = [v for k, v, _ in dropped if k == "event"]
        assert not any(e[1] == "i" for e in d_events), "input events survived --drop-input"
        total_before = sum(e[0] for e in events)
        total_after = sum(e[0] for e in d_events)
        assert abs(total_before - total_after) < 1e-6, (
            f"v3 cumulative timing changed: {total_before} -> {total_after}"
        )
    print("self-test OK")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("input", nargs="?", help="source .cast (never modified)")
    p.add_argument("output", nargs="?", help="destination for the sanitized .cast")
    p.add_argument(
        "--scan",
        action="store_true",
        help="report findings only; exit 1 if any (no payloads printed)",
    )
    p.add_argument(
        "--paths", action="store_true", help="also rewrite /Users/<x> and /home/<x> to a demo user"
    )
    p.add_argument(
        "--pattern",
        action="append",
        metavar="REGEX[=>REPL]",
        help="extra regex rule (repeatable); do NOT put literal secrets here",
    )
    p.add_argument(
        "--replace-file",
        metavar="FILE",
        help="file of 'literal=>replacement' lines for known secret values (keep it gitignored)",
    )
    p.add_argument(
        "--drop-input", action="store_true", help="remove all input ('i') events from the output"
    )
    p.add_argument("--force", action="store_true", help="allow overwriting an existing output file")
    p.add_argument("--self-test", action="store_true", help="run the built-in verification suite")
    args = p.parse_args()

    if args.self_test:
        self_test()
        return 0
    if not args.input:
        p.error("input file required")
    rules = compile_rules(args)

    if args.scan:
        _lines, findings, _n = process(args.input, rules, drop_input=False)
        if findings:
            report(findings)
            print(
                f"RESULT: {len(findings)} finding group(s) - redact before publishing",
                file=sys.stderr,
            )
            return 1
        print("RESULT: clean (no rule matched)")
        return 0

    if not args.output:
        p.error("output file required (the input is never modified in place)")
    if os.path.abspath(args.input) == os.path.abspath(args.output):
        p.error("output must differ from input")
    if os.path.exists(args.output) and not args.force:
        p.error(f"{args.output} exists (use --force to overwrite)")
    lines, findings, replaced = process(args.input, rules, drop_input=args.drop_input)
    write_cast(lines, args.output)
    report(findings)
    print(f"WROTE {args.output} ({replaced} replacement(s))")
    _l, resid, _n = process(args.output, rules, drop_input=False)
    if resid:
        print("ERROR: sanitized output still matches rules - do not publish", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, json.JSONDecodeError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
