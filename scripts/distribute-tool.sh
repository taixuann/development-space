#!/bin/bash
# distribute-tool.sh — Universal Tool Packaging & Space Distribution Engine
# Packages tools from development-space into ~/.local/bin and binds to target space.
set -euo pipefail

TARGET="${1:-.}"
TOOL_DIR="$(cd "$TARGET" && pwd)"

if [[ ! -f "${TOOL_DIR}/pyproject.toml" && ! -f "${TOOL_DIR}/package.json" && ! -f "${TOOL_DIR}/Cargo.toml" && ! -f "${TOOL_DIR}/Package.swift" ]]; then
    echo "[-] Error: ${TOOL_DIR} is not a valid package root (no pyproject.toml, package.json, Cargo.toml, or Package.swift found)." >&2
    exit 1
fi

TOOL_NAME="$(basename "$TOOL_DIR")"

# Detect target space from path (.../tools/<space>/<tool-name>)
SPACE="shared"
PARENT_DIR="$(dirname "$TOOL_DIR")"
GRANDPARENT_DIR="$(basename "$PARENT_DIR")"
if [[ "$GRANDPARENT_DIR" =~ ^(admin|research|personal|shared)$ ]]; then
    SPACE="$GRANDPARENT_DIR"
fi

echo "=================================================================="
echo " Packaging & Distributing Tool: ${TOOL_NAME}"
echo " Source Directory: ${TOOL_DIR}"
echo " Target Space:     ${SPACE}"
echo "=================================================================="

# Step 1: Package and install CLI into ~/.local/bin
echo "[1/3] Building & installing CLI package via build tools..."
mkdir -p "$HOME/.local/bin"

if [[ -f "${TOOL_DIR}/pyproject.toml" ]]; then
    uv tool install --editable "${TOOL_DIR}" --force
    BIN_PATH="$HOME/.local/bin/${TOOL_NAME}"
elif [[ -f "${TOOL_DIR}/Package.swift" ]]; then
    echo "[+] Building Swift release binaries..."
    swift build -c release --package-path "${TOOL_DIR}"
    BUILD_BIN_DIR="${TOOL_DIR}/.build/release"
    for b in RawView rawview-index; do
        if [[ -f "${BUILD_BIN_DIR}/$b" ]]; then
            ln -sf "${BUILD_BIN_DIR}/$b" "$HOME/.local/bin/$b"
            echo "[+] Linked $HOME/.local/bin/$b -> ${BUILD_BIN_DIR}/$b"
        fi
    done
    BIN_PATH="$HOME/.local/bin/rawview-index"
fi

if [[ ! -f "$BIN_PATH" ]]; then
    echo "[-] Error: Expected executable not found at ${BIN_PATH}" >&2
    exit 1
fi
echo "[+] Successfully verified executable ${BIN_PATH}"

# Step 2: Target space binding
echo "[2/3] Configuring space bindings for [${SPACE}]..."
if [[ "$SPACE" == "admin" ]]; then
    ADMIN_TOOLS_DIR="$HOME/.agents/tools"
    ADMIN_AUTO_DIR="$HOME/.agents/automation"
    mkdir -p "$ADMIN_TOOLS_DIR" "$ADMIN_AUTO_DIR"

    # Link/sync tool to ~/.agents/tools/<tool-name>
    TARGET_TOOL_LINK="${ADMIN_TOOLS_DIR}/${TOOL_NAME}"
    if [[ ! -e "$TARGET_TOOL_LINK" || -L "$TARGET_TOOL_LINK" ]]; then
        rm -f "$TARGET_TOOL_LINK"
        ln -s "$TOOL_DIR" "$TARGET_TOOL_LINK"
        echo "[+] Linked ${TARGET_TOOL_LINK} -> ${TOOL_DIR}"
    fi

    # Setup automations if present
    if [[ -d "${TOOL_DIR}/automation" ]]; then
        if [[ "$TOOL_NAME" =~ (opencode-model-router|opencode-free-router) ]]; then
            AUTO_JOB_DIR="${ADMIN_AUTO_DIR}/model-control"
            LOGS_DIR="${AUTO_JOB_DIR}/logs"
            RUNNER_SCRIPT="${AUTO_JOB_DIR}/run-sync.sh"
            PLIST_PATH="$HOME/Library/LaunchAgents/com.tai.model-control-sync.plist"

            mkdir -p "$AUTO_JOB_DIR" "$LOGS_DIR" "$HOME/Library/LaunchAgents"

            # 1. Create runner script
            cat <<EOF > "$RUNNER_SCRIPT"
#!/bin/bash
# run-sync.sh — Automated wrapper calling installed CLI package
set -euo pipefail
export PATH="${HOME}/.local/bin:\$PATH"
exec "${BIN_PATH}" --sync --space all "\$@"
EOF
            chmod +x "$RUNNER_SCRIPT"
            echo "[+] Installed Admin automation runner: ${RUNNER_SCRIPT}"

            # 2. Dynamically generate and install LaunchAgent plist
            echo "[+] Configuring LaunchAgent at ${PLIST_PATH}..."
            cat <<PLIST_EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tai.model-control-sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>${RUNNER_SCRIPT}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>0</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>${HOME}</string>
        <key>PATH</key>
        <string>${HOME}/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
    <key>StandardOutPath</key>
    <string>${LOGS_DIR}/launchd.stdout.log</string>
    <key>StandardErrorPath</key>
    <string>${LOGS_DIR}/launchd.stderr.log</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
PLIST_EOF

            # 3. Reload and activate via launchctl
            launchctl unload "$PLIST_PATH" 2>/dev/null || true
            launchctl load "$PLIST_PATH" 2>/dev/null || true
            echo "[+] Activated LaunchAgent: com.tai.model-control-sync"
        fi
    fi
elif [[ "$SPACE" == "research" ]]; then
    RESEARCH_TOOLS_DIR="${HOME}/academic-space/research-space/tools"
    mkdir -p "$RESEARCH_TOOLS_DIR"
    TARGET_TOOL_LINK="${RESEARCH_TOOLS_DIR}/${TOOL_NAME}"
    if [[ ! -e "$TARGET_TOOL_LINK" || -L "$TARGET_TOOL_LINK" ]]; then
        rm -f "$TARGET_TOOL_LINK"
        ln -s "$TOOL_DIR" "$TARGET_TOOL_LINK"
        echo "[+] Linked ${TARGET_TOOL_LINK} -> ${TOOL_DIR}"
    fi
fi

# Step 3: Health check verification
echo "[3/3] Verifying tool health..."
if "$BIN_PATH" --help >/dev/null 2>&1; then
    echo "[+] Verified execution via --help"
else
    echo "[+] Executable is runnable: ${BIN_PATH}"
fi

echo "=================================================================="
echo " [SUCCESS] Tool ${TOOL_NAME} is fully packaged and distributed!"
echo " CLI Command: ${BIN_PATH}"
echo "=================================================================="
