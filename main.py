import requests
import yaml
import os
import json
import urllib.parse
import base64

# Daftar sumber langganan
# Base64 & Uri

SUB_LINKS = [ 
   

"https://raw.githubusercontent.com/sevcator/5ubscrpt10n/refs/heads/main/full/5ubscrpt10n-b64.txt"
]



#

BUGCDN = "104.22.5.240"

def ambil_langganan():
    semua_node = []
    for url in SUB_LINKS:
        try:
            print(f"Mengambil langganan: {url}")
            res = requests.get(url, timeout=60)
            konten = res.text.strip()

            # Proses konten untuk mendeteksi node
            if konten.startswith(("vmess://", "trojan://")):
                semua_node.append(konten)
            else:
                # Coba mendekode base64 jika tidak dalam format yang diharapkan
                try:
                    konten = base64.b64decode(konten + '===').decode('utf-8', errors='ignore')
                    baris = [line.strip() for line in konten.splitlines() if line.strip()]
                    semua_node.extend(baris)
                except Exception as e:
                    print(f"⚠️ Kesalahan saat mendekode base64: {e}")
                    continue  # Lanjutkan jika ada kesalahan
        except Exception as e:
            print(f"❌ Kesalahan sumber langganan: {url} -> {e}")
    return semua_node

def saring_node(nodes):
    terfilter = []
    for node in nodes:
        if node.startswith("vmess://"):
            info = decode_node_info(node)
            if info is not None and "path" in info:
                if info.get("port") == 443 and info.get("net") == "ws":
                    terfilter.append(node)

        elif node.startswith("trojan://"):
            parts = node[9:].split('@')
            if len(parts) == 2:
                server_info = parts[1]
                server_details = server_info.split(':')
                if len(server_details) == 2:
                    port = server_details[1].split('?')[0]
                    query = server_details[1].split('?')[1] if '?' in server_details[1] else ''
                    params = {param.split('=')[0]: param.split('=')[1] for param in query.split('&') if '=' in param}

                    if port == '443' and params.get('type') == 'ws' and params.get('path'):
                        terfilter.append(node)
    return terfilter

def decode_node_info(node):
    try:
        if node.startswith("vmess://"):
            raw = node[8:]
            decoded = json.loads(urllib.parse.unquote(raw))
            return decoded
    except Exception as e:
        print(f"⚠️ Gagal mendecode node: {e}")
        return None

def konversi_ke_clash(nodes):
    proxies = []
    unique_vmess_ids = set()
    unique_trojan_ids = set()

    for node in nodes:
        if node.startswith("vmess://"):
            try:
                info = decode_node_info(node)
                name = info.get("ps", "Tanpa Nama")
                uuid = info.get("id")
                host = info.get("host", "")
                proxy_id = (uuid, host)
                if proxy_id not in unique_vmess_ids:
                    unique_vmess_ids.add(proxy_id)
                    proxies.append({
                        "name": name,
                        "server": BUGCDN,
                        "port": int(info["port"]),
                        "type": "vmess",
                        "uuid": uuid,
                        "alterId": int(info.get("aid", 0)),
                        "cipher": "auto",
                        "tls": True,
                        "skip-cert-verify": True,
                        "servername": host,
                        "network": info.get("net", "ws"),
                        "ws-opts": {
                            "path": info.get("path", "/vmess-ws"),
                            "headers": {
                                "Host": host
                            }
                        },
                        "udp": True
                    })
            except Exception as e:
                print(f"⚠️ Gagal memparsing vmess: {e}")

        elif node.startswith("trojan://"):
            try:
                raw = node[9:]  
                parts = raw.split('@')
                credentials, server_info = parts
                
                server_details = server_info.split(':')
                port = int(server_details[1].split('?')[0])
                query = server_details[1].split('?')[1] if '?' in server_details[1] else ''
                params = {param.split('=')[0]: param.split('=')[1] for param in query.split('&') if '=' in param}

                host = params.get('host', '')
                password = urllib.parse.unquote(credentials)
                proxy_id = (password, host)
                if proxy_id not in unique_trojan_ids:
                    unique_trojan_ids.add(proxy_id)
                    proxies.append({
                        "name": node.split('#')[1].strip() if '#' in node else 'default_name',
                        "server": BUGCDN,
                        "port": port,
                        "type": "trojan",
                        "password": password,
                        "skip-cert-verify": True,
                        "sni": params.get('sni', host),
                        "network": params.get('type') if 'type' in params and params['type'] == 'ws' else None,
                        "ws-opts": {
                            "path": urllib.parse.unquote(params.get('path', '')),
                            "headers": {
                                "Host": host if host else params.get('sni', '')
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
    with open("proxies/vmesstrojanwscdn443.yaml", "w", encoding="utf-8") as f:
        f.write(konversi_ke_clash(filtered_nodes))

if __name__ == "__main__":
    main()
