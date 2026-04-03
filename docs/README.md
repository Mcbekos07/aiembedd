# Документация AIEmbedd

Кодовая база — browser-based embedded agent platform: FastAPI backend + Vue3 frontend + AI/context/build/git/log/device модули.

## Как устроена система (кратко)
- **Backend (`backend/app`)**: REST API, WebSocket каналы, сервисные слои (AI/build/git/files/logs/context и т.д.), SQLAlchemy модели.
- **Frontend (`frontend/src/app`)**: layouts/pages/components, Pinia stores, REST/WS клиенты, инженерный UX для manual + AI сценариев.
- **Agent layer**: задачи/действия/патчи/контекст через `app.services.ai.*` и UI-панели в `frontend/src/app/components/ai/*`.
- **Context engine**: упаковка контекста и выбор источников через `app.services.context.*` и `app.services.prompts.*`.

## Навигация по документам
- Архитектура: [architecture/system_overview.md](./architecture/system_overview.md)
- API: [api/README.md](./api/README.md)
- Модули: [modules/README.md](./modules/README.md)
- Агент: [agent/README.md](./agent/README.md)
- Контекст: [context/README.md](./context/README.md)
- UX: [ux/frontend_v2.md](./ux/frontend_v2.md)
- Workflows: [workflows/README.md](./workflows/README.md)
- Deployment: [deployment/README.md](./deployment/README.md)
- Dev: [dev/README.md](./dev/README.md)

> Принцип: описываем только реализованное в текущей кодовой базе; спорные места помечаем как `partial`/`TODO`.
