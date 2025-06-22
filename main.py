import base64
import requests
import yaml
import os
import urllib.parse  # Untuk dekoding

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
                server_details = server_info.split(':')
                if len(server_details) != 2:
                    print("⚠️ Format server info tidak valid")
                    continue

                server, port_and_query = server_details
                port = port_and_query.split('?')[0]
                query = port_and_query.split('?')[1] if '?' in port_and_query else ''
                params = {param.split('=')[0]: param.split('=')[1] for param in query.split('&') if '=' in param}

                # Hanya memproses jika tipe adalah ws dan port 443 atau 80
                if params.get('type') == 'ws' and port in ['443', '80']:
                    # Mengambil dan mendekode name
                    name = node.split('#')[1].strip() if '#' in node else 'default_name'
                    name = urllib.parse.unquote(name)  # Dekode nama

                    # Ambil host dan hapus bagian setelah '#'
                    host = params.get('host', '')
                    if '#' in host:
                        host = host.split('#')[0]  # Hapus bagian setelah '#'
                    host = urllib.parse.unquote(host)  # Dekode host

                    # Ambil sni dan hapus bagian setelah '#'
                    sni = params.get('sni', '')
                    if '#' in sni:
                        sni = sni.split('#')[0]  # Hapus bagian setelah '#'
                    sni = urllib.parse.unquote(sni)  # Dekode SNI

                    # Ambil path dan mendekode, pastikan tidak ada karakter '#' setelahnya
                    path = urllib.parse.unquote(params.get('path', ''))
                    if '#' in path:
                        path = path.split('#')[0]  # Hapus bagian setelah '#'
                    path = path.replace('%2F', '/')  # Ganti '%2F' dengan '/'

                    # Pastikan tidak ada karakter '#' di akhir path
                    if path.endswith('#'):
                        path = path[:-1]

                    proxies.append({
                        "name": name,
                        "server": server,
                        "port": int(port),
                        "type": "trojan",
                        "password": urllib.parse.unquote(credentials),  # Dekode password
                        "skip-cert-verify": True,
                        "sni": sni,  # Set SNI yang telah dibersihkan
                        "network": "ws",
                        "ws-opts": {
                            "path": path,  # Path yang sudah dibersihkan
                            "headers": {
                                "Host": host  # Set Host yang telah dibersihkan
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
