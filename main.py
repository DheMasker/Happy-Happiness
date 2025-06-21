import base64
import requests
import yaml
import os
import json
import re

# Daftar sumber langganan
SUB_LINKS = [ 
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/networks/ws",
    "https://raw.githubusercontent.com/V2RayRoot/V2RayConfig/refs/heads/main/Config/vmess.txt"
]

BUGCDN = "104.22.5.240"

def ambil_langganan():
    semua_node = []
    for url in SUB_LINKS:
        try:
            print(f"Mengambil langganan: {url}")
            res = requests.get(url, timeout=10)
            konten = res.text.strip()
            if not konten.startswith("vmess") and not konten.startswith("trojan"):
                konten = base64.b64decode(konten + '===').decode('utf-8', errors='ignore')
            baris = [line.strip() for line in konten.splitlines() if line.strip()]
            semua_node.extend(baris)
        except Exception as e:
            print(f"тЭМ Kesalahan sumber langganan: {url} -> {e}")
    return semua_node

def saring_node(nodes):
    terfilter = []
    for node in nodes:
        info = decode_node_info_base64(node)
        if info is not None:
            if (node.startswith("vmess://") or node.startswith("trojan://")) and info.get("port") in {443, 80} and info.get("net") == "ws":
                terfilter.append(node)
    return terfilter

def decode_node_info_base64(node):
    try:
        if node.startswith("vmess://") or node.startswith("trojan://"):
            # Memisahkan bagian yang valid untuk dekode
            raw = node[8:].split('#')[0]  # Ambil hanya bagian sebelum '#'
            # Pisahkan bagian yang valid sebelum dan setelah '@'
            parts = raw.split('@')
            if len(parts) < 2:
                print(f"тЪая╕П Gagal memisahkan bagian dari node: {node}")
                return None
            
            # Ambil bagian sebelum '@' dan tambahkan bagian setelah '@' yang relevan
            base64_part = parts[0] + '@' + parts[1].split('?')[0]  # Ambil hanya bagian sebelum query string

            # Validasi format Base64
            if not re.match(r'^[A-Za-z0-9+/=]*$', base64_part):
                print(f"тЪая╕П Karakter tidak valid ditemukan dalam Base64: {base64_part}")
                return None
            
            # Tambahkan padding jika perlu
            padding = len(base64_part) % 4
            if padding:
                base64_part += '=' * (4 - padding)

            # Dekode string
            decoded = base64.b64decode(base64_part, validate=True).decode('utf-8', errors='ignore')
            return json.loads(decoded.replace("false", "False").replace("true", "True"))
    except json.JSONDecodeError as json_err:
        print(f"тЪая╕П Gagal memparsing JSON dari node: {node} -> {json_err}")
    except Exception as e:
        print(f"тЪая╕П Gagal mendecode node: {e}")
    return None

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
                print(f"тЪая╕П Gagal memparsing vmess: {e}")

        elif node.startswith("trojan://"):
            try:
                trojan_config = base64.b64decode(node[8:] + '===').decode('utf-8', errors='ignore')
                config = json.loads(trojan_config.replace("false", "False").replace("true", "True"))
                proxies.append({
                    "name": config.get("ps", "Tanpa Nama"),
                    "server": BUGCDN,
                    "port": config["port"],
                    "type": "trojan",
                    "password": config["password"],
                    "skip-cert-verify": True,
                    "sni": config.get("host", ""),
                    "network": config.get("net", "ws"),
                    "ws-opts": {
                        "path": config.get("path", "/trojan-ws"),
                        "headers": {"Host": config.get("host", "")}
                    },
                    "udp": True
                })
            except Exception as e:
                print(f"тЪая╕П Gagal memparsing trojan: {e}")

    config_clash = {
        "proxies": proxies,
        "proxy-groups": [{
            "name": "ЁЯФ░ Pilihan Node",
            "type": "select",
            "proxies": [p["name"] for p in proxies]
        }],
        "rules": ["MATCH,ЁЯФ░ Pilihan Node"]
    }
    return yaml.dump(config_clash, allow_unicode=True, sort_keys=False)

def main():
    nodes = ambil_langganan()
    filtered_nodes = saring_node(nodes)
    os.makedirs("docs", exist_ok=True)
    with open("docs/clash.yaml", "w", encoding="utf-8") as f:
        f.write(konversi_ke_clash(filtered_nodes))
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write("<h2>Langganan Clash Telah Dihasilkan</h2><ul><li><a href='clash.yaml'>clash.yaml</a></li></ul>")

if __name__ == "__main__":
    main()
