#!/usr/bin/env bash
set -euo pipefail
find data/runners -mindepth 1 -maxdepth 1 -type d -mtime +2 -exec rm -rf {} +
