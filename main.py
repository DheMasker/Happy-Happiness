import base64
import requests
import yaml
import os
import urllib.parse

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
                server_details = server_info.split('#')
                if len(server_details) != 2:
                    print("⚠️ Format server info tidak valid")
                    continue
                
                server_port, name = server_details[0], server_details[1]
                server_info_parts = server_port.split(':')
                if len(server_info_parts) != 2:
                    print("⚠️ Format server info tidak valid")
                    continue

                server, port = server_info_parts

                # Memisahkan dan mencetak detail
                server_parameters = server_info.split('&')  # Menggunakan '&' untuk memisahkan parameter
                for detail in server_parameters:
                    key, value = detail.split('=')
                    print(f"{key}: {value}")

                    # Logika tambahan untuk memeriksa format tertentu
                    if key == 'host':
                        host = value
                    elif key == 'path':
                        path = value
                    elif key == 'security':
                        security = value
                    elif key == 'sni':
                        sni = value

                # Dekode nama
                decoded_name = urllib.parse.unquote(name)

                proxies.append({
                    "name": decoded_name,
                    "server": server,
                    "port": int(port),
                    "type": "trojan",
                    "password": credentials,
                    "skip-cert-verify": True,
                    "sni": sni,
                    "network": "ws",
                    "ws-opts": {
                        "path": path,
                        "headers": {
                            "Host": host
                        }
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
