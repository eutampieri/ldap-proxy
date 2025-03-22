import ldaptor.protocols.pureldap
from twisted.internet import protocol, defer, reactor
from ldaptor.config import LDAPConfig
from ldaptor.protocols.ldap import ldapclient, merger, ldaperrors
from proxy.proxydatabase import ProxyDatabase, ServerEntry, UserEntry
from ldaptor.protocols import pureldap

class TimeoutLDAPClient(ldapclient.LDAPClient):
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

class ProxyMerger(merger.MergedLDAPServer):
    def __init__(self, database: ProxyDatabase, timeout=30):
        self.reply_counter = 0
        self.reply_store = {}
        self.protocol = lambda: TimeoutLDAPClient(timeout=timeout)
        self.database = database
        configs = database.get_servers()
        c = [self._ldap_config_from_db_entry(i) for i in configs]
        self.credentials = [i[1] for i in c]
        super().__init__([i[0] for i in c], [c.tls for c in configs])

    # def _gotResponse(self, response, replies_list, deferred):
    #     replies_list.append(response)

    #     value = isinstance(
    #         response,
    #         (
    #             pureldap.LDAPSearchResultDone,
    #             pureldap.LDAPBindResponse,
    #         ),
    #     )
    #     if value:
    #         reactor.callWhenRunning(deferred.callback)
    #     return value
    
    # def _clientQueue(self, request, controls, reply):
    #     # Controls are ignored.
    #     l = []
    #     for c in self.clients:
    #         if request.needs_answer:
    #             replies = []
    #             rd = defer.Deferred(replies)
    #             rd.addCallback(defer.succeed)
    #             rd.addErrback(defer.fail)
    #             d = c.send_multiResponse(request, self._gotResponse, replies, rd)
    #             d.addErrback(rd.errback)
    #             l.append(rd)
    #         else:
    #             c.send_noResponse(request)
        
    #     dl = defer.DeferredList(l, fireOnOneErrback=True, consumeErrors=True)

    #     def _pickWorstResponse(result: list[tuple]): #[(success, Result), ...]
    #         res = max(result, key=lambda r: r[1].resultCode)
    #         return res[1]
    #     def _replyWithError(failure): # failure is a Failure(FirstFailure)
    #         f = failure.value.subFailure
    #         r = pureldap.LDAPBindResponse(resultCode=f.value.resultCode)
    #         [reply(r) for c in self.clients]
    #     def _replyWithSuccess(result):
    #         r = _pickWorstResponse(result)
    #         [reply(r) for c in self.clients]

    #     dl.addCallback(_replyWithSuccess)
    #     dl.addErrback(_replyWithError)

    def handle_LDAPBindRequest(self, request, controls, reply):
        auth_client = self.authenticate_client(request.dn.decode("utf-8"), request.auth.decode("utf-8"))
        if auth_client is None:
            # Invalid credentials
            ldap_bind_reject = pureldap.LDAPBindResponse(resultCode=49)
            reply(ldap_bind_reject)
            return defer.succeed(ldap_bind_reject)
        else:
            # Client registered: binding with own credentials
            l = []
            for client, creds in zip(self.clients, self.credentials):
                ldap_bind_request = pureldap.LDAPBindRequest(version=3, dn=creds[0], auth=creds[1])
                d = client.send(ldap_bind_request)
                l.append(d)

            dl = defer.DeferredList(l, fireOnOneErrback=True, consumeErrors=True)

            def _pickWorstResponse(result: list[tuple]): #[(success, Result), ...]
                res = max(result, key=lambda r: r[1].resultCode)
                return res[1]
            def _replyWithError(failure): # failure is a Failure(FirstFailure)
                f = failure.value.subFailure
                r = pureldap.LDAPBindResponse(resultCode=f.value.resultCode)
                [reply(r) for c in self.clients]
            def _replyWithSuccess(result):
                r = _pickWorstResponse(result)
                [reply(r) for c in self.clients]

            dl.addCallback(_replyWithSuccess)
            dl.addErrback(_replyWithError)
            return defer.succeed(None)
        
    def handle_LDAPSearchRequest(self, request, controls, reply):
        l = []
        for client in self.clients:
            d = client.send_multiResponse(request, self._gotResponse, reply)
            l.append(d)

        dl = defer.DeferredList(l, fireOnOneErrback=True, consumeErrors=True)

        def _replyWithError(failure): # failure is a Failure(FirstFailure)
            f = failure.value.subFailure
            r = pureldap.LDAPSearchResultDone(resultCode=f.value.resultCode)
            [reply(r) for c in self.clients]

        dl.addErrback(_replyWithError)
        return defer.succeed(None)

    # def _handle_LDAPBindRequest(self, request: LDAPBindRequest, controls, reply):
    #     # authenticate user
    #     auth_client = self.authenticate_client(request.dn.decode("utf-8"), request.auth.decode("utf-8"))
    #     if auth_client is None:
    #         invalid_credentials_result_code=49
    #         print('Invalid credentials')
    #         return reply(pureldap.LDAPBindResponse(resultCode=invalid_credentials_result_code))

    #     else:
    #         for client, creds in zip(self.clients, self.credentials):
    #             ldap_bind_request = LDAPBindRequest(version=3, dn=creds[0], auth=creds[1])
    #             d = client.send_multiResponse(ldap_bind_request, self._gotResponse, reply)
    #             d.addErrback(defer.logError)
    #     return defer.succeed(request)

    # def add_server(self, server: ServerEntry):
    #    c = self._ldap_config_from_db_entry(server)
    #    self.configs.append(c[0])
    #    self.credentials.append(c[1])

    def _ldap_config_from_db_entry(self, config: ServerEntry):
        return (
            LDAPConfig(serviceLocationOverrides={"": (config.ip, config.port)}),
            (config.bind_dn, config.bind_password)
        )

    # authenticate a user. Return None if not authorized
    def authenticate_client(self, dn, auth):
        return self.database.get_authenticated_client(dn, auth)