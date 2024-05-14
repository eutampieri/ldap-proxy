use ldap3::{LdapConn, LdapError, LdapResult};

fn get_ldap_connection() -> Result<LdapConn, LdapError> {
    LdapConn::new(&std::env::var("LDAP_SERVER").unwrap_or("ldap://10.0.0.2:10389".to_string()))
}
fn ldap_bind(conn: &mut LdapConn) -> Result<LdapResult, LdapError> {
    conn.simple_bind("cn=admin,dc=example,dc=org", "adminpassword")
}

#[test]
pub fn ldap_connects() {
    let ldap = get_ldap_connection();
    assert!(ldap.is_ok());
}

#[test]
pub fn ldap_binds() {
    let mut ldap = get_ldap_connection().unwrap();
    let bind_result = ldap_bind(&mut ldap);
    assert!(bind_result.and_then(|x| x.success()).is_ok());
}

#[test]
pub fn ldap_bind_fails_with_wrong_credentials() {
    let mut ldap = get_ldap_connection().unwrap();
    let bind_result = ldap.simple_bind("cn=random,dc=example,dc=org", "randomdata");
    assert!(bind_result.and_then(|x| x.success()).is_err());
}

#[test]
pub fn ldap_search() {
    let mut ldap = get_ldap_connection().unwrap();
    ldap_bind(&mut ldap).unwrap();
    let results = ldap.search(
        "dc=example,dc=org",
        ldap3::Scope::Subtree,
        "(objectClass=inetOrgPerson)",
        vec!["dn"],
    );
    assert!(results.is_ok());
    assert_eq!(1, results.unwrap().0.len())
}
