from proxydatabase import *
from ldaptor.protocols import pureldap
from ldaptor.protocols.ldap.ldaperrors import LDAPTimeLimitExceeded
from ldaptor.protocols.ldap.ldapclient import LDAPClient
from ldaptor.protocols.ldap.ldapconnector import connectToLDAPEndpoint
from ldaptor.protocols.ldap.proxybase import ProxyBase
from twisted.internet import defer, protocol, reactor
from twisted.python import log
from functools import partial
import sys
 
PROTOCOL = "ssl"  # ssl or tcp
PROXY_IP = "ldap.example.com"
PROXY_PORT = 10636
DB_IP = "localhost"
DB_PORT = 21017

# Ldap proxy
class LdapProxy(ProxyBase):
    
    def __init__(self):
        super().__init__(self)
        self.db = LdapProxyDatabase(DB_IP, DB_PORT)
        # TODO
        pass

    # find the servers to which redirect the request
    def find_server(self, base_dn):
        servers = self.db.get_servers()
        return filter(lambda s: s.base_dn == base_dn, servers)
    
    # change the client connection configuration, in order to connect to
    # a specific LDAP server
    def set_proxied_client(self, ip, port):
        endpointString = '{PROTOCOL}:host={ip}:port={port}'
        self.use_tls = False
        self.clientConnector = partial(
            connectToLDAPEndpoint,
            reactor,
            endpointString,
            LDAPClient)
    
    def handleBeforeForwardRequest(self, request, controls, reply):
        # TODO
        # log.msg("Request => " + repr(request))
        # if ratelimiter.check(request):
        #     return defer.succeed((request, controls))
        # else:
        #     log.msg("> RATE LIMIT EXCEEDED")
        #     msg = pureldap.LDAPResult(resultCode=LDAPTimeLimitExceeded.resultCode, errorMessage="Rate Limit Exceeded")
        #     reply(msg)
        #     return defer.succeed(None)
        return defer.succeed((request, controls))
 
    def handleProxiedResponse(self, response, request, controls):
        log.msg("Request => " + repr(request))
        log.msg("Response => " + repr(response))
        log.msg("------------------------------------")
        return defer.succeed(response)
 
 
def ldapBindRequestRepr(self):
    l = []
    l.append('version={0}'.format(self.version))
    l.append('dn={0}'.format(repr(self.dn)))
    l.append('auth=****')
    if self.tag != self.__class__.tag:
        l.append('tag={0}'.format(self.tag))
    l.append('sasl={0}'.format(repr(self.sasl)))
    return self.__class__.__name__+'('+', '.join(l)+')'
 
 
pureldap.LDAPBindRequest.__repr__ = ldapBindRequestRepr
 
if __name__ == '__main__':
    # set port
    if len(sys.argv) > 1:
        PROXY_PORT = int(sys.argv[1])
    # start logging service
    log.startLogging(sys.stderr)
    factory = protocol.ServerFactory()
 
    def buildProtocol():
        return LdapProxy()
 
    factory.protocol = buildProtocol
    reactor.listenTCP(PROXY_PORT, factory)
    reactor.run()