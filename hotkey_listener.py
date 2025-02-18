from pynput import keyboard
import subprocess
import sys
import os
import signal

main_process = None 

def run_screenshot_tool():
    global main_process
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))

    if main_process is None or main_process.poll() is not None:
        main_process = subprocess.Popen([sys.executable, script_path])

def stop_screenshot_tool():
    global main_process
    if main_process is not None:
        main_process.terminate() 
        try:
            main_process.wait(timeout=2)  
        except subprocess.TimeoutExpired:
            main_process.kill()
        main_process = None

def on_press(key):
    try:
        if key == keyboard.Key.print_screen:
            run_screenshot_tool()

        if key == keyboard.Key.esc: 
            stop_screenshot_tool()

    except AttributeError:
        pass

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
