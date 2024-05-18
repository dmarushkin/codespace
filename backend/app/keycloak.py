from keycloak import KeycloakOpenID

keycloak_openid = KeycloakOpenID(
    server_url="http://localhost:8080/auth/",
    client_id="myclient",
    realm_name="myrealm",
    client_secret_key="mysecret"
)


