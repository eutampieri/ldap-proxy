from twisted.internet import reactor, defer, error
from twisted.internet.defer import Deferred
from ldaptor.protocols import pureldap
from ldaptor.protocols.ldap.ldapserver import LDAPServer
from ldaptor.protocols.ldap import ldapsyntax
from ldaptor.protocols.ldap.ldapconnector import connectToLDAPEndpoint
from ldaptor.protocols.ldap.ldapclient import LDAPClient
from ldaptor.protocols.ldap.distinguishedname import DistinguishedName
from proxy.proxydatabase import ClientEntry, ServerEntry

### LDAP Client ###

class MockLDAPClient():
    """A base mock for a LDAP client."""
    def __init__(self):
        self.conn = None

    def close(self) -> None:
        """Close the client connection."""
        self.conn.loseConnection()

    def connectToEndpoint(self, host: str, port: int) -> Deferred[LDAPClient]:
        return connectToLDAPEndpoint(reactor, f"tcp:{host}:{port}", LDAPClient)

    def run(self, host: str, port: int) -> Deferred:
        """Executes the query of this client."""
        d = self.connectToEndpoint(host, port)
        def _setConnection(proto):
            self.conn = proto.transport
            return proto
        d.addCallbacks(_setConnection, print)
        return d

class BindingClient(MockLDAPClient):
    """A mock LDAP client that makes a bind request."""
    def __init__(self, dn: str, password: str):
        self.dn = dn
        self.password = password
        super().__init__()

    def bind(self, connection, dn: str, password: str) -> Deferred:
        def _doBind(proto):
            baseEntry = ldapsyntax.LDAPEntry(client=proto, dn=DistinguishedName(dn))
            x = baseEntry.bind(password=password)
            return x
        connection.addCallbacks(_doBind, print)
        return connection

    def run(self, host, port) -> Deferred:
        d = super().run(host, port)
        return self.bind(d, self.dn, self.password)

class SearchingClient(MockLDAPClient):
    """A mock LDAP client that makes a search request."""
    def __init__(self, base_dn: str, filter: str):
        self.base_dn = base_dn
        self.filter = filter
        super().__init__()

    def search(self, connection, base_dn: str, filter: str) -> Deferred:
        def _doSearch(proto):
            from ldaptor import ldapfilter
            searchFilter = ldapfilter.parseFilter(filter)
            baseEntry = ldapsyntax.LDAPEntry(client=proto, dn=DistinguishedName(base_dn))
            x = baseEntry.search(filterObject=searchFilter)
            return x
        connection.addCallbacks(_doSearch, print)
        return connection

    def run(self, host, port) -> Deferred:
        d = super().run(host, port)
        return self.search(d, self.base_dn, self.filter)

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
    
class UnresponsiveBind(MockLDAPServer):
    """A mock LDAP server that never replies to bind requests."""
    def handle_LDAPBindRequest(self, request, controls, reply):
        # Dont reply to bind request
        return None
    
class SimpleSearch(MockLDAPServer):
    """A mock LDAP server that replies to search requests."""
    def handle_LDAPSearchRequest(self, request, controls, reply):
        dn = "cn=Bob,dc=example,dc=org"
        attributes = [
            ("cn", ["Bob"]),
            ("sn", ["Bobby"]),
            ("mail", ["bob@example.com"]),
            ("objectClass", ["inetOrgPerson"])
        ]
        # Reply to search requests with a mock person
        reply(pureldap.LDAPSearchResultEntry(objectName=dn.encode(), attributes=attributes))
        return defer.succeed(pureldap.LDAPSearchResultDone(resultCode=0))
    
class UnresponsiveSearch(MockLDAPServer):
    """A mock LDAP server that never replies to search requests."""
    def handle_LDAPSearchRequest(self, request, controls, reply):
        # Dont reply to search request
        return None

### Database ###

class MockProxyDatabase():
    """A base mock for a database. Needs to be extended with the wanted capabilities. Can be created with a set of servers."""
    def __init__(self, servers: list[ServerEntry]=[]):
        self.servers = servers

    def get_servers(self):
        return self.servers

class OneClientDatabase(MockProxyDatabase):
    """A mock database that contains only one client."""
    def __init__(self, client: ClientEntry, servers: list[ServerEntry]=[]):
        self.client = client
        super().__init__(servers)

    def get_clients(self) -> list[ClientEntry]:
        return [self.client]
    
    def get_authenticated_client(self, client_dn, client_auth) -> ClientEntry | None:
        return self.client if client_dn == self.client.dn and client_auth == self.client.password else None