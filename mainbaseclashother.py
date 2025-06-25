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
combined_proxies = proxies1 + proxies2

# Menghapus duplikat
unique_proxies = []
seen = set()

for proxy in combined_proxies:
    # Gunakan string representasi dari proxy untuk menghindari duplikat
    proxy_key = (proxy['type'], proxy.get('password'), proxy.get('uuid'))
    if proxy_key not in seen:
        seen.add(proxy_key)
        unique_proxies.append(proxy)

# Simpan hasil ke file baru di folder proxies
with open('proxies/vmesstrojanwscdn443.yaml', 'w') as f:
    yaml.dump(unique_proxies, f)
