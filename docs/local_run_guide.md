# Local Run Guide

## Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[test]
uvicorn app.main:app --reload
```

## Frontend
```bash
cd frontend
npm install
npm run dev
```
