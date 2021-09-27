# Keyboard module in Python
import keyboard

# press ctrl+shift+z to print "Hotkey Detected"
keyboard.add_hotkey('ctrl + shift + space', print, args=('Hotkey', 'Detected'))

keyboard.wait('esc')
