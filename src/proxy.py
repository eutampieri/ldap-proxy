from twisted.internet import reactor
from ldaptor.protocols.ldap.ldapserver import LDAPServer
from ldaptor.protocols.ldap.ldaperrors import LDAPBindNotAllowed, LDAPUnknownCommand

class RestrictedProxyServer(LDAPServer):
    def handleUnknownCommand(self, request):
        # Reject all unknown commands
        return LDAPUnknownCommand(request)

    def handle_LDAPBindRequest(self, request):
        # Handle bind request
        print(request)
        return super().handle_LDAPBindRequest(request)

    def handle_LDAPSearchRequest(self, request):
        # Handle search request
        print(request)
        return super().handle_LDAPSearchRequest(request)

    def handle_LDAPAddRequest(self, request):
        # Reject add request
        return LDAPBindNotAllowed(request)

    def handle_LDAPDeleteRequest(self, request):
        # Reject delete request
        return LDAPBindNotAllowed(request)

    def handle_LDAPModifyRequest(self, request):
        # Reject modify request
        return LDAPBindNotAllowed(request)

if __name__ == "__main__":
    from twisted.internet.protocol import Factory

    f = Factory()
    f.protocol = RestrictedProxyServer
    reactor.listenTCP(10389, f)
    reactor.run()