import base64
import requests
import yaml
import os
import json
import urllib.parse

# Daftar sumber langganan
SUB_LINKS = [
    "https://raw.githubusercontent.com/sevcator/5ubscrpt10n/refs/heads/main/full/5ubscrpt10n-b64.txt"
]

# Contoh Trojan node
EXAMPLE_TROJAN_NODE = "trojan://936c6853-6bbf-4e24-8667-ec5b2fc275b3@104.26.15.85:443/?type=ws&host=md1.safecdn.site&path=%2FChannel_vpnAndroid2-Channel_vpnAndroid2-Channel_vpnAndroid2-Channel_vpnAndroid2&security=tls&sni=md1.safecdn.site#%F0%9F%94%92%20TR-WS-TLS%20%F0%9F%8F%B4%E2%80%8D%E2%98%A0%EF%B8%8F%20NA-104.26.15.85%3A443"

def ambil_langganan():
    semua_node = []
    # Menambahkan contoh Trojan node
    semua_node.append(EXAMPLE_TROJAN_NODE)
    
    for url in SUB_LINKS:
        try:
            print(f"Mengambil langganan: {url}")
            res = requests.get(url, timeout=60)
            konten = res.text.strip()
            if not konten.startswith("trojan"):
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
                # Menggunakan node[9:] untuk mengabaikan prefix "trojan://"
                trojan_config = base64.b64decode(node[9:] + '===').decode('utf-8', errors='ignore')
                config = json.loads(trojan_config.replace("false", "False").replace("true", "True"))

                # Mengambil nama dari parameter ps atau dari bagian setelah #
                name = config.get("ps", "Tanpa Nama")
                if "ps" not in config:
                    name = urllib.parse.unquote(node.split("#")[-1])  # Dekode nama

                proxies.append({
                    "name": name,
                    "server": config["server"],
                    "port": int(config["port"]),
                    "type": "trojan",
                    "password": config["id"],
                    "cipher": "auto",
                    "tls": True,
                    "skip-cert-verify": True,
                    "sni": config.get("host", ""),
                    "network": config.get("type", "ws"),
                    "ws-opts": {
                        "path": config.get("path", ""),
                        "headers": {"Host": config.get("host", "")}
                    }
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
