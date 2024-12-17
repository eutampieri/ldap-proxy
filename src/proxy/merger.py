#! /usr/bin/env python3
from ldaptor.protocols.pureldap import LDAPBindRequest
from twisted.internet import protocol, defer, reactor
from ldaptor.config import LDAPConfig
from ldaptor.protocols.ldap.merger import MergedLDAPServer
from proxydatabase import ServerEntry

class ProxyMerger(MergedLDAPServer):
    def __init__(self, configs: [ServerEntry], use_tls):
        c = [self._ldap_config_from_db_entry(i) for i in configs]
        self.credentials = [i[1] for i in c]
        super().__init__([i[0] for i in c], use_tls)

    def handle_LDAPBindRequest(self, request, controls, reply):
        # TODO check if credentials are valid
        print()
        for client, creds in zip(self.clients, self.credentials):
            ldap_bind_request = LDAPBindRequest(version=3, dn=creds[0], auth=creds[1])
            d = client.send_multiResponse(ldap_bind_request, self._gotResponse, reply)
            d.addErrback(defer.logError)
        return defer.succeed(request)

    def add_server(self, server: ServerEntry):
        c = self._ldap_config_from_db_entry(server)
        self.configs.append(c[0])
        self.credentials.append(c[1])

    def _ldap_config_from_db_entry(self, config: ServerEntry):
        return (
            LDAPConfig(serviceLocationOverrides={"": (config.ip, config.port)}),
            (config.bind_dn, config.bind_password))

if __name__ == '__main__':
    factory = protocol.ServerFactory()

    def buildProtocol():
        configs = [ServerEntry(ip="192.168.1.2", port=389, bind_dn="", bind_password="", base_dn="")]
        use_tls = [False]
        return ProxyMerger(configs, use_tls)

    factory.protocol = buildProtocol
    reactor.listenTCP(3389, factory)
    reactor.run()