import base64
import requests
import yaml
import os
import json
import urllib.parse

# Daftar sumber langganan
SUB_LINKS = [ 
    "https://raw.githubusercontent.com/sevcator/5ubscrpt10n/refs/heads/main/full/5ubscrpt10n-b64.txt"
]

BUGCDN = "104.22.5.240"

def ambil_langganan():
    semua_node = []
    for url in SUB_LINKS:
        try:
            print(f"Mengambil langganan: {url}")
            res = requests.get(url, timeout=60)
            konten = res.text.strip()
            baris = [line.strip() for line in konten.splitlines() if line.strip()]

            for line in baris:
                if line.startswith("vmess://") or line.startswith("trojan://"):
                    semua_node.append(line)
                else:
                    # Coba decode jika konten adalah base64
                    try:
                        decoded_line = base64.b64decode(line + '===').decode('utf-8', errors='ignore')
                        if decoded_line.startswith("vmess://") or decoded_line.startswith("trojan://"):
                            semua_node.append(decoded_line)
                    except Exception as e:
                        print(f"⚠️ Gagal mendecode baris: {line} -> {e}")

        except Exception as e:
            print(f"❌ Kesalahan sumber langganan: {url} -> {e}")
    return semua_node

def saring_node(nodes):
    terfilter = []
    for node in nodes:
        if node.startswith("vmess://"):
            info = decode_node_info_base64(node)
            if info is not None and "path" in info and "host" in info and info["host"]:
                if info.get("port") in {443, 80} and info.get("net") == "ws":
                    terfilter.append(node)
        elif node.startswith("trojan://"):
            raw = node[10:]  
            parts = raw.split('@')
            if len(parts) == 2:
                server_info = parts[1]
                server_details = server_info.split(':')
                if len(server_details) == 2:
                    port = server_details[1].split('?')[0]
                    query = server_details[1].split('?')[1] if '?' in server_details[1] else ''
                    params = {param.split('=')[0]: param.split('=')[1] for param in query.split('&') if '=' in param}
                    if port in {'443', '80'} and params.get('type') == 'ws' and 'path' in params and 'host' in params and params['host']:
                        terfilter.append(node)
    return terfilter

def decode_node_info_base64(node):
    try:
        if node.startswith("vmess://"):
            raw = node[8:]
            decoded = base64.b64decode(raw + '===').decode('utf-8', errors='ignore')
            return json.loads(decoded.replace("false", "False").replace("true", "True"))
    except Exception as e:
        print(f"⚠️ Gagal mendecode node: {e}")
        return None

def konversi_ke_clash(nodes):
    proxies = []
    for node in nodes:
        if node.startswith("vmess://"):
            try:
                vmess_config = base64.b64decode(node[8:] + '===').decode('utf-8', errors='ignore')
                config = json.loads(vmess_config.replace("false", "False").replace("true", "True"))
                if "path" in config and "host" in config and config["host"]:
                    proxies.append({
                        "name": config.get("ps", "Tanpa Nama"),
                        "server": BUGCDN,
                        "port": int(config["port"]),
                        "type": "vmess",
                        "uuid": config["id"],
                        "alterId": int(config.get("aid", 0)),
                        "cipher": "auto",
                        "tls": True,
                        "skip-cert-verify": True,
                        "servername": config.get("host", ""),
                        "network": config.get("net") if config.get("net") == "ws" else None,
                        "ws-opts": {
                            "path": config.get("path", "/vmess-ws"),
                            "headers": {"Host": config.get("host", "")}
                        },
                        "udp": True
                    })
            except Exception as e:
                print(f"⚠️ Gagal memparsing vmess: {e}")
        
        elif node.startswith("trojan://"):
            try:
                raw = node[10:]  
                parts = raw.split('@')
                credentials, server_info = parts
                server_details = server_info.split(':')
                
                server = BUGCDN
                port = server_details[1].split('?')[0]
                query = server_details[1].split('?')[1] if '?' in server_details[1] else ''
                params = {param.split('=')[0]: param.split('=')[1] for param in query.split('&') if '=' in param}

                name = node.split('#')[1].strip() if '#' in node else 'default_name'
                name = urllib.parse.unquote(name)

                host = params.get('host', '')
                if '#' in host:
                    host = host.split('#')[0]
                host = urllib.parse.unquote(host)

                sni = params.get('sni', '')
                if '#' in sni:
                    sni = sni.split('#')[0]
                sni = urllib.parse.unquote(sni)

                path = urllib.parse.unquote(params.get('path', ''))
                if '#' in path:
                    path = path.split('#')[0]
                path = path.replace('%2F', '/')

                if port in {'443', '80'} and params.get('type') == 'ws' and path and host:
                    proxies.append({
                        "name": name,
                        "server": server,
                        "port": int(port),
                        "type": "trojan",
                        "password": urllib.parse.unquote(credentials),
                        "skip-cert-verify": True,
                        "sni": sni,
                        "network": params.get('type') if 'type' in params and params['type'] == 'ws' else None,
                        "ws-opts": {
                            "path": path,
                            "headers": {
                                "Host": host
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
    with open("proxies/vmesstrojanwscdn443and80.yaml", "w", encoding="utf-8") as f:
        f.write(konversi_ke_clash(filtered_nodes))

if __name__ == "__main__":
    main()
