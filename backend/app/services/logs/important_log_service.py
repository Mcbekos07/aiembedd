"""Important log extraction for build/flash/runtime diagnostics."""

from __future__ import annotations

import re


class ImportantLogService:
    COMPILER_RE = re.compile(
        r'(?P<file>[\w./\\-]+):(?P<line>\d+):(?:(?P<col>\d+):)?\s*(?P<level>fatal error|error|warning):\s*(?P<message>.+)',
        re.IGNORECASE,
    )

    def extract(self, raw: str, limit: int = 120) -> list[str]:
        events = self.extract_events(raw, limit=limit)
        lines: list[str] = []
        for event in events:
            file_ref = f"{event.get('file')}:{event.get('line')}" if event.get('file') else '-'
            lines.append(f"[{event['stage']}/{event['error_type']}] {file_ref} :: {event['message']}")
        return lines

    def extract_events(self, raw: str, limit: int = 120) -> list[dict[str, object]]:
        events: list[dict[str, object]] = []
        for idx, line in enumerate(raw.splitlines()):
            event = self._to_event(idx + 1, line)
            if event:
                events.append(event)
            if len(events) >= limit:
                break
        return events

    def deduplicate_lines(self, raw: str, max_lines: int = 1200) -> list[str]:
        seen: dict[str, int] = {}
        compact: list[str] = []
        for line in raw.splitlines()[-max_lines:]:
            line_norm = line.strip()
            if not line_norm:
                continue
            count = seen.get(line_norm, 0)
            seen[line_norm] = count + 1
            if count == 0:
                compact.append(line_norm)
            elif count in {1, 4, 9}:
                compact.append(f'{line_norm} (repeated x{count + 1})')
        return compact

    def last_meaningful_lines_before_failure(self, raw: str, events: list[dict[str, object]], window: int = 16) -> list[str]:
        lines = [line for line in raw.splitlines() if line.strip()]
        if not lines:
            return []
        failure_row = next((int(e['row']) for e in events if str(e.get('severity')) == 'critical'), len(lines))
        start = max(0, failure_row - window - 1)
        return lines[start:failure_row]

    def _to_event(self, row: int, line: str) -> dict[str, object] | None:
        lowered = line.lower()

        compiler = self.COMPILER_RE.search(line)
        if compiler:
            level = str(compiler.group('level')).lower()
            return {
                'row': row,
                'stage': 'compile',
                'error_type': 'compiler_error' if 'error' in level else 'warning',
                'severity': 'critical' if 'error' in level else 'warning',
                'message': compiler.group('message').strip(),
                'file': compiler.group('file'),
                'line': int(compiler.group('line')),
                'raw': line,
            }

        if 'undefined reference' in lowered or 'collect2:' in lowered or 'ld:' in lowered:
            return self._base_event(row, 'link', 'linker_error', 'critical', line)

        if any(token in lowered for token in ('openocd', 'avrdude', 'esptool', 'stlink')) and any(
            token in lowered for token in ('error', 'failed', 'timeout', 'no device', 'cannot')
        ):
            return self._base_event(row, 'flash', 'flash_error', 'critical', line)

        runtime_category = self._runtime_category(lowered)
        if runtime_category:
            severity = 'critical' if runtime_category in {'boot_failure', 'repeated_crash', 'assert_panic', 'init_error'} else 'warning'
            return self._base_event(row, 'runtime', runtime_category, severity, line)

        if 'warning' in lowered:
            return self._base_event(row, 'compile', 'warning', 'warning', line)

        return None

    def _runtime_category(self, lowered: str) -> str | None:
        if any(token in lowered for token in ('boot fail', 'boot failed', 'boot error', 'failed to boot')):
            return 'boot_failure'
        if any(token in lowered for token in ('serial timeout', 'uart timeout', 'timeout waiting serial')):
            return 'serial_timeout'
        if any(token in lowered for token in ('rebooting', 'watchdog reset', 'guru meditation', 'hardfault', 'segmentation fault')):
            return 'repeated_crash'
        if any(token in lowered for token in ('assert', 'panic', 'traceback', 'exception')):
            return 'assert_panic'
        if any(token in lowered for token in ('init error', 'initialization failed', 'failed to init', 'sensor init fail')):
            return 'init_error'
        if any(token in lowered for token in ('no expected output', 'expected output missing')):
            return 'no_expected_output'
        return None

    @staticmethod
    def _base_event(row: int, stage: str, error_type: str, severity: str, line: str) -> dict[str, object]:
        return {
            'row': row,
            'stage': stage,
            'error_type': error_type,
            'severity': severity,
            'message': line.strip(),
            'file': None,
            'line': None,
            'raw': line,
        }
