python
import httpx
import asyncio
import time

# ========================= CONFIG =========================
URL = "https://camo.githubusercontent.com/1a39401eaf969c4543ecb6794b6057ee83376bccd82905a81f269a23a1e59dd7/68747470733a2f2f6b6f6d617265762e636f6d2f67687076632f3f757365726e616d653d736b31356572"

TOTAL_REQUESTS = 10_000
MAX_CONCURRENCY = 600          # Tune this value
# ========================================================

async def single_request(client: httpx.AsyncClient, request_id: int):
    """Minimal request - no body reading"""
    try:
        resp = await client.get(URL)
        await resp.aclose()        # Release connection immediately
        return True
    except Exception:
        return False


async def main():
    limits = httpx.Limits(
        max_connections=MAX_CONCURRENCY * 2,
        max_keepalive_connections=MAX_CONCURRENCY,
        keepalive_expiry=30
    )

    async with httpx.AsyncClient(
        limits=limits,
        timeout=15.0,
        http2=True,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; ViewBooster/1.0)"
        }
    ) as client:

        print(f"🚀 Starting {TOTAL_REQUESTS:,} requests with {MAX_CONCURRENCY} concurrency...\n")

        start_time = time.perf_counter()

        # Create all tasks
        tasks = [single_request(client, i) for i in range(TOTAL_REQUESTS)]

        # Execute with high concurrency
        results = await asyncio.gather(*tasks, return_exceptions=True)

        duration = time.perf_counter() - start_time
        success = sum(1 for r in results if r is True)
        rps = TOTAL_REQUESTS / duration

        print("=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Total Requests   : {TOTAL_REQUESTS:,}")
        print(f"Successful       : {success:,}")
        print(f"Failed           : {TOTAL_REQUESTS - success:,}")
        print(f"Total Time       : {duration:.2f} seconds")
        print(f"Requests/sec     : {rps:,.0f}")
        print(f"Target 1k+/sec   : {'✅ ACHIEVED' if rps >= 1000 else '❌ Not reached yet'}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
