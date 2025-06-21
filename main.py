import base64
import requests
import yaml
import os
import json
import urllib.parse

# List of subscription sources
SUB_LINKS = [
    "https://raw.githubusercontent.com/sevcator/5ubscrpt10n/refs/heads/main/full/5ubscrpt10n-b64.txt"
]

def fetch_subscription():
    all_nodes = []
    
    for url in SUB_LINKS:
        try:
            print(f"Retrieving subscription from: {url}")
            response = requests.get(url, timeout=60)
            content = response.text.strip()
            # Utilizing utf-8 encoding to support all characters
            if not content.startswith("trojan"):
                content = base64.b64decode(content + '===').decode('utf-8', errors='ignore')
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            all_nodes.extend(lines)
        except Exception as e:
            print(f"❌ Error while fetching subscription: {url} -> {e}")
    return all_nodes

def filter_nodes(nodes):
    filtered = []
    for node in nodes:
        if node.startswith("trojan://"):
            filtered.append(node)
    return filtered

def convert_to_clash(nodes):
    proxies = []
    for node in nodes:
        if node.startswith("trojan://"):
            try:
                trojan_config = base64.b64decode(node[9:] + '===').decode('utf-8', errors='ignore')
                config = json.loads(trojan_config.replace("false", "False").replace("true", "True"))

                # Extracting the name from the 'ps' parameter or from the part after #
                name = config.get("ps", "Unnamed")
                if "ps" not in config:
                    name = urllib.parse.unquote(node.split("#")[-1])  # Decode the name

                proxies.append({
                    "name": name,
                    "server": config["server"],
                    "port": int(config["port"]),
                    "type": "trojan",
                    "password": config["id"],
                    "skip-cert-verify": True,
                    "sni": config.get("host", ""),
                    "network": config.get("type", "ws"),
                    "ws-opts": {
                        "path": config.get("path", "/trojan-ws"),
                        "headers": {"Host": config.get("host", "")}
                    },
                    "udp": True
                })
            except Exception as e:
                print(f"⚠️ Failed to parse trojan: {e} for node: {node}")

    clash_proxies = {
        "proxies": proxies
    }
    return yaml.dump(clash_proxies, allow_unicode=True, sort_keys=False)

def main():
    nodes = fetch_subscription()
    filtered_nodes = filter_nodes(nodes)
    os.makedirs("proxies", exist_ok=True)
    with open("proxies/trojan.yaml", "w", encoding="utf-8") as f:
        f.write(convert_to_clash(filtered_nodes))

if __name__ == "__main__":
    main()
