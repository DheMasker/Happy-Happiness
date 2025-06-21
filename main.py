import base64
import requests
import yaml
import os
import json

# Daftar sumber langganan
SUB_LINKS = [ 
    "https://raw.githubusercontent.com/sevcator/5ubscrpt10n/refs/heads/main/full/5ubscrpt10n-b64.txt"
]

BUGCDN = "104.22.5.240"

def ambil_langganan():
    semua_node = []
    for url in SUB_LINKS:
        try:
            print(f"Mengambil langganan: {url}")
            res = requests.get(url, timeout=60)
            konten = res.text.strip()
            if konten:
                konten = base64.b64decode(konten + '===').decode('utf-8', errors='ignore')
            baris = [line.strip() for line in konten.splitlines() if line.strip()]
            semua_node.extend(baris)
        except Exception as e:
            print(f"❌ Kesalahan sumber langganan: {url} -> {e}")
    return semua_node

def saring_node(nodes):
    terfilter = []
    for node in nodes:
        if node.startswith("trojan://"):
            terfilter.append(node)
    return terfilter

def konversi_ke_clash(nodes):
    proxies = []

    for node in nodes:
        if node.startswith("trojan://"):
            try:
                raw = node[10:]  # Menghapus 'trojan://'
                parts = raw.split('@')
                if len(parts) != 2:
                    print("⚠️ Format node Trojan tidak valid")
                    continue

                credentials, server_info = parts
                server_details = server_info.split(':')
                if len(server_details) != 2:
                    print("⚠️ Format server info tidak valid")
                    continue

                # Mengambil trojan_config dari credentials
                trojan_config = credentials.split("#", 1)[0]  # Asumsi config ada di bagian ini
                config = json.loads(trojan_config.replace("false", "False").replace("true", "True"))

                # Menggunakan nilai dari config dan BUGCDN
                proxies.append({
                    "name": config.get("ps", "Tanpa Nama"),  # Memastikan 'name' diambil dari config
                    "server": BUGCDN,  # Menggunakan BUGCDN
                    "port": config["port"],  # Menggunakan port dari config
                    "type": "trojan",
                    "password": config["password"],  # Menggunakan password dari config
                    "skip-cert-verify": True,
                    "sni": config.get("host", ""),  # Menggunakan host dari config jika ada
                    "network": config.get("net", "ws"),  # Menggunakan network dari config
                    "ws-opts": {
                        "path": config.get("path", "/trojan-ws"),  # Menggunakan path dari config
                        "headers": {"Host": config.get("host", "")}  # Menggunakan host sebagai header
                    },
                    "udp": True
                })
            except Exception as e:
                print(f"⚠️ Gagal memparsing trojan: {e}")

    proxies_clash = {
        "proxies": proxies
    }
    return yaml.dump(proxies_clash, allow_unicode=True, sort_keys=False)

def main():
    nodes = ambil_langganan()
    filtered_nodes = saring_node(nodes)
    os.makedirs("proxies", exist_ok=True)
    with open("proxies/trojan.yaml", "w", encoding="utf-8") as f:
        f.write(konversi_ke_clash(filtered_nodes))

if __name__ == "__main__":
    main()
