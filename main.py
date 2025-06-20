import base64
import requests
import yaml
import re
import os

# 节点订阅源（可以添加多个）
SUB_LINKS = [
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/networks/ws",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/ermaozi01/free_clash_vpn/main/v2ray",
    "https://raw.githubusercontent.com/iwxf/free-v2ray/master/v2",
    "https://raw.githubusercontent.com/Leon406/SubCrawler/main/sub/share/v2ray.txt"
]

def fetch_subscriptions():
    all_nodes = []
    for url in SUB_LINKS:
        try:
            print(f"获取订阅：{url}")
            res = requests.get(url, timeout=10)
            content = res.text.strip()
            if not content.startswith("vmess") and not content.startswith("trojan"):
                continue  # Skip if not vmess or trojan
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            all_nodes.extend(lines)
        except Exception as e:
            print(f"❌ 订阅源错误: {url} -> {e}")
    return all_nodes

def filter_nodes(nodes):
    filtered = []
    for node in nodes:
        info = base64_decode_node_info(node)
        if info and ("443" in info or "80" in info) and "ws" in info:
            filtered.append(node)
    return filtered  # No limit

def base64_decode_node_info(node):
    try:
        if node.startswith("vmess://"):
            raw = node[8:]
            decoded = base64.b64decode(raw + '===').decode('utf-8', errors='ignore')
            return decoded
        elif node.startswith("trojan://"):
            return node
    except:
        return ""

def save_v2ray_file(nodes, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for node in nodes:
            f.write(node.strip().replace("add", "$BUGCDN").replace("server", "$BUGCDN") + '\n')

def convert_to_clash(nodes):
    proxies = []
    for node in nodes:
        if node.startswith("vmess://"):
            try:
                vmess_config = base64.b64decode(node[8:] + '===').decode('utf-8', errors='ignore')
                config = eval(vmess_config.replace("false", "False").replace("true", "True"))
                proxies.append({
                    "name": config.get("ps", "Unnamed"),
                    "type": "vmess",
                    "server": "$BUGCDN",
                    "port": int(config["port"]),
                    "uuid": config["id"],
                    "alterId": int(config.get("aid", 0)),
                    "cipher": "auto",
                    "tls": "tls" if config.get("tls") else "",
                    "network": config.get("net", "tcp"),
                    "ws-opts": {
                        "path": config.get("path", ""),
                        "headers": {"Host": config.get("host", "")}
                    } if config.get("net") == "ws" else {}
                })
            except Exception as e:
                print(f"⚠️ vmess 解析失败: {e}")
    clash_config = {
        "proxies": proxies,
        "proxy-groups": [{
            "name": "🔰 节点选择",
            "type": "select",
            "proxies": [p["name"] for p in proxies]
        }],
        "rules": ["MATCH,🔰 节点选择"]
    }
    return yaml.dump(clash_config, allow_unicode=True)

def main():
    nodes = fetch_subscriptions()
    filtered_nodes = filter_nodes(nodes)
    os.makedirs("docs", exist_ok=True)
    save_v2ray_file(filtered_nodes, "docs/v2ray.txt")
    save_v2ray_file([base64.b64encode(n.encode()).decode() for n in filtered_nodes], "docs/v2ray64.txt")
    with open("docs/clash.yaml", "w", encoding="utf-8") as f:
        f.write(convert_to_clash(filtered_nodes))
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write("<h2>订阅已生成</h2><ul><li><a href='clash.yaml'>clash.yaml</a></li><li><a href='v2ray.txt'>v2ray.txt</a></li><li><a href='v2ray64.txt'>v2ray64.txt</a></li></ul>")

if __name__ == "__main__":
    main()
