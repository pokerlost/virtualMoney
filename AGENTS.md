# virtualMoney

Read selected [baseRules](https://raw.githubusercontent.com/serrja/baseRules/bafcb63ed94b9769a0ca098e5db4b33c55dbc1b9/docs/engineering.md),
then [Pokerlost norms](https://raw.githubusercontent.com/pokerlost/projectRules/904c65a3daab88802fb5e414cdaccc7ad2b555a8/docs/project.md),
then the full [local contracts](LOCAL_CONTRACTS.md), `PROJECT.md` and `SERVICE.md`.
The local override preserves this foundation's exact auth/scope boundaries,
project-owned settings and applied migrations. Typed SDK service identity selects
a fixed gateway backend; it never grants authorization. No planned product operation is active.

Links are pinned reading sources, not automatic loaders or grants. Review the source
diff, update full-SHA links explicitly and run docs checks to refresh rules.

Daily work uses `dev` and lint only. `main` and `test` stay unchanged until an
explicit promotion. Full acceptance, template render/update checks, builds and
releases are manual; a dev snapshot is not a verified release.
