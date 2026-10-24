# Daily Update Automation: Skills, Superpowers & MCP Xerj

Automated daily maintenance service for `development-space`.

## Responsibilities
1. **Skills Update**: Executes `npx skills update -p -y` to keep project skills in sync.
2. **Superpowers Plugin Check**: Verifies latest upstream git commit of `https://github.com/obra/superpowers.git`.
3. **MCP Xerj Sync**: Asserts local `xerj` binary health and verifies sync across `.agents/mcp.json`, `.opencode/opencode.json`, and `.codex/config.toml`.
4. **Structured Logging**: Pure log-focused execution outputting to `logs/update-YYYY-MM-DD.log`.

## Usage
- **Manual run (live)**:
  ```bash
  ./update.sh
  ```
- **Manual run (dry run)**:
  ```bash
  ./update.sh --dry-run
  ```
- **Install as daily launchd service (runs daily at 03:00)**:
  ```bash
  ./install-launchd.sh
  ```
- **Check service status**:
  ```bash
  ./status.sh
  ```
- **Uninstall service**:
  ```bash
  ./uninstall-launchd.sh
  ```
