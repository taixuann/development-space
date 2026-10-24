# Skills routing for agents

This document governs skill invocation for agents working in `development-space`.
Skills are dispatched strictly according to the **tool folder being modified** ([Standard tool layout](../../docs/standard-tool-layout.md)).

---

## 1. Precedence rules

1. **Superpowers outranks generic steps**:
   - For creative features or new tools: invoke `superpowers:brainstorming`.
   - For multi-step tasks: invoke `superpowers:writing-plans`.
   - For coding and bugfixes: invoke `superpowers:test-driven-development` and `superpowers:systematic-debugging`.
   - Before completion: invoke `superpowers:verification-before-completion`.

2. **Code search across tool codebases**:
   - Always query `xerj def "<symbol>"` and `xerj search "<query>"` before reading whole files.
   - For public reference code and external APIs, query `xerj "<question>"` via `xerj-hub`.

---

## 2. Tool-folder routing (Ánh xạ thư mục ➔ Kỹ năng)

When modifying or creating code in a specific folder of a tool (`tools/<space>/<tool-name>/`), invoke the corresponding specialist skill:

| Folder being modified | Skill to invoke | Boundary & Invariants |
| :--- | :--- | :--- |
| **`backend/`** | `cli-developer`<br/>`codebase-design` | Follow `Small-tool contract`. Keep the CLI flags clean and predictable. Enforce deep modules with minimal public interfaces. |
| **`frontend/`** (Web) | `impeccable` | Craft typography, layout, accessibility, spacing, and responsive design. Do not use for headless CLI tools. |
| **`frontend/`** (Swift/macOS) | `swiftui-expert-skill` | Enforce `@Observable` data flow, Liquid Glass, platform views, and proper view invalidation boundaries. |
| **`tests/`** (Browser E2E) | `playwright-cli` | Automate browser headless verification for tools that expose a web frontend. |
| **`tool root/`** | `tool-scaffolding` | Run when initializing a new tool or standardizing an existing one. |
| **PR & CI checks** | `gh-fix-ci`<br/>`gh-address-comments` | Run `gh-fix-ci` when GitHub Actions fail. Run `gh-address-comments` to address open PR review threads. |

---

## 3. Prohibitions

- Do not invoke `impeccable` or `swiftui-expert-skill` for pure CLI or backend tools.
- Do not invoke `playwright-cli` when unit tests (`pytest`, `swift test`) suffice.
- Do not bypass Superpowers TDD cycles when writing code in `backend/` or `frontend/`.
