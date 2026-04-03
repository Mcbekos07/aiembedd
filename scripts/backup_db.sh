#!/usr/bin/env bash
set -euo pipefail
mkdir -p backups
cp data/aiembedd.db "backups/aiembedd_$(date +%Y%m%d_%H%M%S).db"
