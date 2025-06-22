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
            if not konten.startswith("vmess"):
                konten = base64.b64decode(konten).decode('utf-8', errors='ignore')
            baris = [line.strip() for line in konten.splitlines() if line.strip()]
            semua_node.extend(baris)
        except Exception as e:
            print(f"❌ Kesalahan sumber langganan: {url} -> {e}")
    return semua_node

def decode_node_info_base64(node):
    try:
        if node.startswith("vmess://"):
            raw = node[8:]
            decoded = base64.b64decode(raw).decode('utf-8', errors='ignore')
            return json.loads(decoded.replace("false", "False").replace("true", "True"))
        elif node.startswith("trojan://"):
            return None  # Tidak mendekode Trojan di sini
    except Exception as e:
        print(f"⚠️ Gagal mendecode node: {e}")
        return None

def saring_node(nodes):
    terfilter = []
    for node in nodes:
        info = decode_node_info_base64(node)
        if info is not None and node.startswith("vmess://"):
            if info.get("port") in {443, 80} and info.get("net") == "ws":
                terfilter.append(node)
    return terfilter

def saring_trojan(nodes):
    terfilter = []
    for node in nodes:
        if node.startswith("trojan://"):
            terfilter.append(node)
    return terfilter

def konversi_ke_clash(nodes):
    proxies = []

    for node in nodes:
        if node.startswith("vmess://"):
            try:
                vmess_config = base64.b64decode(node[8:]).decode('utf-8', errors='ignore')
                config = json.loads(vmess_config.replace("false", "False").replace("true", "True"))
                
                proxies.append({
                    "name": config.get("ps", "Tanpa Nama"),
                    "server": config["add"],
                    "port": int(config["port"]),
                    "type": "vmess",
                    "uuid": config["id"],
                    "alterId": int(config.get("aid", 0)),
                    "cipher": "auto",
                    "tls": config.get("tls", False) == "tls",
                    "skip-cert-verify": True,
                    "servername": config.get("host", ""),
                    "network": config.get("net", "ws"),
                    "ws-opts": {
                        "path": config.get("path", "/vmess-ws"),
                        "headers": {"Host": config.get("host", "")}
                    },
                    "udp": True
                })
            except Exception as e:
                print(f"⚠️ Gagal memparsing vmess: {e}")

    proxies_clash = {
        "proxies": proxies
    }
    return yaml.dump(proxies_clash, allow_unicode=True, sort_keys=False)

def konversi_ke_clash_trojan(nodes):
    proxies = []

    for node in nodes:
        if node.startswith("trojan://"):
            try:
                trojan_parts = node[9:].split("@")
                trojan_info = trojan_parts[0].split(":")
                trojan_address = trojan_info[0]
                trojan_port = int(trojan_info[1])
                trojan_password = trojan_parts[1].split("#")[0]
                trojan_name = trojan_parts[1].split("#")[1]  # Nama dari bagian setelah '#'

                # Menambahkan informasi tambahan dari query string
                query_params = dict(q.split('=') for q in trojan_parts[0].split('?')[1].split('&')) if '?' in trojan_parts[0] else {}
                path = query_params.get('path', '/trojan-ws')  # Nilai default untuk path
                network = "ws"  # Mengatur jenis jaringan sesuai kebutuhan
                host = query_params.get('host', trojan_address)  # Mengambil host dari query atau menggunakan alamat server

                proxies.append({
                    "name": trojan_name,
                    "server": trojan_address,
                    "port": trojan_port,
                    "type": "trojan",
                    "password": trojan_password,
                    "skip-cert-verify": True,
                    "sni": host,  # Menggunakan host sebagai SNI
                    "network": network,
                    "ws-opts": {
                        "path": path,
                        "headers": {"Host": host}  # Menggunakan host di dalam header
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
    filtered_trojan_nodes = saring_trojan(nodes)
    os.makedirs("proxies", exist_ok=True)
    
    # Menyimpan konfigurasi VMess
    with open(os.path.join("proxies", "vmesswscdn443and80.yaml"), "w", encoding="utf-8") as f:
        f.write(konversi_ke_clash(filtered_nodes))
    
    # Menyimpan konfigurasi Trojan
    with open(os.path.join("proxies", "trojancdn.yaml"), "w", encoding="utf-8") as f:
        f.write(konversi_ke_clash_trojan(filtered_trojan_nodes))

if __name__ == "__main__":
    main()
