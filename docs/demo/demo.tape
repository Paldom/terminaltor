# terminaltor README walkthrough: record -> scan -> scrub -> render.
# Regenerate from the repo root: vhs docs/demo/demo.tape
Output docs/demo/demo.gif

Require asciinema
Require agg
Require python3

Set Shell "bash"
Set FontSize 17
Set Width 1200
Set Height 660
Set Padding 16
Set Theme "GitHub Dark"
Set TypingSpeed 35ms
Set Framerate 16
Set WindowBar Colorful
Set BorderRadius 8

Hide
Type "export PS1='$ ' && clear"
Enter
Show

Type "# 1. record a real terminal session (the demo 'leaks' a fake token)"
Enter
Type `asciinema rec --headless --window-size 80x10 --overwrite -c "sh -c 'echo deploying...; echo token=sk_live_FAKE0123456789ABCD; echo deploy complete'" /tmp/demo.cast`
Enter
Sleep 1.5s
Type "# 2. scan the recording for leaked secrets"
Enter
Type "python3 skills/cast-redact/scripts/redact_cast.py --scan /tmp/demo.cast"
Enter
Sleep 2s
Type "# 3. scrub them (source file is never touched)"
Enter
Type "python3 skills/cast-redact/scripts/redact_cast.py /tmp/demo.cast /tmp/demo.redacted.cast --force"
Enter
Sleep 2s
Type "# 4. render a README-ready gif from the sanitized cast"
Enter
Type "agg --theme github-dark /tmp/demo.redacted.cast /tmp/demo.gif"
Enter
Sleep 1.5s
Type "# shipped."
Enter
Sleep 3s
