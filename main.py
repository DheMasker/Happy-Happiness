import base64
import requests
import yaml
import os
import json
import urllib.parse

# Daftar sumber langganan
SUB_LINKS = [ 
    "https://raw.githubusercontent.com/kSLAWIASCA/actions/refs/heads/main/Clash.yml",
"https://raw.githubusercontent.com/busymilk/clash_config_auto_build/main/config/config.yaml"
]

BUGCDN = "104.22.5.240"

def ambil_langganan():
    semua_node = []
    for url in SUB_LINKS:
        try:
            print(f"Mengambil langganan: {url}")
            res = requests.get(url, timeout=60)
            konten = res.text.strip()
            
            # Mencoba mendekode konten dan menangani karakter non-ASCII
            try:
                konten = konten.encode('utf-8').decode('utf-8', errors='ignore')
            except Exception as e:
                print(f"⚠️ Kesalahan saat mendekode konten: {e}")

            if not konten.startswith(("vmess://", "trojan://")):
                try:
                    konten = base64.b64decode(konten + '===').decode('utf-8', errors='ignore')
                except Exception as e:
                    print(f"⚠️ Kesalahan saat mendekode base64: {e}")
                    continue

            baris = [line.strip() for line in konten.splitlines() if line.strip()]
            semua_node.extend(baris)
        except Exception as e:
            print(f"❌ Kesalahan sumber langganan: {url} -> {e}")
    return semua_node

def saring_node(nodes):
    terfilter = []
    for node in nodes:
        if node.startswith("vmess://") or node.startswith("trojan://"):
            terfilter.append(node)
    return terfilter

def konversi_ke_clash(nodes):
    proxies = []
    for node in nodes:
        if node.startswith("vmess://"):
            try:
                vmess_config = base64.b64decode(node[8:] + '===').decode('utf-8', errors='ignore')
                config = json.loads(vmess_config.replace("false", "False").replace("true", "True"))
                proxies.append({
                    "name": config.get("ps", "Tanpa Nama"),
                    "server": BUGCDN,
                    "port": int(config["port"]),
                    "type": "vmess",
                    "uuid": config.get("id"),
                    "alterId": int(config.get("aid", 0)),
                    "cipher": "auto",
                    "tls": True,
                    "skip-cert-verify": True,
                    "servername": config.get("host", ""),
                    "network": config.get("net", "ws"),
                    "ws-opts": {
                        "path": config.get("path", "/vmess-ws"),
                        "headers": {
                            "Host": config.get("host", "")
                        }
                    },
                    "udp": True
                })
            except Exception as e:
                print(f"⚠️ Gagal memparsing vmess: {e}")

        elif node.startswith("trojan://"):
            try:
                raw = node[9:]  
                parts = raw.split('@')
                if len(parts) != 2:
                    continue
                credentials, server_info = parts
                server_details = server_info.split(':')
                if len(server_details) != 2:
                    continue
                port = int(server_details[1].split('?')[0])
                host = server_details[0]
                proxies.append({
                    "name": credentials.split('#')[1].strip() if '#' in credentials else 'default_name',
                    "server": BUGCDN,
                    "port": port,
                    "type": "trojan",
                    "password": urllib.parse.unquote(credentials.split('@')[0]),
                    "skip-cert-verify": True,
                    "sni": host,
                    "network": "ws",
                    "ws-opts": {
                        "path": "/linkws",  # Path default
                        "headers": {
                            "Host": host
                        }
                    },
                    "udp": True
                })
            except Exception as e:
                print(f"⚠️ Gagal memparsing trojan: {e}")

    return proxies

def main():
    nodes = ambil_langganan()
    filtered_nodes = saring_node(nodes)
    clash_proxies = konversi_ke_clash(filtered_nodes)

    os.makedirs("proxies", exist_ok=True)
    with open("proxies/vmess_trojan_proxies.yaml", "w", encoding="utf-8") as f:
        yaml.dump({"proxies": clash_proxies}, f, allow_unicode=True)

if __name__ == "__main__":
    main()
