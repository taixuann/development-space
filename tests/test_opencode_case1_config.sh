#!/usr/bin/env bash
# tests/test_opencode_case1_config.sh
set -euo pipefail

CONFIG_FILE="/Users/tai/development-space/.opencode/opencode.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "FAIL: $CONFIG_FILE does not exist"
  exit 1
fi

PRIMARY_MODEL=$(jq -r '.model' "$CONFIG_FILE")
FALLBACK_COUNT=$(jq '.plugins[0].options.models | length' "$CONFIG_FILE")
FIRST_MODEL=$(jq -r '.plugins[0].options.models[0]' "$CONFIG_FILE")
SECOND_MODEL=$(jq -r '.plugins[0].options.models[1]' "$CONFIG_FILE")

if [ "$PRIMARY_MODEL" != "opencode-go/deepseek-v4.1-flash" ]; then
  echo "FAIL: Primary model is $PRIMARY_MODEL, expected opencode-go/deepseek-v4.1-flash"
  exit 1
fi

if [ "$FALLBACK_COUNT" -ne 2 ]; then
  echo "FAIL: Fallback list must have exactly 2 models, got $FALLBACK_COUNT"
  exit 1
fi

if [ "$FIRST_MODEL" != "opencode-go/deepseek-v4.1-flash" ] || [ "$SECOND_MODEL" != "opencode-go/beam-free" ]; then
  echo "FAIL: Expected [opencode-go/deepseek-v4.1-flash, opencode-go/beam-free], got [$FIRST_MODEL, $SECOND_MODEL]"
  exit 1
fi

echo "PASS: Case 1 configuration conforms to 2-model strict chain"
