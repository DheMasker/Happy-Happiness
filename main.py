import base64
import requests
import yaml
import os
import re

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
            trimmed_node = node[9:]  # Menghapus 'trojan://'
            
            # Pastikan format memiliki '@'
            if '@' not in trimmed_node:
                print(f"⚠️ Format tidak valid (tanpa '@'): {trimmed_node}")
                continue
            
            at_index = trimmed_node.index('@')
            # Ambil bagian setelah '@'
            server_port_info = trimmed_node[at_index + 1:]  # Everything after @

            # Pastikan ada ':' di server_port_info untuk mencegah ValueError
            if ':' not in server_port_info:
                print(f"⚠️ Format tidak valid (tanpa ':'): {server_port_info}")
                continue

            # Extract server dan port
            colon_index = server_port_info.index(':')
            port_info = server_port_info[colon_index + 1:]  # Everything after port
            
            # Cek apakah port dalam format yang valid
            port_match = re.match(r'(\[.*?\]|[^:]+):(\d+)', server_port_info)
            if port_match:
                port = int(port_match.group(2))  # Ambil port
                # Cek jika node memiliki "/?type=ws" dan port 443 atau 80
                if "/?type=ws" in port_info and port in [443, 80]:
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
                # Ambil bagian setelah '@'
                server_port_info = trimmed_node[at_index + 1:]  # Everything after @

                # Pastikan ada ':' di server_port_info untuk mencegah ValueError
                if ':' not in server_port_info:
                    print(f"⚠️ Format tidak valid (tanpa ':'): {server_port_info}")
                    continue

                # Extract server dan port
                colon_index = server_port_info.index(':')
                port_info = server_port_info[colon_index + 1:]  # Everything after port
                
                # Extract port using regex
                port_match = re.match(r'(\[.*?\]|[^:]+):(\d+)', server_port_info)
                if port_match:
                    port = int(port_match.group(2))  # Ambil port
                else:
                    continue  # Skip jika tidak ada port yang valid

                # Extract additional parameters dari port_info
                query_params = port_info.split('?')[1] if '?' in port_info else ''
                sni = ''
                host = ''
                path = None  # Set to None initially
                network = None  # Initialize network variable

                for param in query_params.split('&'):
                    # Ambil nilai dari param "sni", "host", "path", dan "type"
                    if param.startswith('sni='):
                        sni = param.split('=')[1].strip().split('#')[0]  # Clean up sni
                    elif param.startswith('host='):
                        host = param.split('=')[1].strip().split('#')[0]  # Clean up host
                    elif param.startswith('path='):
                        path = param.split('=')[1].strip().split('#')[0].replace('%2F', '/')  # Decode path
                    elif param.startswith('type='):
                        network = param.split('=')[1].strip().split('#')[0]  # Ambil nilai type

                # Set host dan sni berdasarkan ketersediaan
                if not sni and host:
                    sni = host
                elif not host and sni:
                    host = sni

                # Extract name dari node
                name_index = server_port_info.index('#')
                name = server_port_info[name_index + 1:].strip() if name_index != -1 else "unknown"

                # Append detail proxy, set server ke BUGCDN
                proxy_detail = {
                    "name": name,
                    "server": BUGCDN,  # Ganti server dengan BUGCDN
                    "port": port,
                    "type": "trojan",
                    "password": password,  # Already stripped
                    "skip-cert-verify": True,
                    "sni": sni if sni else "",  # Use empty string if no sni
                    "network": network if network else "",  # Set network to type
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
