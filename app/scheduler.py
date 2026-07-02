import asyncio
import contextlib

from app.config import Settings
from app import logger


async def _heartbeat_loop(settings: Settings) -> None:
    while True:
        logger.info("heartbeat", "agent service heartbeat")
        await asyncio.sleep(settings.heartbeat_interval_ms / 1000)


def start_scheduler(settings: Settings) -> asyncio.Task:
    return asyncio.create_task(_heartbeat_loop(settings))


async def stop_scheduler(task: asyncio.Task | None) -> None:
    if task is None:
        return
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task
