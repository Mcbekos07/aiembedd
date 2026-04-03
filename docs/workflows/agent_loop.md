# Compile-Fix Agent Loop

## Flow
1. Create pre-agent checkpoint.
2. Build project.
3. If failed -> diagnose using logs + memory + project intelligence.
4. Propose/apply patch (pre-patch checkpoint is created before apply).
5. Rebuild and iterate.
6. On success -> create successful-fix version snapshot and suggest commit message.
7. On failure -> keep rollback option to checkpoint.

## Outputs for UX
- Task timeline actions with build status, stop reason, patch ids.
- Suggested commit message action.
- Successful snapshot action with version.
