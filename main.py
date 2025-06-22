import base64
import requests
import yaml
import os
import urllib.parse
import time
from concurrent.futures import ThreadPoolExecutor

# Daftar sumber langganan
SUB_LINKS = [
    "https://raw.githubusercontent.com/sevcator/5ubscrpt10n/refs/heads/main/full/5ubscrpt10n-b64.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/ermaozi01/free_clash_vpn/main/v2ray",
    "https://raw.githubusercontent.com/iwxf/free-v2ray/master/v2",
    "https://raw.githubusercontent.com/Leon406/SubCrawler/main/sub/share/v2ray.txt",
    "https://raw.githubusercontent.com/Surfboardv2ray/v2ray-worker-sub/refs/heads/master/providers/providers64"
]

# URL untuk pengujian koneksi
TEST_URL = "http://www.gstatic.com/generate_204"

# Alamat server yang akan digunakan
BUGCDN = "104.22.5.240"

def ambil_langganan():
    semua_node = []
    for url in SUB_LINKS:
        try:
            print(f"Mengambil langganan: {url}")
            res = requests.get(url, timeout=60)
            konten = res.text.strip()
            if konten:
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

def uji_latency(proxy):
    try:
        # Membangun konfigurasi proxy
        proxy_config = {
            "http": f"http://{proxy['server']}:{proxy['port']}",
            "https": f"http://{proxy['server']}:{proxy['port']}"
        }
        # Mengukur waktu respons
        start_time = time.time()
        response = requests.get(TEST_URL, proxies=proxy_config, timeout=5)
        latency = time.time() - start_time
        return latency if response.status_code == 204 else None
    except Exception as e:
        print(f"⚠️ Gagal menguji latency untuk proxy {proxy['server']}:{proxy['port']}: {e}")
        return None

def konversi_ke_clash(nodes):
    proxies = []

    for node in nodes:
        if node.startswith("trojan://"):
            try:
                raw = node[10:]  # Menghapus 'trojan://'
                parts = raw.split('@')
                if len(parts) != 2:
                    print("⚠️ Format node Trojan tidak valid")
                    continue

                credentials, server_info = parts
                server_details = server_info.split(':')
                if len(server_details) != 2:
                    print("⚠️ Format server info tidak valid")
                    continue

                # Ganti server dengan BUGCDN
                server = BUGCDN
                port = server_details[1].split('?')[0]  # Ambil port dari server_info
                query = server_details[1].split('?')[1] if '?' in server_details[1] else ''
                params = {param.split('=')[0]: param.split('=')[1] for param in query.split('&') if '=' in param}

                # Hanya memproses jika tipe adalah ws dan port 443 atau 80
                if params.get('type') == 'ws' and port in ['443', '80']:
                    # Mengambil dan mendekode name
                    name = node.split('#')[1].strip() if '#' in node else 'default_name'
                    name = urllib.parse.unquote(name)  # Dekode nama

                    # Ambil host dan hapus bagian setelah '#'
                    host = params.get('host', '')
                    if '#' in host:
                        host = host.split('#')[0]  # Hapus bagian setelah '#'
                    host = urllib.parse.unquote(host)  # Dekode host

                    # Ambil sni dan hapus bagian setelah '#'
                    sni = params.get('sni', '')
                    if '#' in sni:
                        sni = sni.split('#')[0]  # Hapus bagian setelah '#'
                    sni = urllib.parse.unquote(sni)  # Dekode SNI

                    # Ambil path dan mendekode, pastikan tidak ada karakter '#' setelahnya
                    path = urllib.parse.unquote(params.get('path', ''))
                    if '#' in path:
                        path = path.split('#')[0]  # Hapus bagian setelah '#'
                    path = path.replace('%2F', '/')  # Ganti '%2F' dengan '/'

                    # Pastikan tidak ada karakter '#' di akhir path
                    if path.endswith('#'):
                        path = path[:-1]

                    # Tambahkan proxy ke daftar
                    proxies.append({
                        "name": name,
                        "server": server,  # Gunakan server yang telah ditentukan
                        "port": int(port),
                        "type": "trojan",
                        "password": urllib.parse.unquote(credentials),  # Dekode password
                        "skip-cert-verify": True,
                        "sni": sni,  # Set SNI yang telah dibersihkan
                        "network": "ws",
                        "ws-opts": {
                            "path": path,  # Path yang sudah dibersihkan
                            "headers": {
                                "Host": host  # Set Host yang telah dibersihkan
                            }
                        },
                        "udp": True
                    })
            except Exception as e:
                print(f"⚠️ Gagal memparsing trojan: {e}")

    proxies_clash = {
        "proxies": proxies
    }
    return yaml.dump(proxies_clash, allow_unicode=True, sort_keys=False)

def uji_proxies(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Menyimpan latensi dari proxies
    proxy_latencies = []

    # Menggunakan ThreadPoolExecutor untuk pengujian paralel
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(uji_latency, proxy): proxy for proxy in data['proxies']}
        
        for future in futures:
            proxy = futures[future]
            try:
                latency = future.result()
                if latency is not None:
                    proxy_latencies.append({"proxy": proxy, "latency": latency})
                    print(f"✅ Latency untuk {proxy['server']}:{proxy['port']} adalah {latency:.2f} detik.")
                else:
                    print(f"❌ Koneksi ke {proxy['server']}:{proxy['port']} gagal.")
            except Exception as e:
                print(f"⚠️ Gagal memproses proxy {proxy['server']}:{proxy['port']}: {e}")

    # Simpan latensi ke dalam file
    latency_file_path = "proxies/latency_results.yaml"
    with open(latency_file_path, 'w', encoding='utf-8') as f:
        yaml.dump(proxy_latencies, f, allow_unicode=True, sort_keys=False)

def main():
    nodes = ambil_langganan()
    filtered_nodes = saring_node(nodes)
    os.makedirs("proxies", exist_ok=True)
    file_path = "proxies/trojan.yaml"
    
    # Buat file trojan.yaml
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(konversi_ke_clash(filtered_nodes))

    # Uji latency pada proxies setelah file dibuat
    uji_proxies(file_path)

if __name__ == "__main__":
    main()
