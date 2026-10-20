# virtualMoney

Read selected [baseRules](https://raw.githubusercontent.com/serrja/baseRules/730418d3cc480b4f05b88b4c8275296c4845a75a/docs/engineering.md),
then [Pokerlost norms](https://raw.githubusercontent.com/pokerlost/projectRules/4785546cffa58f7ae1c22b6d6b8846a0141793eb/docs/project.md),
then the full [local contracts](LOCAL_CONTRACTS.md), `PROJECT.md` and `SERVICE.md`.
The local override preserves this foundation's exact auth/scope boundaries,
project-owned settings and applied migrations. Typed SDK service identity selects
a fixed gateway backend; it never grants authorization. No planned product operation is active.

Links are pinned reading sources, not automatic loaders or grants. Review the source
diff, update full-SHA links explicitly and run docs checks to refresh rules.
