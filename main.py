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
            # Mendapatkan informasi server dan port
            raw = node[10:]  # Menghapus 'trojan://'
            parts = raw.split('@')
            if len(parts) != 2:
                continue

            server_info = parts[1].split(':')
            if len(server_info) < 2:
                continue

            # Mengambil port sebelum tanda tanya atau karakter lainnya
            server = server_info[0]
            port_info = server_info[1].split('?')[0]  # Ambil bagian sebelum tanda tanya atau karakter lainnya

            try:
                port = int(port_info)  # Convert port to integer
            except ValueError:
                continue  # Jika gagal, lewati node ini

            # Memeriksa apakah port adalah 80 atau 443
            if port in [80, 443]:
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
                if len(server_details) < 2:
                    print("⚠️ Format server info tidak valid")
                    continue

                server = server_details[0]
                port_info = server_details[1].split('?')[0]  # Ambil port sebelum tanda tanya
                port = int(port_info)  # Convert port to integer

                # Memproses parameter tambahan
                params = {}
                if '?' in server_info:
                    param_str = server_info.split('?')[1]
                    params = dict(param.split('=') for param in param_str.split('&'))

                proxies.append({
                    "name": params.get("name", "Tanpa Nama"),  # Mengambil nama dari parameter atau default
                    "server": server,
                    "port": port,
                    "type": "trojan",
                    "password": credentials.split(':')[0],  # Mengambil password
                    "skip-cert-verify": True,
                    "sni": params.get("sni", ""),  # Menggunakan sni jika ada
                    "network": "ws",  # Menggunakan network ws
                    "ws-opts": {
                        "path": params.get("path", "/trojan-ws"),  # Menggunakan path jika ada
                        "headers": {"Host": params.get("host", "")}  # Menggunakan host jika ada
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
