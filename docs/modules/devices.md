# Devices module (backend)

## Назначение
Обнаружение устройств/портов и подготовка данных для monitor/flash.

## Код
- API: `backend/app/api/routes/devices.py`
- Сервисы: `backend/app/services/devices/*`
- WS: `backend/app/api/ws/devices_ws.py`

## Что делает
- Сканирование USB/портов.
- Разрешение доступного порта и связки с programmer.

## Связи
- `build`/`flash` (прошивка)
- `logs`/`monitor` (runtime serial)
- frontend selectors устройств/портов
