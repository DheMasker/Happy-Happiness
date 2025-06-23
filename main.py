import base64
import requests
import yaml
import os
import json
import subprocess
import time

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
            if not konten.startswith("vmess"):
                konten = base64.b64decode(konten + '===').decode('utf-8', errors='ignore')
            baris = [line.strip() for line in konten.splitlines() if line.strip()]
            semua_node.extend(baris)
        except Exception as e:
            print(f"❌ Kesalahan sumber langganan: {url} -> {e}")
    return semua_node

def saring_node(nodes):
    terfilter = []
    for node in nodes:
        info = decode_node_info_base64(node)
        if info is not None:
            if (node.startswith("vmess://") and info.get("port") in {443, 80} and info.get("net") == "ws"):
                terfilter.append(node)
    return terfilter

def decode_node_info_base64(node):
    try:
        if node.startswith("vmess://"):
            raw = node[8:]
            decoded = base64.b64decode(raw + '===').decode('utf-8', errors='ignore')
            return json.loads(decoded.replace("false", "False").replace("true", "True"))
    except Exception as e:
        print(f"⚠️ Gagal mendecode node: {e}")
        return None

def check_node_status(node):
    config = decode_node_info_base64(node)
    if config is None:
        return False

    create_v2ray_config(config)

    # Jalankan V2Ray
    process = subprocess.Popen(["v2ray", "-config", "config.json"])
    time.sleep(5)  # Tunggu beberapa detik untuk memastikan V2Ray terhubung

    # Menguji koneksi (misalnya menggunakan curl)
    response = os.system("curl -s -o /dev/null -w '%{http_code}' http://example.com")  # Ubah URL sesuai kebutuhan

    process.terminate()  # Hentikan V2Ray
    
    return response == 200

def create_v2ray_config(config):
    v2ray_config = {
        "outbounds": [{
            "protocol": "vmess",
            "settings": {
                "vnext": [{
                    "address": config["address"],
                    "port": config["port"],
                    "users": [{
                        "id": config["id"],
                        "alterId": config.get("aid", 0)
                    }]
                }]
            }
        }]
    }
    
    with open("config.json", "w") as f:
        json.dump(v2ray_config, f)

def konversi_ke_clash(nodes):
    proxies = []

    for node in nodes:
        if node.startswith("vmess://"):
            if check_node_status(node):  # Periksa status node
                try:
                    config = decode_node_info_base64(node)
                    name = f"{config.get('ps', 'Tanpa Nama')}"
                    proxies.append({
                        "name": name,
                        "server": config["address"],
                        "port": int(config["port"]),
                        "type": "vmess",
                        "uuid": config["id"],
                        "alterId": int(config.get("aid", 0)),
                        "cipher": "auto",
                        "tls": True,
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

def main():
    nodes = ambil_langganan()
    filtered_nodes = saring_node(nodes)
    os.makedirs("proxies", exist_ok=True)
    output_file = "proxies/vmesswscdn443and80base64.yaml"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(konversi_ke_clash(filtered_nodes))
    print(f"File berhasil disimpan di {output_file}")

if __name__ == "__main__":
    main()
