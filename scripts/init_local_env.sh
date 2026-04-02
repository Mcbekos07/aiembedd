#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

if [[ ! -f ".env" && -f ".env.example" ]]; then
  cp .env.example .env
  echo "[ok] created .env from .env.example"
fi

if [[ ! -f "backend/.env" && -f "backend/.env.example" ]]; then
  cp backend/.env.example backend/.env
  echo "[ok] created backend/.env from backend/.env.example"
fi

if [[ ! -f "frontend/.env" && -f "frontend/.env.example" ]]; then
  cp frontend/.env.example frontend/.env
  echo "[ok] created frontend/.env from frontend/.env.example"
fi

python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements-dev.txt

echo "[ok] backend virtualenv initialized at backend/.venv"
