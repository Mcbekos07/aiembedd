"""Build/flash/runtime log summarization helpers for UI and AI context."""

from __future__ import annotations

from collections import Counter, defaultdict

from app.services.logs.important_log_service import ImportantLogService


class LogSummaryService:
    def summarize(self, events: list[dict[str, object]]) -> dict[str, object]:
        if not events:
            return {
                'important_summary': 'Критичных фрагментов не найдено.',
                'root_cause': '',
                'repeated_warnings': [],
                'counts': {},
                'grouped_errors': {},
            }

        type_counter = Counter(str(e['error_type']) for e in events)
        warning_counter = Counter(str(e['message']) for e in events if e.get('error_type') == 'warning')
        repeated_warnings = [f'{message} (x{count})' for message, count in warning_counter.items() if count > 1][:20]

        grouped_errors: dict[str, list[str]] = defaultdict(list)
        for event in events:
            key = f"{event.get('stage')}::{event.get('file') or '-'}"
            grouped_errors[key].append(str(event.get('message', '')))

        root = next((e for e in events if str(e.get('severity')) == 'critical'), events[0])
        root_cause = str(root.get('message', ''))

        counts_text = ', '.join(f'{k}: {v}' for k, v in sorted(type_counter.items()))
        important_summary = f'Найдено {len(events)} важных событий ({counts_text}). Вероятная первопричина: {root_cause}'

        return {
            'important_summary': important_summary,
            'root_cause': root_cause,
            'repeated_warnings': repeated_warnings,
            'counts': dict(type_counter),
            'grouped_errors': {k: v[:5] for k, v in grouped_errors.items()},
        }

    def ai_ready_context(self, events: list[dict[str, object]], last_n_critical: int = 12) -> str:
        critical = [e for e in events if str(e.get('severity')) == 'critical']
        tail = critical[-last_n_critical:]
        lines = [
            f"[{e['stage']}/{e['error_type']}] row={e['row']} file={e.get('file') or '-'} line={e.get('line') or '-'} :: {e['message']}"
            for e in tail
        ]
        return '\n'.join(lines)

    def compress(self, raw_log: str, events: list[dict[str, object]], max_ai_lines: int = 36) -> dict[str, object]:
        extractor = ImportantLogService()
        dedup = extractor.deduplicate_lines(raw_log)
        tail = extractor.last_meaningful_lines_before_failure(raw_log, events)
        summary = self.summarize(events)

        stage_file_groups = self._group_by_stage_and_file(events)
        runtime_summary = self._runtime_summary(events)
        root_hints = self._root_cause_hints(events, summary.get('root_cause', ''))

        important_lines = extractor.extract(raw_log, limit=140)
        compact_lines: list[str] = []
        compact_lines.append(f"root_cause: {summary.get('root_cause', '') or 'n/a'}")
        compact_lines.extend([f"hint: {hint}" for hint in root_hints[:4]])
        if runtime_summary:
            compact_lines.extend([f"runtime: {line}" for line in runtime_summary])

        for group in stage_file_groups[:12]:
            compact_lines.append(group)

        compact_lines.append('last_meaningful_before_failure:')
        compact_lines.extend(tail[-10:])

        ai_lines = compact_lines[:max_ai_lines]
        impacted_files = sorted({str(e.get('file')) for e in events if e.get('file')})[:20]
        stages = sorted({str(e.get('stage')) for e in events if e.get('stage')})

        return {
            'raw': {'line_count': len(raw_log.splitlines()), 'preview': '\n'.join(raw_log.splitlines()[:20])},
            'important': {
                'line_count': len(important_lines),
                'preview': '\n'.join(important_lines[:40]),
                'events': events[:120],
                'deduplicated_preview': '\n'.join(dedup[:40]),
            },
            'compressed_ai_context': '\n'.join(ai_lines),
            'root_cause_summary': {
                'summary': summary.get('important_summary', ''),
                'root_cause': summary.get('root_cause', ''),
                'hints': root_hints,
                'grouped_errors': stage_file_groups,
                'runtime': runtime_summary,
            },
            'links': {
                'impacted_files': impacted_files,
                'pipeline_stages': stages,
                'probable_source_modules': [self._module_from_path(path) for path in impacted_files[:12]],
            },
        }

    def _group_by_stage_and_file(self, events: list[dict[str, object]]) -> list[str]:
        grouped: dict[tuple[str, str], list[str]] = defaultdict(list)
        for event in events:
            key = (str(event.get('stage', '-')), str(event.get('file') or '-'))
            grouped[key].append(str(event.get('message', '')))

        rows: list[str] = []
        for (stage, file_ref), messages in grouped.items():
            uniq = []
            seen = set()
            for message in messages:
                if message in seen:
                    continue
                seen.add(message)
                uniq.append(message)
            prefix = self._stage_prefix(stage)
            rows.append(f"{prefix} {file_ref}: " + ' | '.join(uniq[:3]))
        return rows

    @staticmethod
    def _stage_prefix(stage: str) -> str:
        return {
            'compile': '[COMPILE]',
            'link': '[LINKER]',
            'runtime': '[RUNTIME]',
            'flash': '[FLASH]',
        }.get(stage, '[GENERIC]')

    def _runtime_summary(self, events: list[dict[str, object]]) -> list[str]:
        runtime = [e for e in events if str(e.get('stage')) == 'runtime']
        if not runtime:
            return []
        kinds = Counter(str(e.get('error_type')) for e in runtime)
        rows: list[str] = []
        if kinds.get('boot_failure'):
            rows.append(f"boot failure signals: {kinds['boot_failure']}")
        if kinds.get('assert_panic'):
            rows.append(f"panic/assert signals: {kinds['assert_panic']}")
        if kinds.get('serial_timeout'):
            rows.append(f"timeout signals: {kinds['serial_timeout']}")
        if kinds.get('no_expected_output'):
            rows.append(f"missing expected output signals: {kinds['no_expected_output']}")
        if kinds.get('repeated_crash'):
            rows.append(f"repeated crash signals: {kinds['repeated_crash']}")
        return rows

    @staticmethod
    def _root_cause_hints(events: list[dict[str, object]], root_cause: str) -> list[str]:
        hints: list[str] = []
        low = root_cause.lower()
        if 'undefined reference' in low or any(str(e.get('error_type')) == 'linker_error' for e in events):
            hints.append('Проверьте реализацию/линковку функций и соответствие сигнатур между declaration/definition.')
        if any(str(e.get('stage')) == 'compile' for e in events):
            hints.append('Проверьте include/import цепочки и соответствие типов/символов в затронутых файлах.')
        if any(str(e.get('stage')) == 'flash' for e in events):
            hints.append('Проверьте подключение устройства, порт и flasher-параметры.')
        if any(str(e.get('stage')) == 'runtime' for e in events):
            hints.append('Проверьте инициализацию и порядок старта модулей перед падением runtime.')
        if not hints:
            hints.append('Нужно больше диагностических данных: проверьте хвост лога перед первой критичной ошибкой.')
        return hints

    @staticmethod
    def _module_from_path(path: str) -> str:
        if '/' not in path:
            return path
        return '/'.join(path.split('/')[:-1]) or path
