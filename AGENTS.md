# virtualMoney

Read selected [baseRules](https://raw.githubusercontent.com/serrja/baseRules/8434509933feaa71ba312f8d02caad7362766d5a/docs/engineering.md),
then [Pokerlost norms](https://raw.githubusercontent.com/pokerlost/projectRules/c3bfb397c46c2fa1021009e13f9e1090d9078176/docs/project.md),
then the full [local contracts](LOCAL_CONTRACTS.md), `PROJECT.md` and `SERVICE.md`.
The local override preserves this foundation's exact auth/scope boundaries,
project-owned settings and applied migrations. Typed SDK service identity selects
a fixed gateway backend; it never grants authorization. No planned product operation is active.

Links are pinned reading sources, not automatic loaders or grants. Review the source
diff, update full-SHA links explicitly and run docs checks to refresh rules.
