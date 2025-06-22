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

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def ambil_langganan():
    semua_node = []
    for url in SUB_LINKS:
        try:
            print(f"Mengambil langganan: {url}")
            res = requests.get(url, timeout=60)
            konten = res.text.strip()
            if not konten.startswith("vmess"):
                konten = base64.b64decode(konten + '===').decode('utf-8')
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
            if not is_ascii(raw):
                print(f"⚠️ Karakter non-ASCII ditemukan dalam node: {node}")
                return None  # Lewati node ini jika ada karakter non-ASCII
            
            decoded = base64.b64decode(raw + '===').decode('utf-8')
            return json.loads(decoded.replace("false", "False").replace("true", "True"))
    except json.JSONDecodeError as e:
        print(f"⚠️ Gagal mendecode JSON: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Gagal mendecode node: {e}")
        return None

def konversi_ke_clash(nodes):
    proxies = []
    for node in nodes:
        if node.startswith("vmess://"):
            try:
                vmess_config = base64.b64decode(node[8:] + '===').decode('utf-8')
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
                print(f"⚠️ Gagal memparsing vmess: {e}")

    proxies_clash = {
        "proxies": proxies
    }
    return yaml.dump(proxies_clash, allow_unicode=True, sort_keys=False)

def main():
    nodes = ambil_langganan()
    filtered_nodes = saring_node(nodes)
    os.makedirs("proxies", exist_ok=True)
    with open("proxies/vmesswscdn443and80.yaml", "w", encoding="utf-8") as f:
        f.write(konversi_ke_clash(filtered_nodes))

if __name__ == "__main__":
    main()
