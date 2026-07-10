# Desktop Control Skill - Manual Installation

Since SkillHub cannot connect to GitHub, here's how to use desktop control:

## Option 1: Use the Python Script Directly

```bash
# Install dependencies
pip install pyautogui keyboard mouse

# Run commands
python3 desktop_control_skill.py mouse_move 500 300
python3 desktop_control_skill.py mouse_click left
python3 desktop_control_skill.py type_text "Hello World"
python3 desktop_control_skill.py press_key enter
python3 desktop_control_skill.py hotkey "ctrl+c"
```

## Option 2: Use with OpenClaw Shell Skill

```bash
# Through OpenClash
# Use the 'shell' skill to run desktop_control_skill.py commands
```

## Option 3: AutoHotkey Script

Create `desktop_control.ahk`:
```autohotkey
; Mouse control
MouseMove, 500, 300
Click

; Keyboard
Send, Hello World
Send, {Enter}
Send, ^c  ; Ctrl+C
```

## Commands Available

| Command | Args | Description |
|---------|------|-------------|
| mouse_move | x y | Move mouse |
| mouse_click | [button] | Click mouse |
| type_text | "text" | Type text |
| press_key | key | Press key |
| hotkey | "key+key" | Key combination |
| screenshot | [path] | Take screenshot |
| get_mouse_position | - | Get current position |
| scroll | amount | Scroll wheel |
| drag_to | x y [duration] | Drag mouse |

## Integration with OpenClash

Since SkillHub is unavailable, use the `shell` skill:

```
# Execute desktop control commands
shell: python3 desktop_control_skill.py mouse_move 100 200
shell: python3 desktop_control_skill.py type_text "Text to type"
```

## Note

The `agent-browser-clawdbot` skill can also automate mouse/keyboard within browsers, which may be sufficient for many tasks.
