from abc import ABC, abstractmethod
import asyncio
from threading import Thread
from typing import List, Optional
import socket
from time import sleep

from zeroconf import IPVersion
from zeroconf.asyncio import AsyncServiceInfo, AsyncZeroconf

class NodeDiscovery(ABC):
    @abstractmethod
    def get_other_nodes(self):
        pass

class MDNSDiscovery(NodeDiscovery):
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

    def __init__(self):
        self.nodes = []
        t = Thread(target=self.launch_advertisements)
        t.run() 
        #launch_browser() # update self.nodes
        
    def get_other_nodes(self):
        return self.nodes
    
    def launch_advertisements(self):
        ip_version = IPVersion.V4Only

        infos = [AsyncServiceInfo(
                    "_ldapproxy._tcp.local.",
                    "ProxyA._ldapproxy._tcp.local.",
                    addresses=[socket.inet_aton("127.0.0.1")],
                    port=10389,
                    #server=f"zcdemohost-.local.",
                )]

        loop = asyncio.get_event_loop()
        runner = MDNSDiscovery.AsyncRunner(ip_version)
        try:
            loop.run_until_complete(runner.register_services(infos))
        except:
            loop.run_until_complete(runner.unregister_services(infos))

class DNSDiscovery(NodeDiscovery):
    def __init__(self, dns_address):
        self.address = dns_address
    def get_other_nodes():
        return [] # in facts, you have to query the 
    


if __name__ == '__main__':
    MDNSDiscovery()
    while True:
        sleep(60)