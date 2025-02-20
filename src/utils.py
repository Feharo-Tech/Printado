import os

def delete_temp_screenshot():
    temp_file = "temp_screenshot.png"
    if os.path.exists(temp_file):
        os.remove(temp_file)
