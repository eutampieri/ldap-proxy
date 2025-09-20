from pymongo import MongoClient
from proxy.entries import *

DB_NAME = "ldap-proxy-database"

# DB utility class
class ProxyDatabase():
    def __init__(self, address, port):
        self.client = MongoClient(address, port)
        self.db = self.client[DB_NAME]
        
    def get_servers(self) -> list[ServerEntry]:
        return [ServerEntry(ip=i["ip"], base_dn=i["base_dn"], bind_dn=i["bind_dn"], bind_password=i["bind_password"],
                               port=i["port"], tls=i["tls"]) for i in self.db["servers"].find()]
    
    def put_client(self, client: ClientEntry) -> None:
        self.db["clients"].insert_one(client.to_object())

    def get_clients(self) -> list[ClientEntry]:
        return [ClientEntry(i["dn"], i["password"]) for i in self.db["clients"].find()]

    # authenticate a client and return it. Return None if not authorized
    def get_authenticated_client(self, client_dn, client_auth) -> ClientEntry | None:
        clients = self.get_clients()
        for u in clients:
            if u.dn == client_dn and u.password == client_auth:
                return u
        return None