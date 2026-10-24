#!/usr/bin/env bash
# tests/test_runner_modes.sh
set -euo pipefail

RUNNER="/Users/tai/development-space/scripts/opencode-runner.sh"

if [ ! -x "$RUNNER" ]; then
  echo "FAIL: $RUNNER is not executable"
  exit 1
fi

CASE1_PROFILE=$("$RUNNER" --dry-run --mode case1)
if [ "$CASE1_PROFILE" != "case1:deepseek-v4.1-flash->beam-free" ]; then
  echo "FAIL: expected case1 profile, got $CASE1_PROFILE"
  exit 1
fi

CASE2_PROFILE=$("$RUNNER" --dry-run --mode case2)
if [ "$CASE2_PROFILE" != "case2:beam-free->deepseek-v4.1-flash-free" ]; then
  echo "FAIL: expected case2 profile, got $CASE2_PROFILE"
  exit 1
fi

echo "PASS: Runner mode resolution works"
