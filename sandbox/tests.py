import unittest

from find_matching_server import *

class UpstreamLdapServer():
    def __init__(self, ip, port, base_dn, user, password):
        self.ip = ip
        self.port = port
        self.base_dn = base_dn
        self.user = user
        self.password = password

server_a = UpstreamLdapServer("127.0.0.1", 10389, "dc=example,dc=org", "cn=admin,dc=example,dc=org", "custompassword")
server_b = UpstreamLdapServer("127.0.0.1", 11389, "dc=example,dc=com", "cn=admin,dc=example,dc=com", "custompassword")

class TestMethods(unittest.TestCase):
    def test_single_server(self):
        dn = "cn=a,dc=example,dc,org"
        server = get_server([server_a], dn)
        self.assertEqual("dc=example,dc=org", server.base_dn)
    def test_multiple_server(self):
        dn = "cn=a,dc=example,dc,org"
        server = get_server([server_a, server_b], dn)
        self.assertEqual("dc=example,dc=org", server.base_dn)
    def test_no_servers(self):
        dn = "cn=a,dc=example,dc,org"
        server = get_server([], dn)
        self.assertEqual(None, server)

if __name__ == '__main__':
    unittest.main()