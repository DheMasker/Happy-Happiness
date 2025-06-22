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
            
            # Memproses konten berdasarkan formatnya
            if konten.startswith("vmess"):
                baris = [konten]
            else:
                baris = decode_base64(konten)
            
            semua_node.extend(baris)
        except Exception as e:
            print(f"❌ Kesalahan sumber langganan: {url} -> {e}")
    return semua_node

def decode_base64(konten):
    try:
        # Hapus karakter yang tidak valid
        konten = ''.join(filter(lambda x: x in string.printable, konten))
        
        # Menambahkan padding '=' jika diperlukan
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
            # Mengizinkan semua node dengan port 443 atau 80 dan network ws
            if (info.get("port") in {443, 80} and info.get("net") == "ws"):
                terfilter.append(node)
    return terfilter

def decode_node_info(node):
    try:
        if node.startswith("vmess://"):
            raw = node[8:]
            # Menambahkan padding '=' jika diperlukan
            while len(raw) % 4 != 0:
                raw += '='
            decoded = base64.b64decode(raw).decode('utf-8', errors='ignore')
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
