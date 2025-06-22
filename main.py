from decimal import Decimal
import logging
import asyncio
from datetime import datetime
import sys
import aiohttp
import yaml
import collections
import os
from tqdm import tqdm  # Include this for displaying a progress bar

SubInfo = collections.namedtuple(
    "SubInfo",
    ['url', 'upload', 'download', 'total', 'expireSec']
)

# Configure logging settings
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

async def fetch_content(url):
    logger.info(f"Initiating content retrieval from: {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            text = await response.text()
            logger.info(f"Content fetched successfully, length: {len(text)}")
            return text

async def get_subscription_info(session, url) -> SubInfo | None:
    try:
        logger.debug(f"Fetching subscription info from: {url}")
        async with session.get(url) as response:
            response.raise_for_status()
            subscription_info = response.headers.get("subscription-userinfo")
            if not subscription_info:
                logger.warning(f"No subscription info found: {url}")
                return None

            info_dict = {}
            for item in subscription_info.split(";"):
                item = item.strip()
                if not item:
                    continue
                key, value = item.split("=")
                info_dict[key.strip()] = value.strip()

            def safe_int(value):
                try:
                    if value.lower() == 'infinity':
                        return 0
                    if not value:
                        return sys.maxsize
                    return Decimal(value)
                except ValueError:
                    logger.error(f"Failed to parse data: <{value}>")
                    return -1

            return SubInfo(
                url=url,
                upload=safe_int(info_dict.get("upload")),
                download=safe_int(info_dict.get("download")),
                total=safe_int(info_dict.get("total")),
                expireSec=safe_int(info_dict.get("expire"))
            )
    except Exception as e:
        logger.error(f"Failed to retrieve subscription info: {url}, error: {str(e)}")
        return None

async def filter_valid_urls_concurrently(urls: list[str]) -> list[str]:
    valid_urls = []
    connector = aiohttp.TCPConnector(limit=50, force_close=True)
    start_time = datetime.now()

    async with aiohttp.ClientSession(
        connector=connector,
        headers={"User-Agent": "clash.meta"}
    ) as session:
        tasks = [
            asyncio.create_task(
                get_subscription_info(session, url)
            )
            for url in urls
        ]
        now = datetime.now().timestamp()

        with tqdm(total=len(urls), desc="Filtering URLs") as pbar:
            for task in asyncio.as_completed(tasks):
                try:
                    info: SubInfo | None = await task
                    if not info:
                        continue

                    usage = info.download + info.upload
                    if info.total > 0 and usage >= info.total:
                        logger.warning(f"Subscription quota exhausted ({usage / (1024**3):.2f} GB) - {info.url}")
                        continue

                    if info.expireSec <= now:
                        logger.warning(f"Subscription expired - {info.url}")
                        continue

                    valid_urls.append(info.url)
                    logger.info(f"Valid URL: {info.url}")

                except asyncio.TimeoutError:
                    logger.warning("Request timed out")
                except Exception as e:
                    logger.error(f"Error processing URL: {str(e)}")
                finally:
                    pbar.update(1)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"URL filtering completed - Total: {len(urls)}, Successful: {len(valid_urls)}, Duration: {duration:.2f} seconds")
    return valid_urls

async def filter_valid_urls(urls: list[str]) -> list[str]:
    logger.info(f"Starting URL filtering, total: {len(urls)}")
    valid_urls = await filter_valid_urls_concurrently(urls)
    logger.info(f"Filtering finished, number of valid URLs: {len(valid_urls)}")
    return valid_urls

async def save_proxies_yml(valid_proxies):
    # Combine all valid URLs into a single proxy entry
    if not valid_proxies:
        logger.warning("No valid proxies to save.")
        return

    combined_urls = "\n".join(valid_proxies)

    proxies = [{
        "name": "Combined Proxy",
        "type": "combined",
        "server": "104.22.5.240",
        "port": 443,
        "network": "ws",
        "urls": combined_urls  # Includes all valid original URLs
    }]

    # Ensure the 'proxies' directory exists
    os.makedirs("proxies", exist_ok=True)

    # Save the file in the 'proxies' folder
    with open("proxies/proxies.yaml", "w", encoding="utf-8") as file:
        yaml.dump({"proxies": proxies}, file, allow_unicode=True)

    logger.info("File proxies.yaml successfully created with valid proxies.")

async def main():
    logger.info("Starting to load configuration file")
    # Additional configurations can be handled here if needed

    logger.info("Beginning to fetch remote subscription content")
    remote_url = "https://raw.githubusercontent.com/devojony/collectSub/refs/heads/main/sub/sub_all_clash.txt"
    content = await fetch_content(remote_url)
    proxy_providers = [p for p in content.split("\n") if p.strip()]
    logger.info(f"Initial number of URLs fetched: {len(proxy_providers)}")

    logger.info("Starting to filter valid URLs")
    valid_proxy_providers = await filter_valid_urls(proxy_providers)

    # Save valid proxies to file
    await save_proxies_yml(valid_proxy_providers)

if __name__ == "__main__":
    asyncio.run(main())
