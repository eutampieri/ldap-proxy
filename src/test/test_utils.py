from twisted.internet import reactor, defer
from twisted.internet.protocol import Factory
from twisted.internet.task import react
from twisted.internet.endpoints import clientFromString
from ldaptor.protocols import pureldap
from ldaptor.protocols.ldap.ldapserver import LDAPServer
from ldaptor.protocols.ldap import ldapsyntax
from ldaptor.protocols.ldap.ldapconnector import connectToLDAPEndpoint
from ldaptor.protocols.ldap.ldapclient import LDAPClient
from ldaptor.protocols.ldap.distinguishedname import DistinguishedName

### LDAP Server ###

class MockLDAPServer(LDAPServer):
    """A base mock for a LDAP server. Needs to be extended with the wanted capabilities."""
    def run(port: int):
        factory = Factory()
        factory.protocol = MockLDAPServer

        reactor.listenTCP(port, factory)
        print(f"[Mock LDAP Server] Running on port {port}...")
        reactor.run()
        print(f"[Mock LDAP Server] Stopped.")

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
    