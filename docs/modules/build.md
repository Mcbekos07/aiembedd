# Build module (backend)

## Назначение
Запуск build-пайплайна, подготовка/очистка/пересборка, сбор артефактов и базовая интеграция прошивки.

## Код
- API: `backend/app/api/routes/builds.py`, `flash.py`
- Сервисы: `backend/app/services/build/*`, `backend/app/services/flash/*`
- Модели: `backend/app/db/models/build_job.py`, `artifact.py`, `flash_job.py`

## Что делает
- Операции `prepare/build/clean/rebuild`.
- Сохранение статуса build jobs.
- Flash-операции через toolchain/flasher слой.

## Связи
- `logs` (build output и сводки)
- `devices` (port/programmer)
- `toolchains` (адаптеры/flashers)
- `ai` (compile-fix и build-assist сценарии, partial)
