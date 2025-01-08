#! /usr/bin/env python3
from ldaptor.protocols.pureldap import LDAPBindRequest
from twisted.internet import protocol, defer, reactor
from ldaptor.config import LDAPConfig
from ldaptor.protocols.ldap.merger import MergedLDAPServer
from proxydatabase import LdapProxyDatabase, ServerEntry, UserEntry

class ProxyMerger(MergedLDAPServer):
    def __init__(self, database: LdapProxyDatabase):
        configs = database.get_servers()
        c = [self._ldap_config_from_db_entry(i) for i in configs]
        self.credentials = [i[1] for i in c]
        super().__init__([i[0] for i in c], [c.tls for c in configs])

    def handle_LDAPBindRequest(self, request, controls, reply):
        self._whenConnected(self._handle_LDAPBindRequest, request, controls, reply)
    def _handle_LDAPBindRequest(self, request: LDAPBindRequest, controls, reply):
        # authenticate user
        auth_user = self.authenticate_user(request.dn, request.auth)
        if auth_user is None:
            raise Exception("User not authorized")
            
        for client, creds in zip(self.clients, self.credentials):
            ldap_bind_request = LDAPBindRequest(version=3, dn=creds[0], auth=creds[1])
            d = client.send_multiResponse(ldap_bind_request, self._gotResponse, reply)
            d.addErrback(defer.logError)
        return defer.succeed(request)

    #def add_server(self, server: ServerEntry):
    #    c = self._ldap_config_from_db_entry(server)
    #    self.configs.append(c[0])
    #    self.credentials.append(c[1])

    def _ldap_config_from_db_entry(self, config: ServerEntry):
        return (
            LDAPConfig(serviceLocationOverrides={"": (config.ip, config.port)}),
            (config.bind_dn, config.bind_password)
        )
    
    # authenticate a user. Return None if not authorized
    def authenticate_user(self, dn, auth):
        users = self.database.get_users()
        for u in users:
            if u["user"] == dn and u["password"] == auth:
                return UserEntry(dn, auth, u["is_admin"])
        return None

if __name__ == '__main__':
    factory = protocol.ServerFactory()

    def buildProtocol():
        db = LdapProxyDatabase("127.0.0.1", "27017")
        # configs = [
        #     ServerEntry(ip="192.168.1.2", port=389, bind_dn="", bind_password="dc", base_dn=""),
        #     ServerEntry(ip="192.168.1.189", port=389, bind_dn="", bind_password="dc-temp", base_dn="")
        # ]
        return ProxyMerger(db)

    factory.protocol = buildProtocol
    reactor.listenTCP(3389, factory)
    print("Starting")
    reactor.run()