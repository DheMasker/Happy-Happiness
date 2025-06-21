
import base64
import requests
import yaml
import os
import json

# Daftar sumber langganan
SUB_LINKS = [
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/ermaozi01/free_clash_vpn/main/v2ray",
    "https://raw.githubusercontent.com/iwxf/free-v2ray/master/v2",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/networks/ws",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/trojan",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vmess",
    "https://raw.githubusercontent.com/V2RayRoot/V2RayConfig/refs/heads/main/Config/vmess.txt",
    "https://raw.githubusercontent.com/Leon406/SubCrawler/main/sub/share/v2ray.txt"
]

# Contoh link yang menyimpan link lain
LINKS_SOURCE = [
    "https://raw.githubusercontent.com/devojony/collectSub/refs/heads/main/sub/sub_all_clash.txt"
]

# Contoh link konfigurasi Clash
CLASH_CONFIG_URLS = [
    "https://raw.githubusercontent.com/vxiaov/free_proxies/main/clash/clash.provider.yaml",
    "https://raw.githubusercontent.com/busymilk/clash_config_auto_build/main/config/config.yaml"
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
            print(f"❌ Kesalahan sumber langganan: {url} -> {e}")
    return semua_node

def ambil_sub_links(url):
    sub_links = []
    try:
        print(f"Mengambil sub-link dari: {url}")
        res = requests.get(url, timeout=10)
        sub_links = [line.strip() for line in res.text.splitlines() if line.strip()]
    except Exception as e:
        print(f"❌ Kesalahan mengambil sub-link: {url} -> {e}")
    return sub_links

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
            raw = node[8:]
            decoded = base64.b64decode(raw + '===').decode('utf-8', errors='ignore')
            return json.loads(decoded.replace("false", "False").replace("true", "True"))
    except Exception as e:
        print(f"⚠️ Gagal mendecode node: {e}")
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
                print(f"⚠️ Gagal memparsing vmess: {e}")

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
                print(f"⚠️ Gagal memparsing trojan: {e}")

    config_clash = {
        "proxies": proxies,
        "proxy-groups": [{
            "name": "🔰 Pilihan Node",
            "type": "select",
            "proxies": [p["name"] for p in proxies]
        }],
        "rules": ["MATCH,🔰 Pilihan Node"]
    }
    return yaml.dump(config_clash, allow_unicode=True, sort_keys=False)

def ambil_config_clash(url):
    try:
        print(f"Mengambil konfigurasi Clash dari: {url}")
        res = requests.get(url, timeout=10)
        return res.text.strip()
    except Exception as e:
        print(f"❌ Kesalahan mengambil konfigurasi Clash: {url} -> {e}")
        return None

def main():
    nodes = ambil_langganan()
    filtered_nodes = saring_node(nodes)

    # Mengambil sub-link dari sumber yang ditentukan
    for url in LINKS_SOURCE:
        sub_links = ambil_sub_links(url)
        for sub_link in sub_links:
            # Mengambil langganan dari setiap sub-link
            nodes.extend(ambil_langganan(sub_link))

    # Mengambil konfigurasi Clash dari link
    for url in CLASH_CONFIG_URLS:
        config = ambil_config_clash(url)
        if config:
            print("Konfigurasi Clash berhasil diambil.")

    os.makedirs("docs", exist_ok=True)
    with open("docs/clash.yaml", "w", encoding="utf-8") as f:
        f.write(konversi_ke_clash(filtered_nodes))
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write("<h2>Langganan Clash Telah Dihasilkan</h2><ul><li><a href='clash.yaml'>clash.yaml</a></li></ul>")

if __name__ == "__main__":
    main()
