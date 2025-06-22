import os
import requests
import speedtest
import base64
import yaml
import re

def get_proxy_links(url):
    response = requests.get(url)
    if response.status_code == 200:
        content = response.text
        # Ambil semua link yang mengandung 'vmess' atau 'trojan' dengan ws
        proxy_links = re.findall(r'(https?://\S+)', content)
        return [link for link in proxy_links if 'ws' in link]
    return []

def test_proxy(link):
    try:
        # Menggunakan speedtest untuk menguji kecepatan
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000  # dalam Mbps
        upload_speed = st.upload() / 1_000_000  # dalam Mbps
        return download_speed, upload_speed
    except Exception as e:
        print(f"Failed to test proxy {link}: {e}")
        return None, None

def convert_to_clash_format(proxies):
    clash_format = {'proxies': []}
    for proxy in proxies:
        clash_format['proxies'].append(proxy)
    return clash_format

def main():
    url = "https://raw.githubusercontent.com/devojony/collectSub/refs/heads/main/sub/sub_all_clash.txt"
    proxy_links = get_proxy_links(url)
    valid_proxies = []

    for link in proxy_links:
        download_speed, upload_speed = test_proxy(link)
        if download_speed and upload_speed:
            proxy_name = f"{link} - Download: {download_speed:.2f} Mbps"
            valid_proxies.append(proxy_name)

    clash_proxies = convert_to_clash_format(valid_proxies)
    
    # Pastikan folder 'proxies' ada
    os.makedirs('proxies', exist_ok=True)
    
    # Simpan ke file YAML di dalam folder 'proxies'
    yaml_file_path = os.path.join('proxies', 'proxies_clash.yaml')
    with open(yaml_file_path, 'w') as yaml_file:
        yaml.dump(clash_proxies, yaml_file)

    print(f"Proxies have been saved to {yaml_file_path}")

if __name__ == "__main__":
    main()
