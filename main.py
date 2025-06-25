import base64
import requests
import yaml
import os
import json
import urllib.parse

# Daftar sumber langganan
SUB_LINKS = [ 
    "https://raw.githubusercontent.com/MrMohebi/xray-proxy-grabber-telegram/master/collected-proxies/clash-meta/all.yaml",
    "https://raw.githubusercontent.com/chengaopan/AutoMergePublicNodes/master/list.yml",
    "https://raw.githubusercontent.com/WilliamStar007/ClashX-V2Ray-TopFreeProxy/main/combine/clash.config.yaml",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/Eternity.yml",
    "https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/snippets/nodes.yml",
    "https://raw.githubusercontent.com/Airuop/cross/master/Eternity.yml",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/clash.config.yaml",
    "https://raw.githubusercontent.com/busymilk/clash_config_auto_build/main/config/config.yaml",
    "https://raw.githubusercontent.com/PuddinCat/BestClash/refs/heads/main/proxies.yaml",
    "https://raw.githubusercontent.com/kSLAWIASCA/actions/refs/heads/main/Clash.yml",
    "https://raw.githubusercontent.com/busymilk/clash_config_auto_build/main/config/config.yaml"
]

BUGCDN = "104.22.5.240"

def ambil_langganan():
    semua_node = []
    for url in SUB_LINKS:
        try:
            print(f"Mengambil langganan: {url}")
            res = requests.get(url, timeout=60)
            konten = res.text.strip()
            
            # Mencoba mendekode konten dan menangani karakter non-ASCII
            try:
                konten = konten.encode('utf-8').decode('utf-8', errors='ignore')
            except Exception as e:
                print(f"⚠️ Kesalahan saat mendekode konten: {e}")

            if not konten.startswith(("vmess://", "trojan://")):
                try:
                    konten = base64.b64decode(konten + '===').decode('utf-8', errors='ignore')
                except Exception as e:
                    print(f"⚠️ Kesalahan saat mendekode base64: {e}")
                    continue  # Lanjutkan ke iterasi berikutnya jika ada kesalahan

            baris = [line.strip() for line in konten.splitlines() if line.strip()]
            semua_node.extend(baris)
        except Exception as e:
            print(f"❌ Kesalahan sumber langganan: {url} -> {e}")
    return semua_node

def saring_node(nodes):
    terfilter = []
    for node in nodes:
        if node.startswith("vmess://"):
            info = decode_node_info_base64(node)
            if info is not None and "path" in info:
                if info.get("port") == 443 and info.get("net") == "ws":
                    name = info.get("ps", "").replace('"', '')
                    servername = info.get("host", "").split('#')[0]
                    if not servername:
                        servername = info.get("servername", "").split('#')[0]
                    
                    # Hanya tambahkan jika ada nilai di host, servername, dan path
                    if (servername or info.get("host")) and info.get("path"):
                        terfilter.append(node)

        elif node.startswith("trojan://"):
            raw = node[9:]  
            parts = raw.split('@')
            if len(parts) == 2:
                server_info = parts[1]
                server_details = server_info.split(':')
                if len(server_details) == 2:
                    port = server_details[1].split('?')[0]
                    query = server_details[1].split('?')[1] if '?' in server_details[1] else ''
                    params = {param.split('=')[0]: param.split('=')[1] for param in query.split('&') if '=' in param}

                    name = node.split('#')[1].strip() if '#' in node else 'default_name'
                    name = name.replace('"', '')

                    host = params.get('host', '').split('#')[0]
                    if not host:
                        host = params.get('sni', '').split('#')[0]

                    # Hanya tambahkan jika ada nilai di host atau sni dan path
                    if port == '443' and params.get('type') == 'ws' and (host or params.get('sni')) and params.get('path'):
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
    unique_vmess_ids = set()  # Set untuk menyimpan kombinasi unik dari uuid dan host untuk vmess
    unique_trojan_ids = set()  # Set untuk menyimpan kombinasi unik dari password dan host untuk trojan

    for node in nodes:
        if node.startswith("vmess://"):
            try:
                vmess_config = base64.b64decode(node[8:] + '===').decode('utf-8', errors='ignore')
                config = json.loads(vmess_config.replace("false", "False").replace("true", "True"))
                name = config.get("ps", "Tanpa Nama").replace('"', '')  # Menghapus tanda kutip
                servername = config.get("host", "") or config.get("servername", "")
                if servername and '#' in servername:
                    servername = servername.split('#')[0]

                uuid = config.get("id")
                host = config.get("host", "")
                proxy_id = (uuid, host)  # Kombinasi unik berdasarkan uuid dan host
                if proxy_id not in unique_vmess_ids:  # Memeriksa keunikan
                    unique_vmess_ids.add(proxy_id)
                    proxies.append({
                        "name": name,
                        "server": BUGCDN,
                        "port": int(config["port"]),
                        "type": "vmess",
                        "uuid": uuid,
                        "alterId": int(config.get("aid", 0)),
                        "cipher": "auto",
                        "tls": True,
                        "skip-cert-verify": True,
                        "servername": servername.replace('"', ''),  # Menghapus tanda kutip
                        "network": config.get("net", "ws"),
                        "ws-opts": {
                            "path": config.get("path", "/vmess-ws"),
                            "headers": {
                                "Host": servername.replace('"', '')  # Mengisi Host dengan servername
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
                if '#' in host:
                    host = host.split('#')[0]
                host = urllib.parse.unquote(host)

                password = urllib.parse.unquote(credentials)
                proxy_id = (password, host)  # Kombinasi unik berdasarkan password dan host
                if proxy_id not in unique_trojan_ids:  # Memeriksa keunikan
                    unique_trojan_ids.add(proxy_id)
                    proxies.append({
                        "name": node.split('#')[1].strip() if '#' in node else 'default_name',
                        "server": BUGCDN,
                        "port": port,
                        "type": "trojan",
                        "password": password,
                        "skip-cert-verify": True,
                        "sni": params.get('sni', host),  # Mengisi SNI dengan host
                        "network": params.get('type') if 'type' in params and params['type'] == 'ws' else None,
                        "ws-opts": {
                            "path": urllib.parse.unquote(params.get('path', '')),
                            "headers": {
                                "Host": host if host else params.get('sni', '')  # Mengisi Host
                            }
                        },
                        "udp": True
                    })
            except Exception as e:
                print(f"⚠️ Gagal memparsing trojan: {e}")

    proxies_clash = {
        "proxies": proxies
    }
    return yaml.dump(proxies_clash, allow_unicode=True, sort_keys=False).replace('"', '')  # Menghapus tanda kutip

def main():
    nodes = ambil_langganan()
    filtered_nodes = saring_node(nodes)
    os.makedirs("proxies", exist_ok=True)
    with open("proxies/vmesstrojanwscdn443.yaml", "w", encoding="utf-8") as f:
        f.write(konversi_ke_clash(filtered_nodes))

if __name__ == "__main__":
    main()
