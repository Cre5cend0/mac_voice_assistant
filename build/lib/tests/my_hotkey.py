# Keyboard module in Python
import keyboard
from main import start

# press ctrl+shift+z to print "Hotkey Detected"
keyboard.add_hotkey('ctrl + shift + space', start)

keyboard.wait('esc')
