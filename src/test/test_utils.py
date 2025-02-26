from twisted.internet import reactor, defer
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import clientFromString
from ldaptor.protocols import pureldap
from ldaptor.protocols.ldap.ldapserver import LDAPServer
from ldaptor.protocols.ldap import ldapsyntax
from ldaptor.protocols.ldap.ldapconnector import connectToLDAPEndpoint
from ldaptor.protocols.ldap.ldapclient import LDAPClient
from ldaptor.protocols.ldap.distinguishedname import DistinguishedName

### LDAP Client ###

class MockLDAPClient():
    """A base mock for a LDAP client."""
    def run(self, endpoint) -> Deferred:
        """Executes the query of this client."""
        pass

class BindingClient(MockLDAPClient):
    """A mock LDAP client that makes a bind request."""
    def __init__(self, dn: str, password: str):
        self.dn = dn
        self.password = password

    def bind(self, endpoint, dn, password):
        d = connectToLDAPEndpoint(reactor, endpoint, LDAPClient)

        def _doBind(proto):
            baseEntry = ldapsyntax.LDAPEntry(client=proto, dn=DistinguishedName(dn))
            x = baseEntry.bind(password=password)
            return x
        
        d.addCallback(_doBind)
        return d

    def run(self, endpoint) -> Deferred:
        d = self.bind(endpoint, self.dn, self.password)
        d.addErrback(defer.logError)
        return d

### LDAP Server ###

class MockLDAPServer(LDAPServer):
    """A base mock for a LDAP server. Needs to be extended with the wanted capabilities."""

class AcceptBind(MockLDAPServer):
    """A mock LDAP server that accepts all bind requests."""
    def handle_LDAPBindRequest(self, request, controls, reply):
        # Accept bind request
        return reply(pureldap.LDAPBindResponse(resultCode=0))
    
class RejectBind(MockLDAPServer):
    """A mock LDAP server that rejects all bind requests."""
    def handle_LDAPBindRequest(self, request, controls, reply):
        # Reject bind request (invalid credentials)
        return reply(pureldap.LDAPBindResponse(resultCode=49))
    
class TestUtils:
    """Utility module for testing multip[le servers and clients together."""

    def __init__(self):
        self.actions = Deferred()
        self._clients = []

    def addServer(self, port: int, server: type[MockLDAPServer]) -> None:
        """Adds a server to the reactor."""
        def _createServer(res):
            factory = Factory()
            factory.protocol = server
            reactor.listenTCP(port, factory)
            print(f"[{server.__name__}] Running on port {port}...")

        return self.actions.addCallback(_createServer)

    def addClient(self, port: int, client: MockLDAPClient) -> Deferred:
        """Adds a client to the reactor. Returns the Deferred of the client"""
        def _createClient(res, client_index):
            d = client.run(f"tcp:localhost:{port}")
            d.addCallback(lambda _: print(f"[{client.__class__.__name__}] Client requesting to port {port}"))
            d.chainDeferred(self._clients[client_index])
            return d

        # empty deferred, for accumulating callbacks
        self._clients.append(Deferred())
        index = len(self._clients) - 1

        self.actions.addCallback(_createClient, index)
        return self._clients[index]

    def addTimeout(self, seconds: float) -> None:
        """Adds a timeout (in seconds) for execution"""
        self.actions.addTimeout(seconds)
        self.actions.addCallback(lambda _: print(f"(Timeout set to {seconds} sec)"))

    def then(self, callback) -> None:
        """Executes a callback after all the previous ones are completed"""
        self.actions.addCallback(callback)
    
    def catch(self, errback) -> None:
        """Catches an error, and executes the errback function"""
        self.actions.addErrback(errback)

    def run(self) -> None:
        """Starts the test"""
        reactor.callLater(1, self.actions.callback, None)
        reactor.run()

    def stop(self, ignored=None) -> None:
        """Stops the test"""
        reactor.stop()

if __name__ == "__main__":
    # Testing the testing framework
    test = TestUtils()
    test.addServer(port=3890, server=AcceptBind)
    test.addServer(port=3891, server=RejectBind)
    c = test.addClient(port=3890, client=BindingClient('cn=admin,dc=example,dc=org', 'password'))
    c.addCallback(lambda _: print("Binded successfully!"))
    c.addErrback(lambda _: print("Error while binding!"))
    c.addBoth(test.stop)
    test.run()