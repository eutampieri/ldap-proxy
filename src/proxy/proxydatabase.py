from pymongo import MongoClient
DB_NAME = "ldap-proxy-database"

# DB entry of a ldap server
class ServerEntry():
    def __init__(self, ip, port, base_dn, bind_dn, bind_password):
        self.ip = ip
        self.port = port
        self.base_dn = base_dn
        self.bind_dn = bind_dn
        self.bind_password = bind_password

    def to_object(self):
        return {
            "ip": self.ip,
            "port": self.port,
            "base_dn": self.base_dn,
            "bind_dn": self.bind_dn,
            "bind_password": self.bind_password,
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

# DB utility class
class LdapProxyDatabase():
    def __init__(self, address, port):
        self.client = MongoClient(address, port)
        self.db = self.client[DB_NAME]
        
    def put_server(self, server: ServerEntry):
        self.db["servers"].insert_one(server)

    def get_servers(self):
        return self.db["servers"].find()
    
    def put_admin(self, admin: AdminEntry):
        self.db["admins"].insert_one(admin)

    def get_admins(self):
        return self.db["admins"].find()