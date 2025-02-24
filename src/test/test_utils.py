from twisted.internet import reactor, defer
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
    def run(self, endpoint):
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

    def run(self, endpoint):
        d = self.bind(endpoint, self.dn, self.password)
        d.addCallback(lambda _: print("Successful binding!"))
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

    def addServer(self, port: int, protocol: type[MockLDAPServer]):
        """Adds a server to the reactor."""
        factory = Factory()
        factory.protocol = protocol
        reactor.listenTCP(port, factory)
        print(f"[{protocol.__name__}] Running on port {port}...")

    def addClient(self, port: int, client: MockLDAPClient):
        """Adds a client to the reactor"""
        d = client.run(f"tcp:localhost:{port}")
        print(f"[{client.__class__.__name__}] Client requesting to port {port}")
        return d

    def run(self):
        reactor.run()

    def stop(self, ignored=None):
        reactor.stop()

if __name__ == "__main__":
    test = TestUtils()
    test.addServer(3890, AcceptBind)
    test.addServer(3891, RejectBind)
    test.addClient(3890, BindingClient('cn=admin,dc=example,dc=org', 'password')).addBoth(test.stop)
    test.run()