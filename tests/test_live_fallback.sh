#!/usr/bin/env bash
# tests/test_live_fallback.sh
set -euo pipefail

cd /Users/tai/development-space
OUTPUT=$(opencode run "Output EXACTLY the string: FALLBACK_SUCCESS" 2>&1)

echo "$OUTPUT"

if echo "$OUTPUT" | grep -q "FALLBACK_SUCCESS"; then
  echo "PASS: Fallback to beam-free succeeded and produced expected output"
  exit 0
else
  echo "FAIL: Expected FALLBACK_SUCCESS in output"
  exit 1
fi
