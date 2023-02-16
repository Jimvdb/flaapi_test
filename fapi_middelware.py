import asyncio
from fastapi import FastAPI, Request, HTTPException
from collections import deque
from datetime import datetime, timedelta
from typing import Optional
import uvicorn

app = FastAPI()


class RateLimitMiddleware:
    def __init__(self, app, limit=100, per=timedelta(minutes=1), block_for=timedelta(minutes=5),
                 watchdog_interval=timedelta(minutes=5)):
        self.app = app
        self.limit = limit
        self.per = per
        self.block_for = block_for
        self.watchdog_interval = watchdog_interval
        self.requests = {}
        self.blocked_ips = set()

    async def __call__(self, scope, receive, send):
        print("call")
        now = datetime.now()
        request = Request(scope, receive)
        remote_addr = request.client.host
        if remote_addr in self.blocked_ips:
            raise HTTPException(status_code=403, detail="Access Denied - IP Blocked")
        self.cleanup_requests(now)
        if len(self.requests.get(remote_addr, [])) > self.limit:
            self.blocked_ips.add(remote_addr)
            raise HTTPException(status_code=429, detail="Too Many Requests - IP Blocked")
        self.requests.setdefault(remote_addr, deque()).append(now)
        response = await self.app(scope, receive, send)
        return response

    def cleanup_requests(self, now):
        print("clean")
        for ip, requests in list(self.requests.items()):
            while requests and requests[0] < now - self.per:
                requests.popleft()
            if not requests:
                del self.requests[ip]
            elif len(requests) > self.limit:
                self.blocked_ips.add(ip)
                del self.requests[ip]
                return
        asyncio.create_task(self.watchdog(now))

    async def watchdog(self, now):
        print("Bark")
        for ip, requests in list(self.requests.items()):
            if len(requests) > self.limit:
                self.blocked_ips.add(ip)
                del self.requests[ip]
        await asyncio.sleep(self.watchdog_interval.total_seconds())


app.add_middleware(RateLimitMiddleware, limit=100, per=timedelta(minutes=1), block_for=timedelta(minutes=5),
                   watchdog_interval=timedelta(minutes=5))


@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
