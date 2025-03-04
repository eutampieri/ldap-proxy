from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Factory
from test.mocks import MockLDAPClient, MockLDAPServer
    
class TestFailure(RuntimeError):
    def __init__(self, message: str=''):
        RuntimeError.__init__(self, f"::FAILURE::{message}")

class TestEnvironment:
    """Utility module for testing multiple servers and clients together."""

    def __init__(self):
        self.actions = Deferred()
        self._clients = []
        self.succeeded = True
        self.stopped = False

    def addServer(self, port: int, server: type[MockLDAPServer]) -> None:
        """Adds a server to the reactor."""
        serverName = server.__name__

        def _createServer(res):
            factory = Factory()
            factory.protocol = server
            reactor.listenTCP(port, factory)
            print(f"[{serverName}] Running on port {port}...")

        self.actions.addCallback(lambda _: print(f"[{serverName}] Starting..."))
        return self.actions.addCallback(_createServer)

    def addClient(self, port: int, client: MockLDAPClient) -> Deferred:
        """Adds a client to the reactor. Returns the Deferred of the client"""
        clientName = client.__class__.__name__

        def _createClient(res, clientIndex):
            d = client.run(f"tcp:localhost:{port}")
            d.addCallback(lambda _: print(f"[{clientName}] Client requesting to port {port}"))
            d.chainDeferred(self._clients[clientIndex])
            return d

        # empty deferred, for accumulating callbacks
        self._clients.append(Deferred())
        index = len(self._clients) - 1

        self.actions.addCallback(lambda _: print(f"[{clientName}] Starting..."))
        self.actions.addCallback(_createClient, index)
        return self._clients[index]

    def addTimeout(self, seconds: float) -> None:
        """Adds a timeout (in seconds) for execution"""
        self.actions.addTimeout(seconds, reactor, lambda err, f: self.fail('Timeout elapsed.'))

    def then(self, callback) -> None:
        """Executes a callback after all the previous ones are completed"""
        self.actions.addCallback(callback)
    
    def catch(self, errback) -> None:
        """Catches an error, and executes the errback function"""
        self.actions.addErrback(errback)

    def run(self) -> bool:
        """Starts the test. Returns true if ran successfully, false if it failed."""
        self.catch(self.fail)
        reactor.callLater(0, self.actions.callback, None)
        try:
            reactor.run()
            return self.succeeded
        except Exception:
            return False

    def stop(self, ignored=None) -> None:
        """Stops the test"""
        if not self.stopped:
            self.stopped = True
            reactor.stop()

    def fail(self, error: str='') -> None:
        """Fails the test"""
        self.succeeded = False
        print(TestFailure(error))
        self.stop()

if __name__ == "__main__":
    ### Testing the testing environment ###
    from test.mocks import AcceptBind, RejectBind, UnresponsiveBind, BindingClient

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
    # in this case, the test should fail
    assert not test.run()