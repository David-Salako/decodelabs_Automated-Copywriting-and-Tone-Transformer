"""
Bulk pipeline: reads a CSV of products and generates copy for all of them
concurrently, capped by a semaphore so we don't blow through rate limits.
Mirrors the "Semaphore Gate" + retry pattern from the project brief, without
requiring a separate batch-API service (Gemini's batch API works differently
from OpenAI's, so for this project size, bounded asyncio concurrency is the
practical equivalent).
"""

import asyncio
import csv
import random

from gemini_client import generate_copy_async
from schemas import BatchResult

MAX_CONCURRENT_REQUESTS = 5
MAX_RETRIES = 3


async def _generate_with_retry(row: dict, semaphore: asyncio.Semaphore) -> BatchResult:
    async with semaphore:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                result = await generate_copy_async(
                    product_name=row["product_name"],
                    description=row["description"],
                    tone=row["tone"],
                    platform=row["platform"],
                )
                return BatchResult(
                    product_name=row["product_name"],
                    platform=row["platform"],
                    tone=row["tone"],
                    result=result,
                )
            except Exception as exc:
                if attempt == MAX_RETRIES:
                    return BatchResult(
                        product_name=row["product_name"],
                        platform=row["platform"],
                        tone=row["tone"],
                        error=str(exc),
                    )
                # Exponential backoff with jitter before retrying.
                delay = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(delay)


async def run_batch(csv_path: str) -> list[BatchResult]:
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = []
        for raw_row in reader:
            row = {}
            for key, value in raw_row.items():
                if key is None:
                    continue
                normalized_key = key.lstrip("\ufeff").strip()
                row[normalized_key] = value.strip() if isinstance(value, str) else value
            rows.append(row)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    tasks = [_generate_with_retry(row, semaphore) for row in rows]
    return await asyncio.gather(*tasks)