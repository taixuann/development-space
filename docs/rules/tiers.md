# Pick the tier first

Scope: which track a piece of work follows. Read this before any other rule file.

| Tier | Example | Track |
|---|---|---|
| Small tool | One command-line tool, one script, one purpose | Short form: `superpowers:brainstorming` (brief), then `superpowers:test-driven-development`, then `superpowers:verification-before-completion` |
| Platform or app | An API, a dashboard, a desktop app, a rewrite, anything with more than one language or more than one front end | [Phase 1](phase-1-vision.md), then [Phase 2](phase-2-plan.md), then [Phase 3](phase-3-build.md) |

Ask the user which tier applies when it is not clear. Do not infer the tier from file count alone: a one-file script with a web UI is still a platform, and a large repository that only ships one binary is still a small tool.

The tier can change. If a small tool grows a second front end or a second language, stop, say so, and move it to the three-phase track before building the new part.
