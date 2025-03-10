import unittest
import twisted.internet
from twisted.trial import unittest as twistedtest
from test.mocks import *
from test_utils import TestEnvironment
from proxy.merger import ProxyMerger
from twisted.internet.protocol import Factory

### Tests for the LDAP proxy merger ###

# 1. Bind: the client should bind if he's registered to the proxy
# 2. Search: the search should be done on all the server
# 3. Consistency over Availability
# 4. Read-only proxy: only queries should be allowed
# 5. Database error handling

class TestProxyMerger(twistedtest.TestCase):

    def startServer(self, port: int, server: type[MockLDAPServer]):
        factory = Factory()
        factory.protocol = server
        listening_port = reactor.listenTCP(port, factory)
        self.addCleanup(listening_port.stopListening)
        return listening_port

    def startClient(self, port: int, client: MockLDAPClient) -> Deferred:
        d = client.run("localhost", port)
        self.addCleanup(client.close)
        return d

    def tearDown(self):
        for call in reactor.getDelayedCalls():
            if call.active():
                call.cancel()

    def test_registered_client_should_bind(self):
        # config
        client = ClientEntry('cn=client,dc=example,dc=org', 'clientpassword')
        servers = [
            ServerEntry('127.0.0.1', 3890, 'dc=example,dc=org', 'cn=proxy,dc=example,dc=org', 'proxypassword'),
            ServerEntry('127.0.0.1', 3891, 'dc=example,dc=org', 'cn=proxy,dc=example,dc=org', 'proxypassword')
        ]

        # start server
        for s in servers:
            self.startServer(port=s.port, server=AcceptBind)

        # start proxy
        proxy = lambda: ProxyMerger(OneClientDatabase(client, servers))
        self.startServer(port=10389, server=proxy)

        # start client
        clientDef = self.startClient(port=10389, client=BindingClient(client.dn, client.password))
        clientDef.addErrback(self.fail)

        # wait completion
        return clientDef

    # def test_unregistered_client_should_not_bind(self):
    #     pass
    # def test_bind_should_fail_when_one_server_is_unavailable(self):
    #     pass
    # def test_search_should_be_executed_on_all_servers(self):
    #     pass
    # def test_search_should_fail_when_one_server_is_unavailable(self):
    #     pass
    # def test_only_read_operations_should_be_allowed(self):
    #     pass
    # def test_request_should_fail_when_database_is_unavailable(self):
    #     pass

if __name__ == '__main__':
    unittest.main()