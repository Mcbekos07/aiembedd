#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip nginx git

mkdir -p /opt/aiembedd/{data,logs,backups}
echo "Install completed. Configure .env and deploy builds manually."
