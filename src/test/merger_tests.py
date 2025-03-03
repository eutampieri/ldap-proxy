import unittest

### Tests for the LDAP proxy merger ###

# 1. Bind: the client should bind if he's registered to the proxy
# 2. Search: the search should be done on all the server
# 3. Consistency over Availability
# 4. Read-only proxy: only queries should be allowed
# 5. Database error handling

class TestProxyMerger(unittest.TestCase):
    def test_registered_client_should_bind():
        pass
    def test_unregistered_client_should_not_bind():
        pass
    def test_bind_should_fail_when_one_server_is_unavailable():
        pass
    def test_search_should_be_executed_on_all_servers():
        pass
    def test_search_should_fail_when_one_server_is_unavailable():
        pass
    def test_only_read_operations_should_be_allowed():
        pass
    def test_request_should_fail_when_database_is_unavailable():
        pass

if __name__ == '__main__':
    unittest.main()