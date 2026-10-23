# Runtime environments

`main`, `dev`, `test` and `local` identify a process, not a Git branch or service ID.
The explicit `ServiceSettings(environment=...)` argument overrides the corresponding
prefixed environment variable. The safe default is `local`; `.env.example` is not
automatically loaded. No HOME, Git or remote endpoint is read on import.

Select a separate database, credentials and deployment namespace for each remote
environment. `DATABASE_URL` remains explicit and secret-redacted; setting the
identity alone does not provision, migrate or isolate an existing database.
Existing local volumes and paths are preserved. Remote endpoints are not configured
by this repository. Container callers need an explicit approved routing arrangement;
the SDK's local origin means loopback in the caller's network namespace.

The SDK's new explicit environment client factory is available in its development
source. This service keeps its existing exact SDK dependency until a separately
reviewed dependency update; no automatic dependency upgrade or fallback to main.

Development: `git switch dev`, `make lint`, review diff and `git push origin dev`.
Full tests, builds, database integration and promotion remain manual. This source
change has lint-only verification, not runtime or deployment acceptance.
