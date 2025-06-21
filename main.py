import base64
import requests
import os
import json

# Daftar sumber langganan
SUB_LINKS = [ 
    "https://raw.githubusercontent.com/sevcator/5ubscrpt10n/refs/heads/main/full/5ubscrpt10n-b64.txt"
]

def ambil_langganan():
    semua_node = []
    for url in SUB_LINKS:
        try:
            print(f"Mengambil langganan: {url}")
            res = requests.get(url, timeout=60)
            konten = res.text.strip()
            if not konten.startswith("trojan"):
                konten = base64.b64decode(konten + '===').decode('utf-8', errors='ignore')
            baris = [line.strip() for line in konten.splitlines() if line.strip()]
            semua_node.extend(baris)
        except Exception as e:
            print(f"❌ Kesalahan sumber langganan: {url} -> {e}")
    return semua_node

def saring_node(nodes):
    terfilter = []
    for node in nodes:
        if node.startswith("trojan://"):  # Memfilter hanya trojan
            terfilter.append(node)
    return terfilter

def konversi_ke_trojan(nodes):
    proxies = []

    for node in nodes:
        if node.startswith("trojan://"):
            try:
                trojan_config = base64.b64decode(node[10:] + '===').decode('utf-8', errors='ignore')
                config = json.loads(trojan_config.replace("false", "False").replace("true", "True"))
                proxies.append({
                    "username": config.get("ps", "Tanpa Nama"),  # Memastikan 'username' di atas
                    "hostname": config.get("host", ""),
                    "port": int(config.get("port", 443)),  # Default ke port 443
                    "params": {},  # Tambahkan parameter jika ada
                    "hash": config.get("id", "")
                })
            except Exception as e:
                print(f"⚠️ Gagal memparsing trojan: {e}")

    return proxies

def main():
    nodes = ambil_langganan()
    filtered_nodes = saring_node(nodes)
    proxies = konversi_ke_trojan(filtered_nodes)

    os.makedirs("proxies", exist_ok=True)
    with open("proxies/trojan_proxies.txt", "w", encoding="utf-8") as f:
        for proxy in proxies:
            f.write(f"{proxy['username']}@{proxy['hostname']}:{proxy['port']}\n")

if __name__ == "__main__":
    main()
