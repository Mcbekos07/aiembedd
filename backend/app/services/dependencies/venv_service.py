import venv
from pathlib import Path


class VenvService:
    def create(self, path: str) -> str:
        target = Path(path)
        target.mkdir(parents=True, exist_ok=True)
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(str(target))
        return str(target)
