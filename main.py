import asyncio
import aiohttp
import speedtest
import base64
import yaml

async def fetch_remote_txt(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

def parse_nodes(content):
    nodes = []
    lines = content.splitlines()
    for line in lines:
        if 'vmess' in line or 'trojan' in line:
            try:
                decoded_line = base64.b64decode(line).decode('utf-8')
                if 'ws' in decoded_line:
                    nodes.append(decoded_line)
            except Exception:
                continue
    return nodes

async def test_speed(node):
    st = speedtest.Speedtest()
    st.get_best_server()
    try:
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        upload_speed = st.upload() / 1_000_000      # Convert to Mbps
        return download_speed, upload_speed
    except Exception:
        return None, None

async def main():
    remote_url = "https://raw.githubusercontent.com/devojony/collectSub/refs/heads/main/sub/sub_all_clash.txt"
    content = await fetch_remote_txt(remote_url)
    nodes = parse_nodes(content)

    clash_nodes = []
    for node in nodes:
        download, upload = await test_speed(node)
        if download and upload:
            node_name = f"{node} - DL:{download:.2f} Mbps, UL:{upload:.2f} Mbps"
            clash_nodes.append(node_name)

    clash_yaml = {
        'proxies': [node for node in clash_nodes]
    }

    with open('clash_config.yaml', 'w') as file:
        yaml.dump(clash_yaml, file)

if __name__ == "__main__":
    asyncio.run(main())
