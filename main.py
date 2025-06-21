import base64
import requests
import yaml
import os

# Daftar sumber langganan
SUB_LINKS = [ 
    "https://raw.githubusercontent.com/sevcator/5ubscrpt10n/refs/heads/main/full/5ubscrpt10n-b64.txt"
]

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
                password = trimmed_node[:at_index]  # Extracting password
                server_info = trimmed_node[at_index + 1:]  # Everything after @

                # Extract server and port
                colon_index = server_info.index(':')
                server = server_info[:colon_index]  # Extracting server
                port_info = server_info[colon_index + 1:]  # Everything after port
                port = int(port_info.split('?')[0])  # Extracting port

                # Extract additional parameters (path, sni, host) from server_info
                path = server_info.split('/')[1] if '/' in server_info else ''  # Path
                query_params = port_info.split('?')[1] if '?' in port_info else ''

                # Replace %2F with /
                path = path.replace('%2F', '/')

                sni = ''
                host = ''

                for param in query_params.split('&'):
                    if param.startswith('sni='):
                        sni = param.split('=')[1]
                    elif param.startswith('host='):
                        host = param.split('=')[1]

                # Extract name from the node
                name_index = server_info.index('#')
                name = server_info[name_index + 1:] if name_index != -1 else "unknown"

                # Append the proxy details
                proxies.append({
                    "name": name,
                    "server": server,
                    "port": port,
                    "type": "trojan",
                    "password": password,
                    "skip-cert-verify": True,
                    "sni": sni,  # Extracted correctly
                    "network": "ws",
                    "ws-opts": {
                        "path": '/' + path,  # Include leading /
                        "headers": {
                            "Host": host  # Extracted correctly
                        }
                    },
                    "udp": True
                })
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
