import base64
import requests
import yaml
import os

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
            # Mendecode Base64 jika diperlukan
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
                # Menghapus 'trojan://' dan memisahkan bagian
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

                server, port = server_details
                params = server_info.split('?')[1] if '?' in server_info else ''
                param_dict = {key: value for key, value in (x.split('=') for x in params.split('&'))}

                # Mengambil name dari bagian setelah '#'
                name = param_dict.get('name', credentials.split(':')[0])  # Menggunakan username sebagai nama

                proxies.append({
                    "name": name,
                    "server": server,
                    "port": int(port),
                    "type": "trojan",
                    "password": credentials.split(':')[1],  # Mengambil password
                    "skip-cert-verify": True,
                    "sni": param_dict.get('sni', ''),
                    "network": param_dict.get('type', 'ws'),
                    "ws-opts": {
                        "path": param_dict.get('path', '/'),
                        "headers": {
                            "Host": param_dict.get('host', '')
                        }
                    },
                    "udp": True
                })
            except Exception as e:
                print(f"⚠️ Gagal memparsing trojan: {e}")

    proxies_clash = {
        "proxies": proxies
    }
    
    # Menghasilkan YAML tanpa tanda kutip
    yaml_output = yaml.dump(proxies_clash, allow_unicode=True, sort_keys=False, default_style=None)
    return yaml_output.replace('"', '').replace("'", '')

def main():
    nodes = ambil_langganan()
    filtered_nodes = saring_node(nodes)
    os.makedirs("proxies", exist_ok=True)
    with open("proxies/trojan.yaml", "w", encoding="utf-8") as f:
        f.write(konversi_ke_clash(filtered_nodes))

if __name__ == "__main__":
    main()
