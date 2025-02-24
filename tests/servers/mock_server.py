from twisted.internet import reactor, defer
from ldaptor.protocols.ldap.ldapserver import LDAPServer
from ldaptor.protocols.ldap.ldaperrors import LDAPNotAllowedOnRDN, LDAPOperationsError
from ldaptor.protocols import pureldap

class MockLDAPServer(LDAPServer):
    def handleUnknown(self, request, controls, callback):
        # Reject all unknown commands
        print(request)
        return super().handleUnknown(request, controls, callback)

    def handle_LDAPBindRequest(self, request, controls, reply):
        # Handle bind request

        # return super().handle_LDAPBindRequest(request, controls, reply)
        return reply(pureldap.LDAPBindResponse(resultCode=0))

    def handle_LDAPSearchRequest(self, request, controls, reply):
        # Handle search request
        return reply(super().fail_LDAPSearchRequest())

    def handle_LDAPAddRequest(self, request, controls, reply):
        # Reject add request
        print(request)
        return super().handle_LDAPAddRequest(request, controls, reply)

    def handle_LDAPDelRequest(self, request, controls, reply):
        # Reject delete request
        print(request)
        return super().handle_LDAPDelRequest(request, controls, reply)

    def handle_LDAPModifyRequest(self, request, controls, reply):
        # Reject modify request
        print(request)
        return super().handle_LDAPModifyRequest(request, controls, reply)

if __name__ == "__main__":
    from twisted.internet.protocol import Factory

    factory = Factory()
    factory.protocol = MockLDAPServer

    reactor.listenTCP(3890, factory)
    print("[Mock LDAP Server] Running on port 3890...")
    reactor.run()
