import asyncio
import time
import random
import httpx
from src.app.core.logger import get_logger

_logger = get_logger("[PythonSidecar - System State]")

class SystemState:
    def __init__(self):
        self._active_requests_count: int = 0
        self._active_background_tasks: int = 0
        self._lock = asyncio.Lock()

    @property
    def total_active_work(self) -> int:
        return self._active_requests_count + self._active_background_tasks

    async def increment_active_requests(self) -> int:
        async with self._lock:
            self._active_requests_count += 1
            return self._active_requests_count

    async def decrement_active_requests(self) -> int:
        async with self._lock:
            self._active_requests_count = max(0, self._active_requests_count - 1)
            return self._active_requests_count

    async def increment_background_tasks(self) -> int:
        async with self._lock:
            self._active_background_tasks += 1
            return self._active_background_tasks

    async def decrement_background_tasks(self) -> int:
        async with self._lock:
            self._active_background_tasks = max(0, self._active_background_tasks - 1)
            return self._active_background_tasks

class ArxivAPIState:
    def __init__(self, user_agents: list[str], max_wait_time_seconds: float,
                 http_timeout_seconds: float = 30.0, http_max_connections: int = 10,
                 http_max_keepalive_connections: int = 5):
        self.last_request_time = 0.0
        self._lock = asyncio.Lock()
        self.http_client: httpx.AsyncClient | None = None
        self.user_agent = random.choice(user_agents)
        self.max_wait_time_seconds = max_wait_time_seconds
        self.http_timeout_seconds = http_timeout_seconds
        self.http_max_connections = http_max_connections
        self.http_max_keepalive_connections = http_max_keepalive_connections

    async def init_client(self):
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Connection": "keep-alive"
        }
        self.http_client = httpx.AsyncClient(
            headers=headers, timeout=self.http_timeout_seconds, follow_redirects=True,
            limits=httpx.Limits(max_connections=self.http_max_connections, max_keepalive_connections=self.http_max_keepalive_connections)
        )

    async def close_client(self):
        if self.http_client:
            await self.http_client.aclose()

    async def wait_for_arxiv(self):
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_request_time
            wait_time = max(0, self.max_wait_time_seconds - elapsed)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self.last_request_time = time.time()