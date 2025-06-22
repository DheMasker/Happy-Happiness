import base64
import requests
import json

# Daftar sumber langganan
SUB_LINKS = [
    "https://raw.githubusercontent.com/roosterkid/openproxylist/refs/heads/main/V2RAY_RAW.txt",
    "https://raw.githubusercontent.com/PlanAsli/configs-collector-v2ray/refs/heads/main/sub/all_configs.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/MhdiTaheri/V2rayCollector/refs/heads/main/sub/mix"
]

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def ambil_langganan():
    semua_node = []
    for url in SUB_LINKS:
        try:
            print(f"Mengambil langganan dari: {url}")
            res = requests.get(url, timeout=60)
            konten = res.text.strip()
            baris = [line.strip() for line in konten.splitlines() if line.strip()]

            for node in baris:
                if node.startswith("vmess://"):
                    try:
                        # Decode base64
                        decoded = base64.b64decode(node[8:] + '===').decode('utf-8', errors='ignore')
                        # Validasi karakter ASCII
                        if is_ascii(decoded):
                            semua_node.append(node)
                        else:
                            print(f"⚠️ Konten tidak hanya mengandung karakter ASCII: {node}")
                    except Exception as e:
                        print(f"⚠️ Gagal mendecode node: {e}")
        except Exception as e:
            print(f"❌ Kesalahan sumber langganan: {url} -> {e}")

    return semua_node

def main():
    nodes = ambil_langganan()
    print(f"Total node valid yang ditemukan: {len(nodes)}")
    for node in nodes:
        print(node)  # Menampilkan node yang valid

if __name__ == "__main__":
    main()
