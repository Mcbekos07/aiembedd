# Local Ubuntu Run Guide

Проверено для Ubuntu 22.04/24.04 и Python 3.11+.

## 1) Системные зависимости

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip curl
sudo apt install -y nodejs npm
```

## 2) Инициализация окружения проекта

```bash
cd /path/to/aiembedd
./scripts/init_local_env.sh
```

Скрипт делает:
- копирует `.env` файлы из `*.example` (если их нет),
- создаёт `backend/.venv`,
- ставит backend runtime+dev зависимости.

## 3) Запуск backend

```bash
cd /path/to/aiembedd
./scripts/run_backend.sh
```

Backend будет доступен на `http://127.0.0.1:8000`.

## 4) Запуск frontend

В отдельном терминале:

```bash
cd /path/to/aiembedd
./scripts/run_frontend.sh
```

Frontend будет доступен на `http://127.0.0.1:5173`.

## 5) Runtime проверки API

```bash
curl http://127.0.0.1:8000/api/v1/health
curl http://127.0.0.1:8000/api/v1/projects
```

Ожидаемо:
- `/health` возвращает JSON со `status: "ok"`.
- `/projects` возвращает JSON-массив (пустой или с проектами).

## 6) Минимальный ручной e2e сценарий

1. Открыть `http://127.0.0.1:5173` (StartPage).
2. Создать проект через UI или API.
3. Проверить, что проект появляется в `/api/v1/projects`.
4. Перейти на IDE-страницу проекта (`/ide/:projectId`).

### Пример создания проекта через API

```bash
curl -X POST http://127.0.0.1:8000/api/v1/projects \
  -H 'Content-Type: application/json' \
  -d '{
    "name":"demo-local",
    "description":"local run",
    "platform":"custom",
    "chip":"generic",
    "board":"generic",
    "toolchain":"gcc"
  }'
```

## 7) Runtime checklist

- [ ] Backend стартовал без traceback
- [ ] Frontend стартовал без traceback
- [ ] `GET /api/v1/health` отвечает `200`
- [ ] `GET /api/v1/projects` отвечает `200`
- [ ] Стартовая страница открывается в браузере
- [ ] IDE страница проекта открывается в браузере
