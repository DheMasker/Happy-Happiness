import base64
import requests
import re

# Daftar sumber langganan
SUB_LINKS = [
    "https://raw.githubusercontent.com/roosterkid/openproxylist/refs/heads/main/V2RAY_RAW.txt",
    "https://raw.githubusercontent.com/PlanAsli/configs-collector-v2ray/refs/heads/main/sub/all_configs.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/MhdiTaheri/V2rayCollector/refs/heads/main/sub/mix"
]

def clean_non_ascii(s):
    """Menghapus karakter non-ASCII dari string."""
    return re.sub(r'[^\x00-\x7F]+', '', s)

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
                        base64_string = node[8:]  # Menghapus "vmess://"
                        # Menambahkan padding jika perlu
                        while len(base64_string) % 4 != 0:
                            base64_string += '='

                        # Decode base64
                        decoded = base64.b64decode(base64_string, validate=True).decode('utf-8', errors='ignore')
                        # Bersihkan karakter non-ASCII
                        cleaned = clean_non_ascii(decoded)
                        if cleaned:  # Pastikan ada konten setelah dibersihkan
                            semua_node.append(node)
                        else:
                            print(f"⚠️ Node dibersihkan tidak memiliki konten valid: {node}")
                    except (base64.binascii.Error, UnicodeDecodeError) as e:
                        print(f"⚠️ Gagal mendecode node: {node} -> {e}")
                    except Exception as e:
                        print(f"⚠️ Kesalahan tidak terduga saat memproses node: {node} -> {e}")
        except requests.RequestException as e:
            print(f"❌ Kesalahan sumber langganan: {url} -> {e}")

    return semua_node

def main():
    nodes = ambil_langganan()
    print(f"Total node valid yang ditemukan: {len(nodes)}")
    for node in nodes:
        print(node)  # Menampilkan node yang valid

if __name__ == "__main__":
    main()
