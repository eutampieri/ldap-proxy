import ldaptor.protocols.pureldap
from ldaptor.protocols.pureldap import LDAPBindRequest
from twisted.internet import protocol, defer, reactor
from ldaptor.config import LDAPConfig
from ldaptor.protocols.ldap.merger import MergedLDAPServer
from proxy.proxydatabase import ProxyDatabase, ServerEntry, UserEntry
from ldaptor.protocols import pureldap

class ProxyMerger(MergedLDAPServer):
    def __init__(self, database: ProxyDatabase):
        self.database = database
        configs = database.get_servers()
        c = [self._ldap_config_from_db_entry(i) for i in configs]
        self.credentials = [i[1] for i in c]
        super().__init__([i[0] for i in c], [c.tls for c in configs])

    def handle_LDAPBindRequest(self, request, controls, reply):
        # return self._whenConnected(self._handle_LDAPBindRequest, request, controls, reply)
        auth_client = self.authenticate_client(request.dn.decode("utf-8"), request.auth.decode("utf-8"))
        if auth_client is None:
            # Invalid credentials
            res = pureldap.LDAPBindResponse(resultCode=49)
            reply(res)
            return defer.succeed(res)
        else:
            return super().handle_LDAPBindRequest(request, controls, reply)

    # def _handle_LDAPBindRequest(self, request: LDAPBindRequest, controls, reply):
    #     # authenticate user
    #     auth_client = self.authenticate_client(request.dn.decode("utf-8"), request.auth.decode("utf-8"))
    #     if auth_client is None:
    #         invalid_credentials_result_code=49
    #         print('Invalid credentials')
    #         return reply(pureldap.LDAPBindResponse(resultCode=invalid_credentials_result_code))

    #     else:
    #         for client, creds in zip(self.clients, self.credentials):
    #             ldap_bind_request = LDAPBindRequest(version=3, dn=creds[0], auth=creds[1])
    #             d = client.send_multiResponse(ldap_bind_request, self._gotResponse, reply)
    #             d.addErrback(defer.logError)
    #     return defer.succeed(request)

    # def add_server(self, server: ServerEntry):
    #    c = self._ldap_config_from_db_entry(server)
    #    self.configs.append(c[0])
    #    self.credentials.append(c[1])

    def _ldap_config_from_db_entry(self, config: ServerEntry):
        return (
            LDAPConfig(serviceLocationOverrides={"": (config.ip, config.port)}),
            (config.bind_dn, config.bind_password)
        )

    # authenticate a user. Return None if not authorized
    def authenticate_client(self, dn, auth):
        return self.database.get_authenticated_client(dn, auth)