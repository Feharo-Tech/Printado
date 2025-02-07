import pyscreenshot as ImageGrab

def capture_screen():
    screenshot = ImageGrab.grab()
    screenshot.save("screenshot.png")
    print("Screenshot salvo como 'screenshot.png'")
