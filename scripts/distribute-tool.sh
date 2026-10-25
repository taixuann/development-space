#!/bin/bash
# distribute-tool.sh — Universal Tool Packaging & Space Distribution Engine
# Packages tools from development-space into ~/.local/bin and binds to target space.
set -euo pipefail

TARGET="${1:-.}"
TOOL_DIR="$(cd "$TARGET" && pwd)"

if [[ ! -f "${TOOL_DIR}/pyproject.toml" && ! -f "${TOOL_DIR}/package.json" && ! -f "${TOOL_DIR}/Cargo.toml" ]]; then
    echo "[-] Error: ${TOOL_DIR} is not a valid package root (no pyproject.toml, package.json, or Cargo.toml found)." >&2
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
echo "[1/3] Building & installing CLI package via uv tool..."
mkdir -p "$HOME/.local/bin"

if [[ -f "${TOOL_DIR}/pyproject.toml" ]]; then
    uv tool install --editable "${TOOL_DIR}" --force
fi

BIN_PATH="$HOME/.local/bin/${TOOL_NAME}"
if [[ ! -f "$BIN_PATH" ]]; then
    echo "[-] Error: Expected executable not found at ${BIN_PATH}" >&2
    exit 1
fi
echo "[+] Successfully installed ${BIN_PATH}"

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

    # Check for automations
    if [[ -d "${TOOL_DIR}/automation" ]]; then
        # Wire model-control or matching automation runners
        if [[ -d "${ADMIN_AUTO_DIR}/model-control" && "$TOOL_NAME" =~ (opencode-model-router|opencode-free-router) ]]; then
            RUNNER_SCRIPT="${ADMIN_AUTO_DIR}/model-control/run-sync.sh"
            cat <<EOF > "$RUNNER_SCRIPT"
#!/bin/bash
# run-sync.sh — Automated wrapper calling installed CLI package
set -euo pipefail
export PATH="/Users/tai/.local/bin:\$PATH"
exec "${BIN_PATH}" --sync --space all "\$@"
EOF
            chmod +x "$RUNNER_SCRIPT"
            echo "[+] Updated Admin automation runner: ${RUNNER_SCRIPT}"
        fi
    fi
elif [[ "$SPACE" == "research" ]]; then
    echo "[+] Research space tool registered."
fi

# Step 3: Health check verification
echo "[3/3] Verifying tool health..."
"$BIN_PATH" --help >/dev/null

echo "=================================================================="
echo " [SUCCESS] Tool ${TOOL_NAME} is fully packaged and distributed!"
echo " CLI Command: ${BIN_PATH}"
echo "=================================================================="
