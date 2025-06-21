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
                password = credentials.split(':')[0]  # Mengambil username sebagai password
                name = f"TR-WS-NA 🇰🇷 {server}:{port}"  # Format nama sesuai keinginan
                sni = server_info.split('sni=')[1].split('&')[0] if 'sni=' in server_info else ''  # Mengambil SNI

                # Mengambil host dari query
                query_params = {param.split('=')[0]: param.split('=')[1] for param in server_info.split('?')[1].split('&')}
                host = query_params.get('host', '')

                proxies.append({
                    "name": name,  # Menggunakan format nama yang diinginkan
                    "type": "trojan",
                    "server": server,
                    "port": int(port), 
                    "password": password,
                    "skip-cert-verify": True,
                    "sni": sni,
                    "network": "ws",
                    "ws-opts": {
                        "path": "",  # Dibiarkan kosong jika tidak ada path
                        "headers": {"Host": host}
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
    
    # Membuat direktori untuk menyimpan hasil
    os.makedirs("proxies", exist_ok=True)
    with open("proxies/trojan.yaml", "w", encoding="utf-8") as f:
        f.write(konversi_ke_clash(filtered_nodes))

if __name__ == "__main__":
    main()
