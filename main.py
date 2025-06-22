import base64
import requests
import yaml
import os
import urllib.parse  # Untuk dekoding

# Daftar sumber langganan
SUB_LINKS = [
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/ermaozi01/free_clash_vpn/main/v2ray",
    "https://raw.githubusercontent.com/iwxf/free-v2ray/master/v2",
    "https://raw.githubusercontent.com/Leon406/SubCrawler/main/sub/share/v2ray.txt"
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
                    # Mengambil name dari bagian akhir URL setelah tanda '#' dan menghapus spasi
                    name = node.split('#')[1].strip() if '#' in node else 'default_name'
                    name = urllib.parse.unquote(name)  # Dekode nama yang di-encoded

                    # Ambil host dan sni
                    host = params.get('host', '')
                    sni = params.get('sni', '')

                    proxies.append({
                        "name": name,
                        "server": server,
                        "port": int(port),
                        "type": "trojan",
                        "password": credentials,
                        "skip-cert-verify": True,
                        "sni": urllib.parse.unquote(sni),  # Dekode SNI
                        "network": "ws",
                        "ws-opts": {
                            "path": params.get('path', ''),
                            "headers": {
                                "Host": urllib.parse.unquote(host)  # Dekode Host
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
