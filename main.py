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
            terfilter.append(node)
    return terfilter

def konversi_ke_clash(nodes):
    proxies = []
    log_errors = []

    for node in nodes:
        if node.startswith("trojan://"):
            try:
                # Menghapus 'trojan://' dan memisahkan bagian
                trimmed_node = node[9:]  # Menghapus 'trojan://'
                at_index = trimmed_node.index('@')
                password = trimmed_node[:at_index].strip()  # Extracting password
                server_info = trimmed_node[at_index + 1:]  # Everything after @

                # Extract server and port using regex for better handling
                match = re.match(r'([^:]+):(\d+)(?:\?(.*))?(#.*)?', server_info)
                if not match:
                    log_errors.append(f"⚠️ Format server tidak valid: {server_info}")
                    continue

                server, port_str, query_params, name_fragment = match.groups()
                try:
                    port = int(port_str)  # Extracting port
                except ValueError:
                    log_errors.append(f"⚠️ Port tidak valid: {port_str}")
                    continue

                # Hanya proses jika port 443 atau 80
                if port not in [443, 80]:
                    continue

                # Memastikan type ws
                if "ws" not in node:
                    continue

                # Initialize parameters
                sni = ''
                host = ''
                path = None  # Set to None initially

                if query_params:
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

                # Extract name from the node if available
                name = name_fragment[1:].strip() if name_fragment else "unknown"

                # Append the proxy details, set server to BUGCDN
                proxy_detail = {
                    "name": name,
                    "server": BUGCDN,  # Ganti server dengan BUGCDN
                    "port": port,
                    "type": "trojan",
                    "password": password,  # Already stripped
                    "skip-cert-verify": True,
                    "sni": sni if sni else "",  # Use empty string if no sni
                    "network": "ws",
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
                log_errors.append(f"⚠️ Gagal memparsing trojan: {e}")

    proxies_clash = {
        "proxies": proxies
    }

    # Simpan log kesalahan ke dalam file
    if log_errors:
        with open("proxies/error_log.txt", "w", encoding="utf-8") as log_file:
            for error in log_errors:
                log_file.write(error + "\n")
    
    return yaml.dump(proxies_clash, allow_unicode=True, sort_keys=False)

def main():
    nodes = ambil_langganan()
    filtered_nodes = saring_node(nodes)
    os.makedirs("proxies", exist_ok=True)
    with open("proxies/trojan.yaml", "w", encoding="utf-8") as f:
        f.write(konversi_ke_clash(filtered_nodes))

if __name__ == "__main__":
    main()
