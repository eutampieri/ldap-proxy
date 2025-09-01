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


# DB entry of a user/admin
class UserEntry():
    def __init__(self, user, password, is_admin):
        self.user = user
        self.password = password  # da cambiare, va salata
        self.is_admin = is_admin

    def to_object(self):
        return {
            "user": self.user,
            "password": self.password,
            "is_admin": self.is_admin,
        }


# DB entry of a client
class ClientEntry():
    def __init__(self, dn, password):
        self.dn = dn
        self.password = password  # da cambiare, va salata

    def to_object(self):
        return {
            "dn": self.dn,
            "password": self.password,
        }
