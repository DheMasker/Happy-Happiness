import requests
import yaml
import os
import json
import urllib.parse
import base64

# Daftar sumber langganan
# Base64 & Uri

SUB_LINKS = [ 
   
"https://raw.githubusercontent.com/Surfboardv2ray/Proxy-sorter/refs/heads/main/input/proxies.txt",

"https://raw.githubusercontent.com/Airuop/cross/refs/heads/master/sub/sub_merge_base64.txt",
"https://raw.githubusercontent.com/peasoft/NoMoreWalls/refs/heads/master/list.txt",
"https://raw.githubusercontent.com/mahdibland/V2RayAggregator/refs/heads/master/sub/sub_merge_base64.txt",
"https://raw.githubusercontent.com/MrMohebi/xray-proxy-grabber-telegram/refs/heads/master/collected-proxies/row-url/all.txt",
"https://raw.githubusercontent.com/chengaopan/AutoMergePublicNodes/refs/heads/master/list.txt",
"https://raw.githubusercontent.com/4n0nymou3/multi-proxy-config-fetcher/refs/heads/main/configs/proxy_configs.txt",
"https://raw.githubusercontent.com/PlanAsli/configs-collector-v2ray/refs/heads/main/sub/all_configs.txt",
"https://raw.githubusercontent.com/V2RayRoot/V2RayConfig/refs/heads/main/Config/vmess.txt",
"https://raw.githubusercontent.com/gfpcom/free-proxy-list/refs/heads/main/list/trojan.txt",
"https://raw.githubusercontent.com/gfpcom/free-proxy-list/refs/heads/main/list/vmess.txt",
"https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/refs/heads/main/subscriptions/v2ray/all_sub.txt",
"https://raw.githubusercontent.com/wuqb2i4f/xray-config-toolkit/refs/heads/main/output/base64/mix-uri",
"https://raw.githubusercontent.com/T3stAcc/V2Ray/refs/heads/main/All_Configs_Sub.txt",
"https://raw.githubusercontent.com/Surfboardv2ray/v2ray-worker-sub/refs/heads/master/providers/providers",
"https://raw.githubusercontent.com/MhdiTaheri/V2rayCollector/refs/heads/main/sub/mix",
"https://raw.githubusercontent.com/Surfboardv2ray/Proxy-sorter/refs/heads/main/submerge/converted.txt",
"https://raw.githubusercontent.com/Surfboardv2ray/TGParse/refs/heads/main/splitted/vmess",
"https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/refs/heads/main/subscriptions/base64/all_sub.txt",
"https://raw.githubusercontent.com/lagzian/SS-Collector/refs/heads/main/vmess_B64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub1_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub2_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub3_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub4_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub5_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub6_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub7_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub8_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub9_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub10_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub11_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub12_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub13_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub14_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub15_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub16_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub17_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub18_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub19_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub20_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub21_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub22_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub23_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub24_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub25_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub26_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub27_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub28_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub29_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub30_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub31_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub32_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub33_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub34_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub35_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub36_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub37_base64.txt",
"https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Base64/Sub38_base64.txt",
"https://raw.githubusercontent.com/Pawdroid/Free-servers/refs/heads/main/sub",
"https://raw.githubusercontent.com/roosterkid/openproxylist/refs/heads/main/V2RAY_BASE64.txt",
"https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vmess",
"https://raw.githubusercontent.com/sevcator/5ubscrpt10n/refs/heads/main/full/5ubscrpt10n-b64.txt",
"https://raw.githubusercontent.com/mheidari98/.proxy/refs/heads/main/all",

"https://raw.githubusercontent.com/V2RAYCONFIGSPOOL/V2RAY_SUB/refs/heads/main/v2ray_configs.txt"
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
