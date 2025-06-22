import os
import speedtest

def test_proxy_speed(proxy):
    st = speedtest.Speedtest()
    
    # Mengatur server dan proxy
    st.get_best_server()
    
    # Setting proxy
    st.proxy = proxy

    print(f"Testing proxy: {proxy}")
    download_speed = st.download() / 1_000_000  # Convert to Mbps
    upload_speed = st.upload() / 1_000_000      # Convert to Mbps
    return download_speed, upload_speed

# Ganti dengan informasi proxy Anda
proxy = "trojan://e9f0702f-c211-4b8e-a827-c0135962d805@104.22.5.240:443/?type=ws&host=free.c-stuff.Web.id&path=%2FFree%2FTG-at-BitzBlack%2F172.232.239.151-587&security=tls&sni=free.c-stuff.Web.id&allowInsecure=1"

# Uji kecepatan
download, upload = test_proxy_speed(proxy)
print(f"Download speed: {download:.2f} Mbps")
print(f"Upload speed: {upload:.2f} Mbps")

# Nama proxy asli
original_proxy_name = "Akamai Connected Cloud"

# Menambahkan hasil ke dalam nama proxy
proxy_name = f"{original_proxy_name} - {download:.2f} Mbps"

# Konfigurasi Clash
clash_config = f"""
proxies:
  - name: "{proxy_name}"
    type: trojan
    server: "104.22.5.240"
    port: 443
    password: "e9f0702f-c211-4b8e-a827-c0135962d805"
    security: "tls"
    sni: "free.c-stuff.Web.id"
    skip-cert-verify: true
    network: "ws"
    ws-opts:
      path: "/Free/TG-at-BitzBlack/172.232.239.151-587"
      host: "free.c-stuff.Web.id"
"""

# Membuat folder jika belum ada
os.makedirs("proxies", exist_ok=True)

# Simpan konfigurasi ke file dalam folder proxies
file_path = os.path.join("proxies", "clash_config.yaml")
with open(file_path, "w") as f:
    f.write(clash_config)

print(f"Konfigurasi Clash telah disimpan ke {file_path}")
