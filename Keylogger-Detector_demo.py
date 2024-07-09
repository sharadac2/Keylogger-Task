import os
import psutil
import platform
import time
import hashlib
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(filename='keylogger_detection.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Function to check for suspicious processes
def check_processes():
    suspicious_processes = []
    process_list = ["python", "pynput", "keylogger", "input_hook"]
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            for suspicious in process_list:
                if suspicious in " ".join(proc.info['cmdline']).lower():
                    proc_info = proc.info
                    proc_info['create_time'] = datetime.fromtimestamp(proc_info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                    suspicious_processes.append(proc_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return suspicious_processes

# Function to check for suspicious files
def check_files():
    suspicious_files = []
    file_list = ["keylog.txt", "keylogger.py", "input_log.txt", "hook.py"]
    for root, dirs, files in os.walk(os.path.expanduser("~")):
        for file in files:
            if file.lower() in file_list:
                file_path = os.path.join(root, file)
                file_info = {
                    "path": file_path,
                    "size": os.path.getsize(file_path),
                    "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                }
                suspicious_files.append(file_info)
    return suspicious_files

# Function to get active window title
def get_active_window():
    if platform.system() == 'Windows':
        try:
            import win32gui
            window = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(window)
        except ImportError:
            return "Unknown Window (Win32GUI not available)"
    elif platform.system() == 'Darwin':
        try:
            from AppKit import NSWorkspace
            return NSWorkspace.sharedWorkspace().frontmostApplication().localizedName()
        except ImportError:
            return "Unknown Window (AppKit not available)"
    elif platform.system() == 'Linux':
        try:
            import subprocess
            window = subprocess.check_output(['xdotool', 'getactivewindow', 'getwindowname'])
            return window.decode('utf-8').strip()
        except Exception:
            return "Unknown Window (xdotool not available)"
    return "Unknown Window"

# Function to calculate file hash
def calculate_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

# Function to check network connections
def check_network_connections():
    suspicious_connections = []
    for conn in psutil.net_connections():
        if conn.status == 'ESTABLISHED' and conn.raddr:
            suspicious_connections.append({
                "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
                "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}",
                "status": conn.status,
                "pid": conn.pid
            })
    return suspicious_connections

# Main function to run the detection
def main():
    print("Starting keylogger detection...")
    logging.info("Starting keylogger detection")

    suspicious_processes = check_processes()
    suspicious_files = check_files()
    current_window = get_active_window()
    suspicious_connections = check_network_connections()

    if suspicious_processes:
        print("\nSuspicious processes found:")
        logging.warning("Suspicious processes found")
        for proc in suspicious_processes:
            print(f"PID: {proc['pid']}, Name: {proc['name']}, Cmdline: {proc['cmdline']}, Created: {proc['create_time']}")
            logging.warning(f"Suspicious process - PID: {proc['pid']}, Name: {proc['name']}, Cmdline: {proc['cmdline']}, Created: {proc['create_time']}")

    if suspicious_files:
        print("\nSuspicious files found:")
        logging.warning("Suspicious files found")
        for file in suspicious_files:
            print(f"File: {file['path']}, Size: {file['size']} bytes, Modified: {file['modified']}")
            file_hash = calculate_file_hash(file['path'])
            print(f"SHA256 Hash: {file_hash}")
            logging.warning(f"Suspicious file - Path: {file['path']}, Size: {file['size']} bytes, Modified: {file['modified']}, Hash: {file_hash}")

    if suspicious_connections:
        print("\nSuspicious network connections found:")
        logging.warning("Suspicious network connections found")
        for conn in suspicious_connections:
            print(f"Local: {conn['local_address']}, Remote: {conn['remote_address']}, Status: {conn['status']}, PID: {conn['pid']}")
            logging.warning(f"Suspicious connection - Local: {conn['local_address']}, Remote: {conn['remote_address']}, Status: {conn['status']}, PID: {conn['pid']}")

    if suspicious_processes or suspicious_files or suspicious_connections:
        print("\nPotential keylogger activity detected.")
        print(f"Active Window: {current_window}")
        logging.warning(f"Potential keylogger activity detected. Active Window: {current_window}")
    else:
        print("\nNo keylogger activity detected.")
        logging.info("No keylogger activity detected")

    print("\nDetection complete. Check 'keylogger_detection.log' for detailed information.")

if __name__ == "__main__":
    main()