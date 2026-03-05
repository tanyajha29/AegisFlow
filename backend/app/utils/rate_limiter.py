import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import HTTPException, Request, status


class SimpleRateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._store: Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))

    def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "anonymous"
        window_start, count = self._store[client_ip]
        now = time.time()

        if now - window_start > self.window_seconds:
            window_start, count = now, 0

        count += 1
        self._store[client_ip] = (window_start, count)

        if count > self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please slow down.",
            )


rate_limiter = SimpleRateLimiter(max_requests=120, window_seconds=60)

