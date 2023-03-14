"""AIO Helper functions"""

import asyncio


async def gather_with_concurrency(concurrency: int, *tasks):
    """async gather with max concurrency"""
    semaphore = asyncio.Semaphore(concurrency)

    async def sem_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))
