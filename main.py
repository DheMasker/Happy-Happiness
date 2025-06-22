import requests

proxy = {
    "http": "http://ced307a2-af2c-4113-bebc-fb888c702b7d@104.22.5.240:443",
    "https": "http://ced307a2-af2c-4113-bebc-fb888c702b7d@104.22.5.240:443",
}

try:
    response = requests.get("https://httpbin.org/ip", proxies=proxy, timeout=5)
    print("Proxy aktif:", response.json())
except requests.exceptions.RequestException as e:
    print("Proxy tidak aktif:", e)
