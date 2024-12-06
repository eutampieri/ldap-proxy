from pymongo import MongoClient
DB_NAME = "ldap-proxy-database"

# DB entry of a ldap server
class LdapServerEntry():
    def __init__(self, ip, port, base_dn):
        self.ip = ip
        self.port = port
        self.base_dn = base_dn
    
    def to_object(self):
        return {
            "ip": self.ip,
            "port": self.port,
            "base_dn": self.base_dn,
        }
    
# DB entry of an admin of
class AdminEntry():
    def __init__(self, user, password):
        self.user = user
        self.password = password # da cambiare, va salata
    
    def to_object(self):
        return {
            "user": self.user,
            "password": self.password,
        }