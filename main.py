
import base64
import requests
import yaml
import os

BUGCDN = "104.22.5.240"

# Daftar sumber langganan (bisa ditambahkan lebih banyak)
SUB_LINKS = [
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/networks/ws",
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
            res = requests.get(url, timeout=10)
            konten = res.text.strip()
            if not konten.startswith("vmess") and not konten.startswith("trojan"):
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
        if info:  # Pastikan info bukan None
            if node.startswith("vmess://"):
                if (info.get("net") == "ws" and 
                    (info.get("port") == 443 or info.get("port") == 80)):
                    terfilter.append(node)
            elif node.startswith("trojan://"):
                terfilter.append(node)  # Menambahkan node Trojan tanpa filter
    return terfilter  # Tidak ada batasan pada jumlah node

def decode_node_info_base64(node):
    try:
        if node.startswith("vmess://"):
            raw = node[8:]
            decoded = base64.b64decode(raw + '===').decode('utf-8', errors='ignore')
            return eval(decoded.replace("false", "False").replace("true", "True"))
        elif node.startswith("trojan://"):
            raw = node[8:]
            # Mengurai informasi Trojan, bisa disesuaikan
            decoded = base64.b64decode(raw + '===').decode('utf-8', errors='ignore')
            return {
                "password": decoded.split('#')[0],  # Ambil password
                "name": decoded.split('#')[1] if '#' in decoded else "Tanpa Nama"  # Ambil nama jika ada
            }
    except Exception as e:
        print(f"⚠️ Gagal mendecode node: {e}")
        return None  # Kembalikan None jika terjadi kesalahan

def konversi_ke_clash(nodes):
    proxies = []
    for node in nodes:
        if node.startswith("vmess://"):
            try:
                vmess_config = base64.b64decode(node[8:] + '===').decode('utf-8', errors='ignore')
                config = eval(vmess_config.replace("false", "False").replace("true", "True"))
                proxies.append({
                    "alterId": int(config.get("aid", 0)),
                    "type": "vmess",
                    "server": BUGCDN,  # Ubah server menjadi BUGCDN
                    "port": int(config["port"]),
                    "uuid": config["id"],
                    "name": config.get("ps", "Tanpa Nama"),                    
                    "cipher": "auto",
                    "tls": "true" if config.get("tls") else "",  # Memperbaiki akses ke 'tls'
                    "network": config.get("net", "ws"),
                    "ws-opts": {
                        "path": config.get("path", ""),
                        "headers": {"Host": config.get("host", "")},
                    "udp": config.get("net", "true"),
                    } if config.get("net") == "ws" else {}
                })
            except Exception as e:
                print(f"⚠️ Gagal memparsing vmess: {e}")
        elif node.startswith("trojan://"):
            try:
                trojan_config = base64.b64decode(node[8:] + '===').decode('utf-8', errors='ignore')
                password = trojan_config.split('#')[0]  # Ambil password
                name = trojan_config.split('#')[1] if '#' in trojan_config else "Tanpa Nama"  # Ambil nama
                proxies.append({
                    "type": "trojan",
                    "server": BUGCDN,  # Ubah server menjadi BUGCDN
                    "port": int(config["port"]),  # Mengakses port dari config yang benar
                    "password": password,
                    "name": name,                    
                    "cipher": "auto",
                    "skip-cert-verify": "true",  # Memperbaiki kunci
                    "sni": config.get("sni", ""),
                    "network": config.get("net", "ws"),
                    "ws-opts": {
                        "path": config.get("path", ""),
                        "headers": {"Host": config.get("host", "")},
                    "udp": config.get("net", "true"),
                    } if config.get("net") == "ws" else {}
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
    return yaml.dump(config_clash, allow_unicode=True)

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
