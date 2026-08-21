# Future Auth Service Interaction

`virtualMoney` currently contains no authentication or authorization implementation. Its internal
HTTP endpoints accept no local API key, Bearer/JWT verifier, service token, scope, principal, or
development credential. Until an external contract is implemented, deployments must isolate the
service behind a trusted network boundary or gateway.

The intended future ownership is:

```text
Client / Poker Server
        |
        | token
        v
Auth Service
        |
        | token validation / introspection contract (future)
        v
virtualMoney
```

Auth Service will own token issuance and the definition of scopes or permissions used by other
services. A future gateway or `virtualMoney` integration may validate or introspect that token,
then pass a verified identity to application operations when the external contract specifies the
required fields and trust model.

The following decisions are deliberately deferred:

- token format and signing method;
- token transport;
- local verification versus remote introspection;
- principal and service identity fields;
- permission and scope names;
- caching, revocation, failure, and availability semantics;
- audit fields and their database migration.

Do not add placeholder ports, adapters, models, middleware, token secrets, or fake principals
before those decisions are part of an explicit cross-service contract. Future identity/audit data
must be introduced by a new migration; removed `actor_service` values must not be reconstructed.
