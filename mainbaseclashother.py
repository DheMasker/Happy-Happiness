import requests
import yaml
import os

# Buat folder proxies jika belum ada
os.makedirs('proxies', exist_ok=True)

# Ambil data dari URL
url1 = "https://raw.githubusercontent.com/DheMasker/Happy-Happiness/refs/heads/main/proxies/frombasewscdn443.yaml"
url2 = "https://raw.githubusercontent.com/DheMasker/Happy-Happiness/refs/heads/main/proxies/fromclashwscdn443.yaml"

data1 = requests.get(url1).text
data2 = requests.get(url2).text

# Muat data YAML
proxies1 = yaml.safe_load(data1)
proxies2 = yaml.safe_load(data2)

# Gabungkan kedua list proxy
combined_proxies = proxies1['proxies'] + proxies2['proxies']

# Menghapus duplikat berdasarkan type, uuid (untuk vmess) dan password (untuk trojan)
unique_proxies = {}
for proxy in combined_proxies:
    proxy_type = proxy.get('type')
    if proxy_type == 'vmess':
        key = (proxy_type, proxy.get('uuid'), proxy.get('ws-opts', {}).get('headers', {}).get('Host'))
    elif proxy_type == 'trojan':
        key = (proxy_type, proxy.get('password'), proxy.get('ws-opts', {}).get('headers', {}).get('Host'))
    else:
        continue  # Jika tipe tidak dikenali, lewati

    if key not in unique_proxies:
        unique_proxies[key] = proxy

# Simpan hasil ke file baru di folder proxies
with open('proxies/vmesstrojanwscdn443.yaml', 'w') as f:
    yaml.dump({'proxies': list(unique_proxies.values())}, f)
