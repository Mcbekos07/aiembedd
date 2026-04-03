# Architecture Overview

- Backend: FastAPI + SQLAlchemy + modular services + WebSocket channels.
- Frontend: Vue 3 + Pinia + router-driven IDE shell.
- Core domains: Projects, Files, Build, Git, Versions, History, Devices, AI.
- Integration strategy: all external systems wrapped by service abstraction layers.
