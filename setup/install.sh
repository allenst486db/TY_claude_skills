#!/usr/bin/env bash
# setup/install.sh — macOS/Linux/Git Bash 편의 래퍼. 실제 작업은 install.mjs 가 한다.
#
#   bash setup/install.sh --dry-run
#   bash setup/install.sh

set -euo pipefail
command -v node >/dev/null 2>&1 || { echo "Node.js 18+ 가 필요합니다." >&2; exit 1; }
exec node "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/install.mjs" "$@"
