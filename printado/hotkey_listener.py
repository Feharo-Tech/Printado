from pynput import keyboard
from printado.core.utils import delete_temp_screenshot
import subprocess
import sys
import os


main_process = None
pressed_keys = set() 

def run_screenshot_tool():
    global main_process
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))

    if main_process is None or main_process.poll() is not None:
        main_process = subprocess.Popen([sys.executable, script_path])

def stop_screenshot_tool():
    global main_process
    if main_process is not None:
        delete_temp_screenshot()
        main_process.terminate()
        main_process = None

def on_press(key):
    global pressed_keys
    try:
        pressed_keys.add(key) 

        if keyboard.Key.ctrl_l in pressed_keys or keyboard.Key.ctrl_r in pressed_keys:
            if key == keyboard.Key.print_screen:
                run_screenshot_tool()

        if key == keyboard.Key.esc:
            stop_screenshot_tool()

    except AttributeError:
        pass

def on_release(key):
    global pressed_keys
    if key in pressed_keys:
        pressed_keys.remove(key)

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
