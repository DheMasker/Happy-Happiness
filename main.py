import base64
import requests
import yaml
import os
import json
import string

# Daftar sumber langganan
SUB_LINKS = [ 
    "https://raw.githubusercontent.com/roosterkid/openproxylist/refs/heads/main/V2RAY_RAW.txt",
    "https://raw.githubusercontent.com/PlanAsli/configs-collector-v2ray/refs/heads/main/sub/all_configs.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/MhdiTaheri/V2rayCollector/refs/heads/main/sub/mix"
]

BUGCDN = "104.22.5.240"

def ambil_langganan():
    semua_node = []
    for url in SUB_LINKS:
        try:
            print(f"Mengambil langganan: {url}")
            res = requests.get(url, timeout=60)
            konten = res.text.strip()
            print(f"Konten yang diambil dari {url}: {konten[:100]}...")  # Mencetak sebagian konten
            
            # Memproses konten berdasarkan formatnya
            baris = konten.splitlines()
            semua_node.extend(baris)
        except Exception as e:
            print(f"❌ Kesalahan sumber langganan: {url} -> {e}")
    return semua_node

def decode_base64(konten):
    try:
        konten = ''.join(filter(lambda x: x in string.printable, konten))
        while len(konten) % 4 != 0:
            konten += '='
        decoded = base64.b64decode(konten).decode('utf-8', errors='ignore')
        return [line.strip() for line in decoded.splitlines() if line.strip()]
    except Exception as e:
        print(f"⚠️ Gagal mendekode Base64: {e}. Menggunakan konten langsung.")
        return [line.strip() for line in konten.splitlines() if line.strip()]

def saring_node(nodes):
    terfilter = []
    for node in nodes:
        info = decode_node_info(node)
        if info is not None:
            # Memfilter node berdasarkan kriteria yang diinginkan
            if (info.get("port") in {443, 80} and info.get("net") == "ws"):
                terfilter.append(node)
    print(f"Jumlah node setelah disaring: {len(terfilter)}")  # Mencetak jumlah node setelah penyaringan
    return terfilter

def decode_node_info(node):
    try:
        if node.startswith("vmess://"):
            raw = node.split("://")[1]
            while len(raw) % 4 != 0:
                raw += '='
            decoded = base64.b64decode(raw).decode('utf-8', errors='ignore')
            return json.loads(decoded.replace("false", "False").replace("true", "True"))
        elif node.startswith("trojan://"):
            return parse_trojan(node)
    except Exception as e:
        print(f"⚠️ Gagal mendecode node: {e}")
        return None

def parse_trojan(node):
    try:
        print("🔍 Memproses node Trojan...")
        # Memisahkan bagian node
        parts = node.split("://")[1].split("@")
        auth = parts[0]  # Mendapatkan autentikasi
        server_info = parts[1].split(":")  # Memisahkan server dan port
        
        # Mengambil query params
        query_params = parts[1].split("/")[1] if len(parts[1].split("/")) > 1 else ""
        params = dict(param.split("=") for param in query_params.split("&") if "=" in param)
        
        # Mengambil nilai dari query params
        sni = params.get("sni", "")
        path = params.get("path", "")
        host = params.get("host", "")
        security = params.get("security", "")
        allow_insecure = params.get("allowInsecure", "0")  # Default ke 0 jika tidak ada
        
        # Menetapkan jenis jaringan dari query params
        network_type = params.get("type", "ws")  # Mengambil dari query params, default ke "ws"

        # Mengembalikan informasi dalam bentuk dictionary
        result = {
            "type": "trojan",
            "password": auth,
            "server": server_info[0],
            "port": int(server_info[1]),
            "sni": sni,
            "network": network_type,
            "skip-cert-verify": True,
            "ws-opts": {
                "path": path,
                "headers": {
                    "Host": host
                }
            },
            "udp": True
        }
        
        print("✅ Node Trojan berhasil diparse:", result)
        return result
    except Exception as e:
        print(f"⚠️ Gagal memparse Trojan node: {e}")
        return None

def konversi_ke_clash(nodes):
    proxies = []

    for node in nodes:
        if node.startswith("vmess://"):
            try:
                vmess_config = base64.b64decode(node.split("://")[1] + '===').decode('utf-8', errors='ignore')
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
                info = parse_trojan(node)
                proxies.append({
                    "name": f"{info['sni']}-trojan_ws_cdn_turbovidio",  # Format nama yang diinginkan
                    "server": info["server"],
                    "port": info["port"],
                    "type": "trojan",
                    "password": info["password"],
                    "skip-cert-verify": info.get("skip-cert-verify"),
                    "sni": info["sni"],
                    "network": info["network"],
                    "ws-opts": info["ws-opts"],
                    "udp": info["udp"]
                })
            except Exception as e:
                print(f"⚠️ Gagal memparsing trojan: {e}")

    proxies_clash = {
        "proxies": proxies
    }
    return yaml.dump(proxies_clash, allow_unicode=True, sort_keys=False)

def main():
    nodes = ambil_langganan()
    print(f"Total node yang berhasil diambil: {len(nodes)}")  # Mencetak total node
    filtered_nodes = saring_node(nodes)
    print(f"Total node setelah disaring: {len(filtered_nodes)}")  # Mencetak total node setelah penyaringan
    os.makedirs("proxies", exist_ok=True)
    with open("proxies/vmesswscdn443and80.yaml", "w", encoding="utf-8") as f:
        f.write(konversi_ke_clash(filtered_nodes))

if __name__ == "__main__":
    main()
