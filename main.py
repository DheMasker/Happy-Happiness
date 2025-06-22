import base64
import requests
import yaml
import os

# Daftar sumber langganan
SUB_LINKS = [ 
    "https://raw.githubusercontent.com/sevcator/5ubscrpt10n/refs/heads/main/full/5ubscrpt10n-b64.txt"
]

# Ganti server dengan BUGCDN
BUGCDN = "104.22.5.240"

def ambil_langganan():
    semua_node = []
    for url in SUB_LINKS:
        try:
            print(f"Mengambil langganan: {url}")
            res = requests.get(url, timeout=60)
            konten = res.text.strip()
            # Mendecode Base64 jika diperlukan
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

def konversi_ke_clash(nodes):
    proxies = []

    for node in nodes:
        if node.startswith("trojan://"):
            try:
                # Menghapus 'trojan://' dan memisahkan bagian
                trimmed_node = node[9:]  # Menghapus 'trojan://'
                at_index = trimmed_node.index('@')
                password = trimmed_node[:at_index].strip()  # Extracting password
                server_info = trimmed_node[at_index + 1:]  # Everything after @

                # Extract server and port
                colon_index = server_info.index(':')
                port_info = server_info[colon_index + 1:]  # Everything after port
                port = int(port_info.split('?')[0])  # Extracting port

                # Hanya proses jika port 443 atau 80
                if port not in [443, 80]:
                    continue

                # Extract additional parameters from server_info
                query_params = port_info.split('?')[1] if '?' in port_info else ''
                sni = ''
                host = ''
                path = None  # Set to None initially

                for param in query_params.split('&'):
                    if param.startswith('sni='):
                        sni = param.split('=')[1].strip().split('#')[0]  # Clean up sni
                    elif param.startswith('host='):
                        host = param.split('=')[1].strip().split('#')[0]  # Clean up host
                    elif param.startswith('path='):
                        path = param.split('=')[1].strip().split('#')[0].replace('%2F', '/')  # Decode path

                # Set host and sni based on availability
                if not sni and host:
                    sni = host
                elif not host and sni:
                    host = sni

                # Extract name from the node
                name_index = server_info.index('#')
                name = server_info[name_index + 1:].strip() if name_index != -1 else "unknown"

                # Tentukan network dari server_info jika ada "ws"
                network = ""
                if "ws" in server_info:
                    network = "ws"  # Ambil dari server_info jika ada "ws"
                else:
                    continue  # Jangan proses jika tidak ada "ws"

                # Append the proxy details, set server to BUGCDN
                proxy_detail = {
                    "name": name,
                    "server": BUGCDN,  # Ganti server dengan BUGCDN
                    "port": port,
                    "type": "trojan",
                    "password": password,  # Already stripped
                    "skip-cert-verify": True,
                    "sni": sni if sni else "",  # Use empty string if no sni
                    "network": network,  # Ambil dari server_info
                    "headers": {
                        "Host": host if host else ""  # Use empty string if no host
                    },
                    "udp": True
                }

                # Add path only if it's defined
                if path is not None:
                    proxy_detail["ws-opts"] = {
                        "path": path  # Set the path if available
                    }

                proxies.append(proxy_detail)

            except Exception as e:
                print(f"⚠️ Gagal memparsing trojan: {e}")

    proxies_clash = {
        "proxies": proxies
    }
    return yaml.dump(proxies_clash, allow_unicode=True, sort_keys=False)

def main():
    nodes = ambil_langganan()
    filtered_nodes = saring_node(nodes)
    os.makedirs("proxies", exist_ok=True)
    with open("proxies/trojan.yaml", "w", encoding="utf-8") as f:
        f.write(konversi_ke_clash(filtered_nodes))

if __name__ == "__main__":
    main()
