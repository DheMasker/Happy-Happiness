# from uri clash yaml

import requests
import yaml
import os

# Variabel untuk alamat server
BUGCDN = "ava.game.naver.com"

# Daftar sumber langganan
SUB_LINKS = [
    "https://raw.githubusercontent.com/MrMohebi/xray-proxy-grabber-telegram/master/collected-proxies/clash-meta/all.yaml",
    "https://raw.githubusercontent.com/chengaopan/AutoMergePublicNodes/master/list.yml",
    "https://raw.githubusercontent.com/WilliamStar007/ClashX-V2Ray-TopFreeProxy/main/combine/clash.config.yaml",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/Eternity.yml",
    "https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/snippets/nodes.yml",
    "https://raw.githubusercontent.com/Airuop/cross/master/Eternity.yml",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/clash.config.yaml",
    "https://raw.githubusercontent.com/busymilk/clash_config_auto_build/main/config/config.yaml",
    "https://raw.githubusercontent.com/PuddinCat/BestClash/refs/heads/main/proxies.yaml",
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
            # Memeriksa apakah proxy memenuhi syarat
            if (proxy.get('type') in ['vmess', 'trojan'] and 
                proxy.get('network') == 'ws' and 
                proxy.get('port') == 443):
                
                # Buat entri proxy dengan 'name' di atas
                proxy_entry = {
                    "name": proxy.get("name", "Tanpa Nama"),  # Memastikan 'name' di atas
                    "server": BUGCDN,  # Ganti server dengan BUGCDN
                    **{k: v for k, v in proxy.items() if k != "name"}  # Tambahkan atribut lain tanpa 'name'
                }
                terfilter.append(proxy_entry)

    return terfilter

def hapus_duplikat(proxies):
    seen_vm = set()
    seen_trojan = set()
    hasil = []

    for proxy in proxies:
        if proxy.get('type') == 'vmess':
            identitas = (proxy.get('host'), proxy.get('uuid'))
            if identitas not in seen_vm:
                seen_vm.add(identitas)
                hasil.append(proxy)
        elif proxy.get('type') == 'trojan':
            identitas = (proxy.get('host'), proxy.get('password'))
            if identitas not in seen_trojan:
                seen_trojan.add(identitas)
                hasil.append(proxy)

    return hasil

def main():
    semua_proxies = []
    
    for link in SUB_LINKS:
        data = ambil_dari_sublink(link)
        if data:
            filtered_proxies = saring_proxies(data)
            semua_proxies.extend(filtered_proxies)  # Menggabungkan hasil

    # Hapus duplikat
    semua_proxies = hapus_duplikat(semua_proxies)

    # Simpan hasil yang sudah disaring ke file
    os.makedirs("proxies", exist_ok=True)
    with open("proxies/fromclashwscdn443.yaml", "w", encoding="utf-8") as f:
        yaml.dump({"proxies": semua_proxies}, f, allow_unicode=True, sort_keys=False)

if __name__ == "__main__":
    main()
