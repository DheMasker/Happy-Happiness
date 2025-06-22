import requests

def cek_keaktifan_url(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"{url} aktif.")
        else:
            print(f"{url} tidak aktif. Kode status: {response.status_code}")
    except requests.RequestException:
        print(f"{url} tidak aktif. Terjadi kesalahan saat menghubungi server.")

# Ganti URL di bawah ini dengan yang ingin Anda periksa
url_to_check = "http://premium.crazpayment.my.id:443/"
cek_keaktifan_url(url_to_check)
