import base64
import json
import os
import requests
import subprocess

# Memastikan V2Ray berada dalam PATH
def check_v2ray_installed():
    try:
        result = subprocess.run(['v2ray', 'version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return True
        else:
            print("V2Ray tidak ditemukan. Pesan kesalahan:", result.stderr.decode())
            return False
    except Exception as e:
        print("Kesalahan saat memeriksa V2Ray:", str(e))
        return False

# URL Trojan yang ingin diuji
trojan_url = "trojan://aaaaaaa1-bbbb-4ccc-accc-eeeeeeeeeee1@ava.game.naver.com:443?encryption=none&security=tls&sni=ava.game.naver.com.free.bansos4u.biz.id&fp=randomized&type=ws&host=ava.game.naver.com.free.bansos4u.biz.id&path=%2FFree%2FTG-at-BitzBlack%2F91.187.93.166-443#(AD)%20Andorra%20Telecom%20Sau%20%40BitzBlack"

# Memparsing URL Trojan
url_parts = trojan_url.split('@')
credentials = url_parts[0].split('://')[1]
server_info = url_parts[1].split('?')[0]

# Menyiapkan file konfigurasi V2Ray untuk Trojan
v2ray_config = {
    "outbounds": [
        {
            "protocol": "trojan",
            "settings": {
                "servers": [
                    {
                        "address": server_info.split(':')[0],
                        "port": int(server_info.split(':')[1]),
                        "password": credentials,
                        "email": ""
                    }
                ]
            }
        }
    ],
    "inbounds": [
        {
            "port": 1080,
            "protocol": "socks",
            "settings": {
                "auth": "noauth",
                "udp": True,
                "ip": "127.0.0.1"
            }
        }
    ]
}

# Menyimpan konfigurasi ke file config.json
with open('config.json', 'w') as json_file:
    json.dump(v2ray_config, json_file, indent=4)

print("File konfigurasi V2Ray untuk Trojan telah dibuat.")

# Memeriksa apakah V2Ray terinstal
if not check_v2ray_installed():
    print("V2Ray tidak ditemukan. Pastikan V2Ray terinstal dengan benar.")
    exit(1)

# Jalankan V2Ray
os.system("v2ray -config ./config.json &")

# Menguji koneksi
url = "http://www.msftconnecttest.com/connecttest.txt"

proxies = {
    "http": "socks5h://127.0.0.1:1080",
    "https": "socks5h://127.0.0.1:1080",
}

try:
    # Mengirim permintaan GET melalui proxy
    response = requests.get(url, proxies=proxies)

    # Memeriksa status kode
    if response.status_code == 200:
        print("Koneksi berhasil!")
        print(response.text)  # Menampilkan konten
    else:
        print("Koneksi gagal. Kode status:", response.status_code)
except Exception as e:
    print("Terjadi kesalahan:", e)
