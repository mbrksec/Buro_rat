from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

KEY = b'bucoookguclusifre'  # 16, 24, veya 32 byte

def encrypt(data):
    cipher = AES.new(KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
    iv = cipher.iv
    return base64.b64encode(iv + ct_bytes).decode()

def decrypt(enc_data):
    enc = base64.b64decode(enc_data)
    iv = enc[:16]
    ct = enc[16:]
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()
