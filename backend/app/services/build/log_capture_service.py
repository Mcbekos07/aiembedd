from pathlib import Path


class LogCaptureService:
    def append(self, log_path: Path, line: str) -> None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open('a', encoding='utf-8') as fp:
            fp.write(line + '\n')
