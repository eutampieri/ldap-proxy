from test.mocks import *
from test_utils import TestEnvironment
from proxy.merger import ProxyMerger

### Tests for the LDAP proxy merger ###

# 1. Bind: the client should bind if he's registered to the proxy
# 2. Search: the search should be done on all the server
# 3. Consistency over Availability
# 4. Read-only proxy: only queries should be allowed
# 5. Database error handling

class TestProxyMerger(unittest.TestCase):

    def test_registered_client_should_bind(self):
        # configs
        client = ClientEntry('cn=client,dc=example,dc=org', 'clientpassword')
        servers = [
            ServerEntry('127.0.0.1', 3890, 'dc=example,dc=org', 'cn=proxy,dc=example,dc=org', 'proxypassword'),
            ServerEntry('127.0.0.1', 3891, 'dc=example,dc=org', 'cn=proxy,dc=example,dc=org', 'proxypassword')
        ]
        # create servers
        test = TestEnvironment()
        for s in servers:
            test.addServer(port=s.port, server=AcceptBind)
        # create proxy
        proxy = lambda: ProxyMerger(OneClientDatabase(client, servers))
        test.addServer(port=10389, server=proxy)
        # create client
        d = test.addClient(port=10389, client=BindingClient(client.dn, client.password))
        d.addCallbacks(lambda _: print('Binded correctly!'), lambda _: print('Error while binding!'))
        d.addBoth(test.stop)

        test.addTimeout(2)
        self.assertTrue(test.run())

    def test_unregistered_client_should_not_bind(self):
        # configs
        client = ClientEntry('cn=client,dc=example,dc=org', 'clientpassword')
        servers = [
            ServerEntry('127.0.0.1', 3890, 'dc=example,dc=org', 'cn=proxy,dc=example,dc=org', 'proxypassword'),
            ServerEntry('127.0.0.1', 3891, 'dc=example,dc=org', 'cn=proxy,dc=example,dc=org', 'proxypassword')
        ]
        # create servers
        test = TestEnvironment()
        for s in servers:
            test.addServer(port=s.port, server=AcceptBind)
        # create proxy
        proxy = lambda: ProxyMerger(OneClientDatabase(client, servers))
        test.addServer(port=10389, server=proxy)
        # create client
        d = test.addClient(port=10389, client=BindingClient('wrong', 'credentials'))
        d.addCallbacks(lambda _: print('Binded correctly!'), lambda _: print('Error while binding!'))
        d.addBoth(test.stop)

        test.addTimeout(2)
        self.assertFalse(test.run())

    def test_bind_should_fail_when_one_server_is_unavailable(self):
        # configs
        client = ClientEntry('cn=client,dc=example,dc=org', 'clientpassword')
        servers = [
            ServerEntry('127.0.0.1', 3892, 'dc=example,dc=org', 'cn=proxy,dc=example,dc=org', 'proxypassword'),
            ServerEntry('127.0.0.1', 3893, 'dc=example,dc=org', 'cn=proxy,dc=example,dc=org', 'proxypassword')
        ]
        # create servers
        tost = TestEnvironment()
        tost.addServer(port=3892, server=AcceptBind)
        tost.addServer(port=3893, server=UnresponsiveBind)
        # create proxy
        proxy = lambda: ProxyMerger(OneClientDatabase(client, servers))
        tost.addServer(port=10389, server=proxy)
        # create client
        d = tost.addClient(port=10389, client=BindingClient(client.dn, client.password))
        d.addBoth(tost.stop)

        tost.addTimeout(2)
        self.assertFalse(tost.run())

    # def test_search_should_be_executed_on_all_servers(self):
    #     pass
    # def test_search_should_fail_when_one_server_is_unavailable(self):
    #     pass
    # def test_only_read_operations_should_be_allowed(self):
    #     pass
    # def test_request_should_fail_when_database_is_unavailable(self):
    #     pass

if __name__ == '__main__':
