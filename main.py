import logging
import asyncio
import aiohttp
import yaml
import os

# Konfigurasi pengaturan logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

async def ambil_info_langganan(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            info_langganan = response.headers.get("subscription-userinfo")
            if not info_langganan:
                logger.warning(f"Tidak ditemukan informasi langganan: {url}")
                return None

            # Parsing informasi langganan
            dict_info = {}
            for item in info_langganan.split(";"):
                item = item.strip()
                if not item:
                    continue
                kunci, nilai = item.split("=")
                dict_info[kunci.strip()] = nilai.strip()

            return dict_info
    except Exception as e:
        logger.error(f"Gagal mengambil informasi langganan: {url}, kesalahan: {str(e)}")
        return None

async def filter_url_valid_konkuren(urls):
    valid_urls = []
    connector = aiohttp.TCPConnector(limit=50)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [ambil_info_langganan(session, url) for url in urls]
        for task in asyncio.as_completed(tasks):
            info = await task
            if info and (info.get("type") in ["trojan", "vmess"] and 
                         info.get("network") == "ws" and 
                         int(info.get("port", 0)) in [443, 80]):
                valid_urls.append(info)  # Simpan informasi valid

    return valid_urls

async def simpan_proxies_yml(penyedia_proxy_valid):
    if not penyedia_proxy_valid:
        logger.warning("Tidak ada proxy valid untuk disimpan.")
        return

    # Simpan hanya URL tanpa format tambahan
    proxies = [f"{proxy['url']}" for proxy in penyedia_proxy_valid]

    os.makedirs("proxies", exist_ok=True)

    # Simpan file di dalam folder 'proxies'
    with open("proxies/proxies.yaml", "w", encoding="utf-8") as file:
        yaml.dump({"proxies": proxies}, file, allow_unicode=True)

    logger.info("File proxies.yaml berhasil dibuat dengan proxy yang valid.")

async def utama():
    remote_url = "https://raw.githubusercontent.com/devojony/collectSub/refs/heads/main/sub/sub_all_clash.txt"
    async with aiohttp.ClientSession() as session:
        async with session.get(remote_url) as response:
            konten = await response.text()
            penyedia_proxy = [p.strip() for p in konten.split("\n") if p.strip()]
    
    penyedia_proxy_valid = await filter_url_valid_konkuren(penyedia_proxy)
    await simpan_proxies_yml(penyedia_proxy_valid)

if __name__ == "__main__":
    asyncio.run(utama())
