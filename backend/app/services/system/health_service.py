"""System health service."""

from datetime import datetime, UTC


class HealthService:
    """Provides service and runtime health information."""

    @staticmethod
    def get_health() -> dict[str, str]:
        return {
            "status": "ok",
            "message": "Сервис работает стабильно",
            "timestamp": datetime.now(UTC).isoformat(),
        }
