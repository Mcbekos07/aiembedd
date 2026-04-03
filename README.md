# AIEmbedd

Browser-based embedded AI IDE for Ubuntu.

## 1) Backend setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

## 2) Database init
База и таблицы создаются автоматически при старте backend через `lifespan` (`Base.metadata.create_all`).

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

## 3) Frontend setup
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

## 4) Smoke-check commands
```bash
# backend import/start smoke
cd backend && source .venv/bin/activate && python -c "from app.main import app; print(app.title)"

# health endpoint
curl http://127.0.0.1:8000/api/v1/health

# frontend build smoke
cd frontend && npm run build
```

## Deployment artifacts
- `deploy/systemd/aiembedd-backend.service`
- `deploy/nginx/aiembedd.conf`
- `deploy/scripts/install_ubuntu.sh`
- `deploy/env/.env.example`

## Backup/Cleanup skeleton
- `scripts/backup_db.sh`
- `scripts/backup_project_metadata.sh`
- `scripts/cleanup_temp_runners.sh`
