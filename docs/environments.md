# Runtime environments

`ServiceSettings.environment` accepts `main`, `dev`, `test`, or `local` (the default).
Set `VIRTUALMONEY_RUNTIME_ENVIRONMENT` or pass `environment=...` explicitly.
Constructor values take priority over process variables, then an explicitly selected
dotenv file or secret directory. No dotenv file is loaded automatically.

`ObservabilitySettings.environment` retains its separate execution contour:
`VIRTUALMONEY_ENVIRONMENT` accepts `local`, `dev`, `ci`, or `remote`, defaulting to `local`.
The inputs do not map into each other; a test deployment may run in the CI contour.
Existing log-level aliases and constructor overrides remain available.

These labels do not configure endpoints, databases, credentials, caches or namespaces.
This financial service remains an empty foundation without persistence, providers,
financial operations or an outbound SDK client. Setting an environment never provisions,
migrates or isolates resources. Owners must configure any future separation explicitly.

The exact existing SDK dependency remains pinned; this change does not enable a new
SDK factory or change HTTP paths, JSON, scopes or authorization. Follow the normal
working-branch to test, dev and main review flow with the full native checks.
