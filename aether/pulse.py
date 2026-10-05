"""PULSE - Async runtime: scheduler, channels, actors."""
from __future__ import annotations
import asyncio
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable


class Channel:
    def __init__(self, maxsize=0):
        self._q = asyncio.Queue(maxsize=maxsize)

    async def send(self, item):
        await self._q.put(item)

    async def recv(self):
        return await self._q.get()

    def qsize(self):
        return self._q.qsize()

    def empty(self):
        return self._q.empty()


@dataclass
class Actor:
    name: str
    handler: Callable[[Any], Awaitable[Any]]
    inbox: Channel = field(default_factory=Channel)
    _task: Any = None

    async def _loop(self):
        while True:
            msg = await self.inbox.recv()
            if msg is None:
                break
            try:
                await self.handler(msg)
            except Exception:
                pass

    def start(self):
        self._task = asyncio.create_task(self._loop())

    async def stop(self):
        await self.inbox.send(None)
        if self._task:
            await self._task


class Runtime:
    def __init__(self, workers=4):
        self.workers = workers
        self._actors = {}
        self._queue = asyncio.Queue()

    def actor(self, name, handler):
        a = Actor(name=name, handler=handler)
        self._actors[name] = a
        a.start()
        return a

    async def submit(self, coro):
        return await coro

    async def gather(self, coros):
        return await asyncio.gather(*coros)

    async def stop_all(self):
        for a in self._actors.values():
            await a.stop()

    def names(self):
        return list(self._actors.keys())
