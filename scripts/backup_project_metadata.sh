#!/usr/bin/env bash
set -euo pipefail
mkdir -p backups
cp -r data/workspaces "backups/workspaces_$(date +%Y%m%d_%H%M%S)"
