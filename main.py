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

                password, server_info = parts
                server_details = server_info.split(':')
                if len(server_details) != 2:
                    print("⚠️ Format server info tidak valid")
                    continue

                server, port = server_details[0], server_details[1]  # server dan port
                params = server_info.split('/?')[1] if '/?' in server_info else ''
                param_parts = params.split('&')
                
                # Mengambil parameter yang diperlukan
                network = param_parts[0].split('=')[1] if 'type=' in param_parts[0] else ''
                host = next((p.split('=')[1] for p in param_parts if 'host=' in p), '')
                path = next((p.split('=')[1] for p in param_parts if 'path=' in p), '/')
                sni = next((p.split('=')[1] for p in param_parts if 'sni=' in p), '')
                allow_insecure = next((p.split('=')[1] for p in param_parts if 'allowInsecure=' in p), '0')

                proxies.append({
                    "name": server_info.split("#")[1] if "#" in server_info else "Unknown",  # Nama
                    "server": server,  # Server
                    "port": int(port),  # Port
                    "type": "trojan",  # Tipe
                    "password": password,  # Password
                    "network": network,  # Network
                    "ws-opts": {
                        "path": path,  # Path
                        "headers": {
                            "Host": host  # Host
                        }
                    },
                    "skip-cert-verify": allow_insecure == '1',  # Mengubah 1/0 menjadi True/False
                    "sni": sni,  # SNI
                    "tls": True,  # TLS
                    "udp": True  # UDP
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
