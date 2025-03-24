import ldaptor.protocols.pureldap
from twisted.internet import protocol, defer, reactor
from ldaptor.config import LDAPConfig
from ldaptor.protocols.ldap import ldapclient, merger, ldaperrors
from proxy.proxydatabase import ProxyDatabase, ServerEntry, UserEntry
from ldaptor.protocols import pureldap

class TimeoutLDAPClient(ldapclient.LDAPClient):
    """LDAP Client that can be set with a timeout for connection"""
    def __init__(self, timeout=30):
        self.timeout = timeout
        super().__init__()

    def __on_timeout(self, err, time):
        raise ldaperrors.LDAPTimeLimitExceeded(f"LDAP request timed out after {time} seconds")
    
    def send(self, op, controls=None):
        d = super().send(op, controls)
        d.addTimeout(self.timeout, reactor, self.__on_timeout)
        return d
    
    def send_multiResponse(self, op, handler, *args, **kwargs):
        d = super().send_multiResponse(op, handler, *args, **kwargs)
        d.addTimeout(self.timeout, reactor, self.__on_timeout)
        return d
    
    def send_multiResponse_ex(self, op, controls=None, handler=None, *args, **kwargs):
        d = super().send_multiResponse_ex(self, op, controls, handler, *args, **kwargs)
        d.addTimeout(self.timeout, reactor, self.__on_timeout)
        return d
    
class DeferredRequestAggregator():
    """Deferred builder that simplifies the creation of DeferredList for replying to LDAPRequests."""
    def __init__(self, reply, LDAPReplyMessageType: pureldap.LDAPProtocolResponse):
        """Create an empty builder. Define the `reply` method and the `msg type` for response."""
        self.requests = []
        self.callbacks = []
        self.msg_type = LDAPReplyMessageType
        self.reply = reply

    def append(self, request: defer.Deferred):
        """Add a request to the list."""
        self.requests.append(request)

    def addErrback(self, errback):
        """Add an errback to the final DeferredList."""
        self.callbacks.append((False, errback))

    def addCallback(self, callback):
        """Add a callback to the final DeferredList."""
        self.callbacks.append((True, callback))

    def build(self) -> defer.DeferredList:
        """Generate the DeferredList from the requests added. It automagically replies on error, so no management is needed."""
        deferred = defer.DeferredList(self.requests, fireOnOneErrback=True, consumeErrors=True)
        for c in self.callbacks:
            if c[0]:
                deferred.addCallback(c[1])
            else:
                deferred.addErrback(c[1])
        def _replyWithError(failure): # failure is a Failure(FirstFailure)
            f = failure.value.subFailure
            r = self.msg_type(resultCode=f.value.resultCode)
            [self.reply(r) for c in self.requests]
        deferred.addErrback(_replyWithError)
        return deferred

class ProxyMerger(merger.MergedLDAPServer):
    def __init__(self, database: ProxyDatabase, timeout=30):
        self.protocol = lambda: TimeoutLDAPClient(timeout=timeout)
        self.allowed_operations = (pureldap.LDAPBindRequest, pureldap.LDAPSearchRequest)
        self.database = database

        creds, configs, tsl = self._fetchConfigs()
        self.credentials = creds
        super().__init__(configs, tsl)

    def handle(self, msg):
        # override handle() so that it loads the configuration from the database
        # before processing the request
        h = super().handle(msg)
        
        if isinstance(msg.value, self.allowed_operations):
            d = self.loadConfigs()
            d.addCallback(lambda _: h)
            return d
        else:
            return h

    def handle_LDAPBindRequest(self, request, controls, reply):
        auth_client = self.authenticate_client(request.dn.decode("utf-8"), request.auth.decode("utf-8"))
        if auth_client is None:
            # Invalid credentials
            ldap_bind_reject = pureldap.LDAPBindResponse(resultCode=49)
            reply(ldap_bind_reject)
            return defer.succeed(ldap_bind_reject)
        else:
            # Client registered: binding with own credentials
            # for each client, send a bind request but with the credentials of the proxy
            builder = DeferredRequestAggregator(reply, pureldap.LDAPBindResponse)
            for client, creds in zip(self.clients, self.credentials):
                ldap_bind_request = pureldap.LDAPBindRequest(version=3, dn=creds[0], auth=creds[1])
                d = client.send(ldap_bind_request)
                builder.append(d)

            def _pickWorstResult(result):
                r = max(result, key=lambda r: r[1].resultCode)
                return r[1]
            def _replyWithSuccess(result): # result is [(bool, result), (bool, result), ...]
                r = _pickWorstResult(result)
                [reply(r) for c in self.clients]

            builder.addCallback(_replyWithSuccess)
            builder.build()

            return defer.succeed(None)
        
    def handle_LDAPSearchRequest(self, request, controls, reply):
        # this override is only to have a better control over errors
        # self.loadConfigs()
        builder = DeferredRequestAggregator(reply, pureldap.LDAPSearchResultDone)
        for client in self.clients:
            d = client.send_multiResponse(request, self._gotResponse, reply)
            builder.append(d)

        builder.build()

        return defer.succeed(None)

    def _ldap_config_from_db_entry(self, config: ServerEntry):
        return (
            LDAPConfig(serviceLocationOverrides={"": (config.ip, config.port)}),
            (config.bind_dn, config.bind_password)
        )
    
    def _fetchConfigs(self):
        configs = self.database.get_servers()
        c = [self._ldap_config_from_db_entry(i) for i in configs]
        proxyCredentials = [i[1] for i in c]
        proxyConfigs = [i[0] for i in c]
        proxyTSL = [c.tls for c in configs]
        return (proxyCredentials, proxyConfigs, proxyTSL)
    
    def loadConfigs(self) -> defer.Deferred:
        """Load the proxy configuration. Return a deferred that fires when completed."""
        def _load(ignored=None):
            creds, configs, tsl = self._fetchConfigs()
            self.credentials = creds
            self.configs = configs
            self.use_tls = tsl

        d = defer.succeed(None)
        d.addCallback(_load)
        return d

    # authenticate a user. Return None if not authorized
    def authenticate_client(self, dn, auth):
        return self.database.get_authenticated_client(dn, auth)