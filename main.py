import requests
import speedtest
import base64
import yaml
import os

async def fetch_remote_txt(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def extract_nodes(content):
    nodes = []
    for line in content.splitlines():
        if 'vmess' in line and 'ws' in line:
            nodes.append(line)
        elif 'trojan' in line and 'ws' in line:
            nodes.append(line)
    return nodes

def test_proxy(node):
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        return download_speed, upload_speed
    except Exception as e:
        print(f"Error testing {node}: {e}")
        return None

def convert_to_clash_yaml(nodes):
    clash_proxies = []
    
    for node in nodes:
        download_speed, upload_speed = test_proxy(node)
        if download_speed is not None and upload_speed is not None:
            node_name = f"{node}_{int(download_speed)}Mbps"
            clash_proxies.append({
                'name': node_name,
                'type': 'vmess' if 'vmess' in node else 'trojan',
                'server': 'YOUR_SERVER',  # Replace with actual server extraction
                'port': 'YOUR_PORT',  # Replace with actual port extraction
                'uuid': 'YOUR_UUID',  # Replace with actual UUID extraction
                'alterId': 64,
                'cipher': 'auto',
                'tls': True,
                'network': 'ws',
                'ws-opts': {
                    'path': '/YOUR_PATH',  # Replace with actual path extraction
                    'headers': {
                        'Host': 'YOUR_HOST'  # Replace with actual host extraction
                    }
                }
            })
    return clash_proxies

async def main():
    remote_url = "https://raw.githubusercontent.com/devojony/collectSub/refs/heads/main/sub/sub_all_clash.txt"
    content = await fetch_remote_txt(remote_url)
    nodes = extract_nodes(content)
    
    clash_proxies = convert_to_clash_yaml(nodes)
    
    os.makedirs('proxies', exist_ok=True)
    with open('proxies/clash_proxies.yaml', 'w') as f:
        yaml.dump({'proxies': clash_proxies}, f)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
