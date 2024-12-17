from pymongo import MongoClient
DB_NAME = "ldap-proxy"

class UpstreamLdapServer():
    def __init__(self, ip, port, base_dn, user, password):
        self.ip = ip
        self.port = port
        self.base_dn = base_dn
        self.user = user
        self.password = password
    
    def to_object(self):
        return {"ip": self.ip,
            "port": self.port,
            "base_dn": self.base_dn,
            "user": self.user,
            "password": self.password
            }

client = MongoClient("mongodb://127.0.0.1:27017")
database = client.get_database(DB_NAME)
config_collection = database.get_collection("ldap_servers")
server_a = UpstreamLdapServer("127.0.0.1", 10389, "dc=example,dc=org", "cn=admin,dc=example,dc=org", "custompassword")
server_b = UpstreamLdapServer("127.0.0.1", 11389, "dc=example,dc=com", "cn=admin,dc=example,dc=com", "custompassword")
print(config_collection.insert_many([server_a.to_object(), server_b.to_object()]))
print([i for i in config_collection.find()])
client.close()