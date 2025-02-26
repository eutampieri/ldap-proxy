from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Factory
from mocks import MockLDAPClient, MockLDAPServer
    
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
    from mocks import AcceptBind, RejectBind, BindingClient

    test = TestUtils()
    test.addServer(port=3890, server=AcceptBind)
    test.addServer(port=3891, server=RejectBind)
    c = test.addClient(port=3890, client=BindingClient('cn=admin,dc=example,dc=org', 'password'))
    c.addCallback(lambda _: print("Binded successfully!"))
    c.addErrback(lambda _: print("Error while binding!"))
    c.addBoth(test.stop)
    test.run()