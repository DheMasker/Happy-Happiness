from decimal import Decimal
import logging
import asyncio
from datetime import datetime
import sys
import aiohttp
import yaml
import collections

SubInfo = collections.namedtuple(
    "SubInfo",
    ['url', 'upload', 'download', 'total', 'expireSec']
)

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

async def ambil_isi_jarak(url):
    logger.info(f"Mulai mengambil konten dari: {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            text = await response.text()
            logger.info(f"Berhasil mengambil konten, panjang: {len(text)}")
            return text

async def ambil_info_langganan(session, url) -> SubInfo | None:
    try:
        logger.debug(f"Mulai mengambil informasi langganan: {url}")
        async with session.get(url) as response:
            response.raise_for_status()
            info_langganan = response.headers.get("subscription-userinfo")
            if not info_langganan:
                logger.warning(f"Tidak ditemukan informasi langganan: {url}")
                return None

            dict_info = {}
            for item in info_langganan.split(";"):
                item = item.strip()
                if not item:
                    continue
                kunci, nilai = item.split("=")
                dict_info[kunci.strip()] = nilai.strip()

            def aman_int(nilai):
                try:
                    if nilai.lower() == 'infinity':
                        return 0
                    if not nilai:
                        return sys.maxsize
                    return Decimal(nilai)
                except ValueError:
                    logger.error(f"Gagal memparsing data: <{nilai}>")
                    return -1

            return SubInfo(
                url=url,
                upload=aman_int(dict_info.get("upload")),
                download=aman_int(dict_info.get("download")),
                total=aman_int(dict_info.get("total")),
                expireSec=aman_int(dict_info.get("expire"))
            )
    except Exception as e:
        logger.error(f"Gagal mengambil informasi langganan: {url}, kesalahan: {str(e)}")
        return None

async def filter_url_valid_konkuren(urls: list[str]) -> list[str]:
    url_valid = []
    connector = aiohttp.TCPConnector(limit=50, force_close=True)
    start_time = datetime.now()

    async with aiohttp.ClientSession(
        connector=connector,
        headers={"User-Agent": "clash.meta"}
    ) as session:
        tasks = [
            asyncio.create_task(
                ambil_info_langganan(session, url)
            )
            for url in urls
        ]
        now = datetime.now().timestamp()

        with tqdm(total=len(urls), desc="Memfilter URL") as pbar:
            for task in asyncio.as_completed(tasks):
                try:
                    info: SubInfo | None = await task
                    if not info:
                        continue

                    penggunaan = info.download + info.upload
                    if info.total > 0 and penggunaan >= info.total:
                        logger.warning(f"Kuota langganan telah habis({penggunaan / (1024**3):.2f} GB) - {info.url}")
                        continue

                    if info.expireSec <= now:
                        logger.warning(f"Langganan telah kedaluwarsa - {info.url}")
                        continue

                    url_valid.append(info.url)
                    logger.info(f"URL valid: {info.url}")

                except asyncio.TimeoutError:
                    logger.warning("Permintaan waktu habis")
                except Exception as e:
                    logger.error(f"Kesalahan saat memproses URL: {str(e)}")
                finally:
                    pbar.update(1)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"Pemfilteran URL selesai - Total: {len(urls)}, Berhasil: {len(url_valid)}, Waktu: {duration:.2f} detik")
    return url_valid

async def filter_url_valid(urls: list[str]) -> list[str]:
    logger.info(f"Mulai memfilter URL, total: {len(urls)}")
    url_valid = await filter_url_valid_konkuren(urls)
    logger.info(f"Pemfilteran selesai, jumlah URL valid: {len(url_valid)}")
    return url_valid

async def simpan_proxies_yml(penyedia_proxy_valid):
    # Menggabungkan semua URL valid menjadi satu proxy
    if not penyedia_proxy_valid:
        logger.warning("Tidak ada proxy valid untuk disimpan.")
        return

    combined_url = "\n".join(penyedia_proxy_valid)
    
    proxies = [{
        "name": "Combined Proxy",
        "type": "combined",
        "server": "104.22.5.240",
        "port": 443,
        "network": "ws",
        "urls": combined_url  # Menggunakan semua URL asli yang valid
    }]

    with open("proxies.yaml", "w", encoding="utf-8") as file:
        yaml.dump({"proxies": proxies}, file, allow_unicode=True)

    logger.info("File proxies.yaml berhasil dibuat dengan proxy yang valid.")

async def utama():
    logger.info("Mulai memuat file konfigurasi")
    # Anda bisa menyesuaikan bagian ini jika diperlukan

    logger.info("Mulai mengambil konten langganan jarak jauh")
    url_jarak_jauh = "https://raw.githubusercontent.com/devojony/collectSub/refs/heads/main/sub/sub_all_clash.txt"
    konten = await ambil_isi_jarak(url_jarak_jauh)
    penyedia_proxy = [p for p in konten.split("\n") if p.strip()]
    logger.info(f"Jumlah URL awal yang diambil: {len(penyedia_proxy)}")

    logger.info("Mulai memfilter URL yang valid")
    penyedia_proxy_valid = await filter_url_valid(penyedia_proxy)

    # Simpan proxies yang valid ke file
    await simpan_proxies_yml(penyedia_proxy_valid)

if __name__ == "__main__":
    asyncio.run(utama())
