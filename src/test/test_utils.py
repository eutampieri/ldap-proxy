from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Factory
from mocks import MockLDAPClient, MockLDAPServer
    
class TestEnvironment:
    """Utility module for testing multip[le servers and clients together."""

    def __init__(self):
        self.actions = Deferred()
        self._clients = []
        self._failure = None

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
        self.actions.addTimeout(seconds, reactor, lambda err, f: self.fail(err))

    def then(self, callback) -> None:
        """Executes a callback after all the previous ones are completed"""
        self.actions.addCallback(callback)
    
    def catch(self, errback) -> None:
        """Catches an error, and executes the errback function"""
        self.actions.addErrback(errback)

    def run(self) -> None:
        """Starts the test"""
        self.catch(self.fail)
        reactor.callLater(0, self.actions.callback, None)
        reactor.run()
        if self._failure != None:
            raise self._failure

    def stop(self, ignored=None) -> None:
        """Stops the test"""
        reactor.stop()

    def fail(self, error=RuntimeError('Error during test')) -> None:
        self._failure = error

if __name__ == "__main__":
    ### Testing the testing environment ###
    from mocks import AcceptBind, RejectBind, UnresponsiveBind, BindingClient

    # create the test environment
    test = TestEnvironment()

    # add some servers to the test
    test.addServer(port=3890, server=AcceptBind)
    test.addServer(port=3891, server=RejectBind)
    test.addServer(port=3892, server=UnresponsiveBind)

    # add a client, and define some callbacks over it
    clientDeferred = test.addClient(port=3892, client=BindingClient('cn=admin,dc=example,dc=org', 'password'))

    clientDeferred.addCallback(lambda _: print("Binded successfully!"))
    clientDeferred.addErrback(lambda _: print("Error while binding!"))
    clientDeferred.addBoth(test.stop)
    
    # set a timeout for the execution
    test.addTimeout(seconds=5)

    # execute the test
    test.run()
    print(test._failure)