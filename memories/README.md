# Development Space memory

This directory stores engineering memory and persistent learnings specific strictly to `development-space`.
It is completely isolated from Admin orchestration, Personal records, and Research experimental data.

## Memory structure

- **`decisions.md`**: Settled engineering and architectural decisions. Agents must check this file before proposing architectural alterations to avoid reopening settled choices.
- **`learnings.md`**: Concrete technical lessons, library quirks, compiler bugs, and tool-specific gotchas encountered during development.
- **`rollouts/`**: Dated logs of tool release events, breaking changes, and migrations.

## Integration with Hindsight

- The Hindsight bank for this directory is configured as `development-space` via `/Users/tai/.hindsight/coding-agent.json`.
- Significant architectural milestones must be captured to Hindsight via `hindsight_capture_initiative`.
- Durable documentation can be ingested via `hindsight_ingest_document`.
