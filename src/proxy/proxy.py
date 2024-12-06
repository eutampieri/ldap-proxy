from proxydatabase import *

# Ldap proxy
class LdapProxy():
    def __init__(self): 
        self.db = LdapProxyDatabase("localhost", 27017)
        # TODO
        pass

    # find the servers to which redirect the request
    def find_server(self, base_dn):
        servers = self.db.get_servers()
        return filter(lambda s: s.base_dn == base_dn, servers)