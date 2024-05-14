#!/usr/bin/env python3
"""Example of announcing 250 services (in this case, a fake HTTP server)."""

import asyncio
import logging
import socket
from typing import List, Optional

from zeroconf import IPVersion
from zeroconf.asyncio import AsyncServiceInfo, AsyncZeroconf


class AsyncRunner:
    def __init__(self, ip_version: IPVersion) -> None:
        self.ip_version = ip_version
        self.aiozc: Optional[AsyncZeroconf] = None

    async def register_services(self, infos: List[AsyncServiceInfo]) -> None:
        self.aiozc = AsyncZeroconf(ip_version=self.ip_version)
        tasks = [self.aiozc.async_register_service(info) for info in infos]
        background_tasks = await asyncio.gather(*tasks)
        await asyncio.gather(*background_tasks)
        #print("Finished registration, press Ctrl-C to exit...")
        while True:
            await asyncio.sleep(1)

    async def unregister_services(self, infos: List[AsyncServiceInfo]) -> None:
        assert self.aiozc is not None
        tasks = [self.aiozc.async_unregister_service(info) for info in infos]
        background_tasks = await asyncio.gather(*tasks)
        await asyncio.gather(*background_tasks)
        await self.aiozc.async_close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)


    ip_version = IPVersion.All

    infos = [AsyncServiceInfo(
                "_http._tcp.local.",
                "Paul's Test Web Site._http._tcp.local.",
                addresses=[socket.inet_aton("127.0.0.1")],
                port=80,
                properties={'path': '/~paulsm/'},
                server=f"zcdemohost-.local.",
            )]

    loop = asyncio.get_event_loop()
    runner = AsyncRunner(ip_version)
    try:
        loop.run_until_complete(runner.register_services(infos))
    except KeyboardInterrupt:
        loop.run_until_complete(runner.unregister_services(infos))