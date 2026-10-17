# virtualMoney service boundary

Status: `implementedFoundation`; financial operations are `plannedBusiness`. This local foundation was generated with `service_name=virtualMoney` from committed `serviceTemplate` source. It registers only `GET /`, `GET /getOpenApi`, `/health/live`, and `/health/ready`. The default has no database resource, business table, active ledger, balance, hold, payment, or token verifier. Readiness reports foundation process readiness only.

## 🧭 Ownership and future flow

`virtualMoney` is the intended sole owner of internal financial accounts, immutable double-entry ledger entries, balances, holds, table escrow, buy-in/rebuy/cash-out accounting, rake postings, compensation, and financial history. Future reviewed inputs are authorized account or table money commands; outputs are durable financial decisions and histories. A financial account is distinct from a human login account. `pokerService` owns game state, final stacks, and serialized table commands; it must supply trusted settlement amounts through an agreed contract. `cryptoService` may later adapt external network/provider observations; it owns neither internal balances nor this database. `authService` owns principals, grants, and tokens; `accountsService` owns human credentials. No cross-service direct database writes or shared transaction are defined.

The reference design stored integer minimal units in PostgreSQL and used idempotent operation IDs. Those invariants remain design inputs, not working behavior. A later implementation needs a reviewed public API, exact authorization scopes and verifier, database schema/revisions, idempotency, concurrency, compensation, and recovery policy. No blockchain, wallet, custody, or payment provider is selected here.

## 🔒 Migration and security

The former active implementation at Git commit `9b165a7968a78747385628851ec0fcea24554d17` used dotted RPC routes and `ApplicationResponse`, with no production authorization. It is not automatically compatible with the current `PokerlostRequest`/`PokerlostResponse` SDK contract. Its source and old deployment files are recoverable from Git and the private pre-migration backup; [historical design](docs/history/README.md) is retained as reference. The confirmed `main` source contained only `alembic/versions/.gitkeep`, with no revision files. This code migration does not clean or migrate any existing storage. Do not run historical or new migrations against a live database as part of this foundation work.

Future PostgreSQL lifecycle can be enabled through a reviewed template update. Until then startup requires no DSN, provider RPC, API key, wallet address, seed, or private key. There is no protected business route and no allow-all verifier. Keep this service unreachable as a financial API until its contract and authorization are implemented and reviewed.
