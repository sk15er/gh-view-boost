import asyncio
import aiohttp
import time
from typing import Optional

URL = "https://camo.githubusercontent.com/1a39401eaf969c4543ecb6794b6057ee83376bccd82905a81f269a23a1e59dd7/68747470733a2f2f6b6f6d617265762e636f6d2f67687076632f3f757365726e616d653d736b31356572"

TOTAL_REQUESTS = 10_000
MAX_CONCURRENCY = 500          # Tune this (300-800 works well)
TIMEOUT = 10


async def single_request(session: aiohttp.ClientSession, request_id: int) -> bool:
    """Ultra-light request - no body reading"""
    try:
        async with session.get(URL, timeout=TIMEOUT) as resp:
            # Just ensure the request completed
            await resp.release()          # Important: release connection quickly
            return resp.status == 200
    except Exception:
        return False


async def main():
    connector = aiohttp.TCPConnector(
        limit=MAX_CONCURRENCY * 2,
        limit_per_host=MAX_CONCURRENCY,
        ttl_dns_cache=300,
        keepalive_timeout=30,
    )

    timeout = aiohttp.ClientTimeout(total=TIMEOUT)

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers={"User-Agent": "Mozilla/5.0 (compatible; ViewBooster/1.0)"}
    ) as session:

        print(f"Starting {TOTAL_REQUESTS:,} requests (concurrency: {MAX_CONCURRENCY})...\n")

        start_time = time.perf_counter()

        # Create all tasks
        tasks = [
            single_request(session, i) 
            for i in range(TOTAL_REQUESTS)
        ]

        # Run them with concurrency limit
        results = await asyncio.gather(*tasks, return_exceptions=True)

        duration = time.perf_counter() - start_time
        success = sum(1 for r in results if r is True)
        rps = TOTAL_REQUESTS / duration

        print("="*50)
        print("RESULTS")
        print("="*50)
        print(f"Total requests : {TOTAL_REQUESTS:,}")
        print(f"Successful     : {success:,}")
        print(f"Failed         : {TOTAL_REQUESTS - success:,}")
        print(f"Total time     : {duration:.2f} seconds")
        print(f"Requests/sec   : {rps:,.0f}")
        print(f"Target 1k/s    : {'✅ ACHIEVED' if rps >= 1000 else '❌ Not reached'}")
        print("="*50)


if __name__ == "__main__":
    asyncio.run(main())
