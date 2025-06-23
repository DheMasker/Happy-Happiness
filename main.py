import base64
import requests
import yaml
import os
import json
import speedtest

# Daftar sumber langganan
SUB_LINKS = [ 
   

"https://raw.githubusercontent.com/Surfboardv2ray/Proxy-sorter/refs/heads/main/submerge/converted.txt",
"https://raw.githubusercontent.com/Surfboardv2ray/TGParse/refs/heads/main/splitted/vmess",
"https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/refs/heads/main/subscriptions/base64/all_sub.txt",
"https://raw.githubusercontent.com/lagzian/SS-Collector/refs/heads/main/vmess_B64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub1_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub2_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub3_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub4_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub5_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub6_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub7_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub8_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub9_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub10_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub11_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub12_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub13_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub14_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub15_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub16_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub17_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub18_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub19_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub20_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub21_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub22_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub23_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub24_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub25_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub26_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub27_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub28_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub29_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub30_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub31_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub32_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub33_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub34_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub35_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub36_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub37_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub38_base64.txt",
"https://raw.githubusercontent.com/Pawdroid/Free-servers/refs/heads/main/sub",
"https://raw.githubusercontent.com/roosterkid/openproxylist/refs/heads/main/V2RAY_BASE64.txt",
"https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vmess",
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

def lakukan_speedtest(node):
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000  # Mengonversi ke Mbps
        upload_speed = st.upload() / 1_000_000  # Mengonversi ke Mbps
        return download_speed, upload_speed
    except Exception as e:
        print(f"⚠️ Gagal melakukan speed test untuk node {node}: {e}")
        return None, None

def konversi_ke_clash(nodes):
    proxies = []

    for node in nodes:
        if node.startswith("vmess://"):
            download_speed, upload_speed = lakukan_speedtest(node)  # Menjalankan speedtest untuk setiap node
            if download_speed is not None and upload_speed is not None:  # Hanya jika speed test berhasil
                try:
                    vmess_config = base64.b64decode(node[8:] + '===').decode('utf-8', errors='ignore')
                    config = json.loads(vmess_config.replace("false", "False").replace("true", "True"))
                    # Menggunakan hasil speed test untuk nama
                    name = f"{config.get('ps', 'Tanpa Nama')} - DL: {download_speed:.2f} Mbps, UL: {upload_speed:.2f} Mbps"
                    proxies.append({
                        "name": name,
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
    with open("proxies/vmesswscdn443and80base64.yaml", "w", encoding="utf-8") as f:
        f.write(konversi_ke_clash(filtered_nodes))

if __name__ == "__main__":
    main()
