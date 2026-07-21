# Starter tape: neutral theme, README-friendly geometry.
# Render: vhs demo.tape   Validate first: vhs validate demo.tape
Output demo.gif
# Output demo.mp4        # uncomment for a video too

Require echo

Set Shell "bash"
Set FontSize 18
Set Width 1200
Set Height 600
Set Padding 20
Set Theme "GitHub Dark"
Set TypingSpeed 50ms
Set Framerate 24

# --- hidden setup: runs but is not rendered; fake values only ---
Hide
Type "clear"
Enter
Show

Type "echo 'hello from terminaltor'"
Sleep 300ms
Enter
Sleep 2s
