from pymongo import MongoClient
DB_NAME = "ldap-proxy-database"

# DB entry of a ldap server
class ServerEntry():
    def __init__(self, ip, port, base_dn, bind_dn, bind_password, tls=False):
        self.ip = ip
        self.port = port
        self.base_dn = base_dn
        self.bind_dn = bind_dn
        self.bind_password = bind_password
        self.tls = tls

    def to_object(self):
        return {
            "ip": self.ip,
            "port": self.port,
            "base_dn": self.base_dn,
            "bind_dn": self.bind_dn,
            "bind_password": self.bind_password,
            "tls": self.tls
        }
    
# DB entry of an admin of
class UserEntry():
    def __init__(self, user, password, is_admin):
        self.user = user
        self.password = password # da cambiare, va salata
        self.is_admin = is_admin
    
    def to_object(self):
        return {
            "user": self.user,
            "password": self.password,
            "is_admin": self.is_admin,
        }

# DB utility class
class LdapProxyDatabase():
    def __init__(self, address, port):
        self.client = MongoClient(address, port)
        self.db = self.client[DB_NAME]
        
    def put_server(self, server: ServerEntry):
        self.db["servers"].insert_one(server.to_object())

    def get_servers(self):
        return [ServerEntry(ip=i["ip"], base_dn=i["base_dn"], bind_dn=i["bind_dn"], bind_password=i["bind_password"],
                               port=i["port"], tls=i["tls"]) for i in self.db["servers"].find()]
    
    def put_user(self, admin: UserEntry):
        self.db["users"].insert_one(admin.to_object())

    def get_admins(self) -> [UserEntry]:
        return self.db["users"].find({"is_admin": True})
    def get_users(self):
        return [UserEntry(i["user"], i["password"], i["is_admin"]) for i in self.db["users"].find()]

    # authenticate a user and return it. Return None if not authorized
    def get_authenticated_user(self, user_dn, user_auth) -> UserEntry | None:
        users = self.get_users()
        for u in users:
            if u.user == user_dn and u.password == user_auth:
                return u
        return None