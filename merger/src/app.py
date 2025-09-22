from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.python import log
from proxy.merger import ProxyMerger
from proxy.proxydatabase import ProxyDatabase
import sys
import os

if __name__ == '__main__':
    # set port
    PROXY_PORT = int(os.getenv("PROXY_PORT", 10636))

    # create the database
    CONNECTION_URI = os.getenv("DB_URI", "mongodb://127.0.0.1:27017")
    db = ProxyDatabase(CONNECTION_URI)
    # configs = [
    #     ServerEntry(ip="192.168.1.2", port=389, bind_dn="", bind_password="dc", base_dn=""),
    #     ServerEntry(ip="192.168.1.189", port=389, bind_dn="", bind_password="dc-temp", base_dn="")
    # ]
    build = lambda: ProxyMerger(db)

    # start logging service
    log.startLogging(sys.stdout)
    # create factory
    factory = Factory()
    factory.protocol = build
    # setup the server
    reactor.listenTCP(PROXY_PORT, factory)
    log.msg(f"[LdapProxyMerger] Running on port {PROXY_PORT}...")
    # start the server
    reactor.run()