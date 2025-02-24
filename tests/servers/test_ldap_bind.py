from twisted.internet import defer
from twisted.internet.task import react
from twisted.internet.endpoints import clientFromString, connectProtocol
from ldaptor import ldapfilter
from ldaptor.protocols.ldap import ldapsyntax
from ldaptor.protocols.ldap.ldapconnector import connectToLDAPEndpoint
from ldaptor.protocols.ldap.ldapclient import LDAPClient
from ldaptor.protocols.ldap.distinguishedname import DistinguishedName

def search(reactor, endpointStr, base_dn):
    d = connectToLDAPEndpoint(reactor, endpointStr, LDAPClient)

    def _doSearch(proto):
        searchFilter = ldapfilter.parseFilter('(gn=j*)')
        baseEntry = ldapsyntax.LDAPEntry(client=proto, dn=base_dn)
        x = baseEntry.search(filterObject=searchFilter)
        return x

    d.addCallback(_doSearch)
    return d

def bind(reactor, endpointStr, base_dn, password):
    d = connectToLDAPEndpoint(reactor, endpointStr, LDAPClient)

    def _doBind(proto):
        baseEntry = ldapsyntax.LDAPEntry(client=proto, dn=base_dn)
        x = baseEntry.bind(password=password)
        return x
    
    d.addCallback(_doBind)
    return d

def main(reactor):
    import sys
    from twisted.python import log
    log.startLogging(sys.stderr, setStdout=0)
    dn =  DistinguishedName('dc=example,dc=org')
    # d = search(reactor, "tcp:localhost:3890", dn)
    d = bind(reactor, "tcp:localhost:3890", dn, 'password')

    def _show(results):
        for item in results:
            print(item)

    d.addCallback(_show)
    d.addErrback(defer.logError)
    d.addBoth(lambda _: reactor.stop())
    return d

if __name__ == '__main__':
    react(main)