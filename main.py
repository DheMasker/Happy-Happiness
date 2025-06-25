import requests
import yaml
import os

# Daftar sumber langganan
SUB_LINKS = [
    "https://raw.githubusercontent.com/kSLAWIASCA/actions/refs/heads/main/Clash.yml",
    "https://raw.githubusercontent.com/busymilk/clash_config_auto_build/main/config/config.yaml"
]

def ambil_dari_sublink(url):
    try:
        res = requests.get(url, timeout=60)
        return yaml.safe_load(res.text)  # Memuat data sebagai YAML
    except Exception as e:
        print(f"❌ Kesalahan saat mengambil data dari {url}: {e}")
        return None

def saring_proxies(data):
    terfilter = []
    if 'proxies' in data:
        for proxy in data['proxies']:
            # Hanya masukkan proxy jika 'name' tidak diawali dengan '-'
            if isinstance(proxy.get('name'), str) and not proxy['name'].startswith('-'):
                terfilter.append(proxy)  # Tambahkan proxy ke hasil
    return terfilter

def main():
    semua_proxies = []
    
    for link in SUB_LINKS:
        data = ambil_dari_sublink(link)
        if data:
            filtered_proxies = saring_proxies(data)
            semua_proxies.extend(filtered_proxies)  # Menggabungkan hasil

    # Simpan hasil yang sudah disaring ke file
    os.makedirs("proxies", exist_ok=True)
    with open("proxies/filtered_proxies.yaml", "w", encoding="utf-8") as f:
        yaml.dump({"proxies": semua_proxies}, f, allow_unicode=True, sort_keys=False)

if __name__ == "__main__":
    main()
