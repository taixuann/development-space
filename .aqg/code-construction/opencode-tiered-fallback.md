---
task_slug: opencode-tiered-fallback
path: mini
created_at: 2026-10-24T13:37:10.391359+00:00
session_agent: codex
skipped_checks: []
behavior_contract_exception: Configuration only; no custom plugin implementation.
---

# Tiered OpenCode fallback

Scope: project-local configuration only, preserve unrelated dirty changes.

| step | required | evidence | file:line | command/result |
|---|---|---|---|---|
| 1. Pattern Mining | yes | Inspected published V2 retry plugin and current Go quota tables | .opencode/opencode.json:1 | Plugin accepts models through ctx.options and uses retry hook |
| 2. Behavior Lock | N/A | Config only | .opencode/opencode.json:1 | Verify actual provider quota failures and fallback |
| 5. Local Verification | yes | Pending real CLI fallback | .opencode/opencode.json:1 | Pending |
| 6. Self Review | yes | Pinned plugin; no secrets, custom router, or global config edits | .opencode/opencode.json:1 | Pending runtime |

## Predicted Objections

1. Session stays on fallback after recovery (.opencode/opencode.json:3) — start a new session or select the primary model with /models after quota resets.

## Warning Acknowledgements

No custom code or production deployment. No commit requested.
