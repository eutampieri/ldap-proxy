import unittest
import twisted.internet.error
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
        """Start a server. Automagically cleanup the server on test end."""
        factory = Factory()
        factory.protocol = server
        listening_port = reactor.listenTCP(port, factory)
        self.addCleanup(listening_port.stopListening)
        return listening_port

    def startClient(self, port: int, client: MockLDAPClient) -> Deferred:
        """Start a client. Automagically cleanup the client on test end."""
        d = client.run("localhost", port)
        self.addCleanup(client.close)
        return d

    def tearDown(self):
        self.flushLoggedErrors(twisted.internet.error.ConnectionDone) # ignore the connection closed error
        for call in reactor.getDelayedCalls():
            if call.active():
                call.cancel()

    def succeed(self, ignored=None):
        """Shorthand for succeeding a test."""
        self.successResultOf(defer.succeed(True))

    ### TESTS ###

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
        clientDef.addCallback(self.succeed)

        # wait completion
        return clientDef

    def test_unregistered_client_should_not_bind(self):
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
        clientDef = self.startClient(port=10389, client=BindingClient('cn=worng,dc=example,dc=org', 'wrongpassword'))
        clientDef.addTimeout(2, reactor, onTimeoutCancel=lambda a, b: self.fail()) # timeout should not kick
        clientDef.addCallback(self.fail) # should throw an error
        clientDef.addErrback(self.succeed)

        # wait completion
        return clientDef

    def test_bind_should_fail_when_one_server_is_unavailable(self):
        # config
        client = ClientEntry('cn=client,dc=example,dc=org', 'clientpassword')
        servers = [
            ServerEntry('127.0.0.1', 3890, 'dc=example,dc=org', 'cn=proxy,dc=example,dc=org', 'proxypassword'),
            ServerEntry('127.0.0.1', 3891, 'dc=example,dc=org', 'cn=proxy,dc=example,dc=org', 'proxypassword')
        ]

        # start server
        self.startServer(port=3890, server=AcceptBind)
        self.startServer(port=3891, server=UnresponsiveBind)

        # start proxy
        proxy = lambda: ProxyMerger(OneClientDatabase(client, servers))
        self.startServer(port=10389, server=proxy)

        # start client
        clientDef = self.startClient(port=10389, client=BindingClient(client.dn, client.password))
        def timeoutCallback(err, val):
            self.succeed()
        clientDef.addBoth(self.fail) # should not reach this point
        clientDef.addTimeout(2, reactor, onTimeoutCancel=timeoutCallback) # timeout should kick

        # wait completion
        return clientDef

    def test_search_should_be_executed_on_all_servers(self):
        # config
        client = ClientEntry('cn=client,dc=example,dc=org', 'clientpassword')
        servers = [
            ServerEntry('127.0.0.1', 3890, 'dc=example,dc=org', 'cn=proxy,dc=example,dc=org', 'proxypassword'),
            ServerEntry('127.0.0.1', 3891, 'dc=example,dc=org', 'cn=proxy,dc=example,dc=org', 'proxypassword')
        ]

        # start server
        for s in servers:
            self.startServer(port=s.port, server=SimpleSearch)

        # start proxy
        proxy = lambda: ProxyMerger(OneClientDatabase(client, servers))
        self.startServer(port=10389, server=proxy)

        # start client
        clientDef = self.startClient(port=10389, client=SearchingClient('dc=example,dc=org', filter='(objectClass=*)'))
        clientDef.addErrback(self.fail)

        def check_result(result):
            self.assertEqual(len(result), 2) # expecting two entries
            entry = result[0]
            self.assertEqual(list(entry.get("cn")), [b"Bob"])
            self.assertEqual(list(entry.get("sn")), [b"Bobby"])
            self.assertEqual(list(entry.get("mail")), [b"bob@example.com"])

        # wait completion
        return clientDef.addCallback(check_result)
    
    # def test_search_should_fail_when_one_server_is_unavailable(self):
    #     pass
    # def test_only_read_operations_should_be_allowed(self):
    #     pass
    # def test_request_should_fail_when_database_is_unavailable(self):
    #     pass

if __name__ == '__main__':
    unittest.main()