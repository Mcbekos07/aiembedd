from __future__ import annotations

import json
import re
from collections import Counter, defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ai_memory_entry import AIMemoryEntry
from app.services.ai.ai_task_service import AITaskService
from app.services.build.build_service import BuildService
from app.services.history.history_service import HistoryService
from app.services.prompts.prompt_service import PromptService
from app.services.prompts.prompt_version_service import PromptVersionService


class AIMemoryService:
    MEMORY_TYPES = {
        'project_summary',
        'architecture_decision',
        'known_risky_file',
        'repeated_failure_pattern',
        'successful_fix',
        'known_good_fix',
        'important_runtime_note',
        'hardware_runtime_note',
        'hardware_specific_note',
        'dependency_toolchain_caveat',
        'build_caveat',
        'flash_caveat',
        'user_instruction',
        'prompt_rule',
        'project_invariant',
    }

    TYPE_ALIAS = {
        'known_good_fix': 'successful_fix',
        'hardware_runtime_note': 'important_runtime_note',
        'hardware_specific_note': 'important_runtime_note',
        'build_caveat': 'dependency_toolchain_caveat',
        'flash_caveat': 'dependency_toolchain_caveat',
    }

    TYPE_WEIGHT = {
        'project_summary': 1.0,
        'architecture_decision': 1.0,
        'known_risky_file': 0.9,
        'repeated_failure_pattern': 1.0,
        'successful_fix': 1.0,
        'important_runtime_note': 0.95,
        'dependency_toolchain_caveat': 0.85,
        'user_instruction': 1.0,
        'prompt_rule': 0.95,
        'project_invariant': 0.9,
    }

    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, project_id: int) -> list[AIMemoryEntry]:
        stmt = select(AIMemoryEntry).where(AIMemoryEntry.project_id == project_id).order_by(AIMemoryEntry.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def add(self, project_id: int, key: str, value: str) -> AIMemoryEntry:
        row = AIMemoryEntry(project_id=project_id, key=key, value=value)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def add_typed(
        self,
        project_id: int,
        memory_type: str,
        title: str,
        content: str,
        *,
        importance: int = 3,
        source: str = 'manual',
    ) -> AIMemoryEntry:
        norm = self._normalize_memory_type(memory_type)
        key = f'{norm}:{title.strip()[:80] or "untitled"}'
        payload = json.dumps({'content': content, 'importance': int(importance), 'source': source}, ensure_ascii=False)
        return self.add(project_id, key, payload)

    def list_typed(self, project_id: int) -> list[dict[str, object]]:
        typed: list[dict[str, object]] = []
        for item in self.list(project_id):
            m_type, title = self._split_key(item.key)
            parsed = self._parse_payload(item.value)
            typed.append(
                {
                    'key': item.key,
                    'memory_type': self._normalize_memory_type(m_type),
                    'title': title,
                    'content': parsed.get('content', item.value),
                    'importance': int(parsed.get('importance', 3)),
                    'source': str(parsed.get('source', 'manual')),
                    'created_at': item.created_at.isoformat(),
                }
            )
        return typed

    def query_context(self, project_id: int, memory_types: list[str] | None = None, limit: int = 30) -> list[dict[str, object]]:
        items = self.list_typed(project_id)
        if memory_types:
            allowed = {self._normalize_memory_type(x) for x in memory_types}
            items = [m for m in items if str(m['memory_type']) in allowed]
        items.sort(key=lambda x: (int(x.get('importance', 0)), x.get('created_at', '')), reverse=True)
        return items[:limit]

    def summary(self, project_id: int) -> str:
        items = self.query_context(project_id, limit=24)
        return '\n'.join([f"[{m['memory_type']}] {m['title']}: {m['content']}" for m in items])

    def summarize_by_type(self, project_id: int) -> dict[str, object]:
        grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
        for item in self.query_context(project_id, limit=200):
            grouped[str(item['memory_type'])].append(item)

        return {
            'counts': {k: len(v) for k, v in grouped.items()},
            'top_items': {
                k: [
                    {'title': str(x['title']), 'content': str(x['content']), 'importance': int(x['importance'])}
                    for x in sorted(v, key=lambda y: int(y.get('importance', 0)), reverse=True)[:5]
                ]
                for k, v in grouped.items()
            },
        }

    def get_memory_layers(
        self,
        project_id: int,
        *,
        task_text: str = '',
        opened_file_path: str | None = None,
        active_limit: int = 10,
        warm_limit: int = 20,
        cold_limit: int = 30,
        include_cold: bool = False,
    ) -> dict[str, list[dict[str, object]]]:
        base_items = self.list_typed(project_id)
        enriched = base_items + self._prompt_memory(project_id)

        scored = [self._score_memory_item(x, task_text=task_text, opened_file_path=opened_file_path) for x in enriched]
        ranked = sorted(scored, key=lambda x: x['score'], reverse=True)

        active = [x for x in ranked if x['score'] >= 65][:active_limit]
        warm_candidates = [x for x in ranked if x not in active]
        warm = [x for x in warm_candidates if x['score'] >= 35][:warm_limit]
        cold = [x for x in ranked if x not in active and x not in warm][:cold_limit] if include_cold else []

        return {
            'active': [self._strip_scoring(x) for x in active],
            'warm': [self._strip_scoring(x) for x in warm],
            'cold': [self._strip_scoring(x) for x in cold],
        }

    def get_active_memory_for_task(self, project_id: int, task_text: str = '', opened_file_path: str | None = None, limit: int = 10) -> list[dict[str, object]]:
        return self.get_memory_layers(
            project_id,
            task_text=task_text,
            opened_file_path=opened_file_path,
            active_limit=limit,
            warm_limit=0,
            include_cold=False,
        )['active']

    def get_relevant_warm_memory(self, project_id: int, task_text: str = '', opened_file_path: str | None = None, limit: int = 20) -> list[dict[str, object]]:
        return self.get_memory_layers(
            project_id,
            task_text=task_text,
            opened_file_path=opened_file_path,
            active_limit=10,
            warm_limit=limit,
            include_cold=False,
        )['warm']

    def fetch_cold_memory(self, project_id: int, task_text: str = '', opened_file_path: str | None = None, limit: int = 30) -> list[dict[str, object]]:
        return self.get_memory_layers(
            project_id,
            task_text=task_text,
            opened_file_path=opened_file_path,
            active_limit=10,
            warm_limit=20,
            cold_limit=limit,
            include_cold=True,
        )['cold']

    def compact_old_data(self, project_id: int, max_per_type: int = 25) -> dict[str, int]:
        typed = self.list_typed(project_id)
        grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
        for item in typed:
            grouped[str(item['memory_type'])].append(item)

        removed = 0
        for memory_type, entries in grouped.items():
            entries.sort(key=lambda x: x['created_at'], reverse=True)
            for stale in entries[max_per_type:]:
                key = str(stale['key'])
                row = self.db.query(AIMemoryEntry).filter(AIMemoryEntry.project_id == project_id, AIMemoryEntry.key == key).first()
                if row:
                    self.db.delete(row)
                    removed += 1
            if len(entries) > max_per_type:
                summary_text = f'Compacted {len(entries) - max_per_type} older records for {memory_type}.'
                self.add_typed(project_id, memory_type, 'compaction_summary', summary_text, importance=4, source='maintenance')

        self.db.commit()
        return {'removed': removed}

    def promote_history_events(self, project_id: int, limit: int = 20) -> int:
        events = HistoryService(self.db).list_events(project_id)[:limit]
        promoted = 0
        for event in events:
            title = (event.title or '').lower()
            details = event.details or ''
            if 'runtime' in title or 'flash' in title:
                self.add_typed(project_id, 'important_runtime_note', event.title[:80], details[:300], importance=4, source='history')
                promoted += 1
            elif 'build' in title:
                self.add_typed(project_id, 'dependency_toolchain_caveat', event.title[:80], details[:300], importance=3, source='history')
                promoted += 1
            elif 'patch' in title or 'fix' in title:
                self.add_typed(project_id, 'successful_fix', event.title[:80], details[:300], importance=4, source='history')
                promoted += 1
        return promoted

    def maintenance_summarize(self, project_id: int) -> dict[str, int]:
        created = 0
        created += self._summarize_old_agent_tasks(project_id)
        created += self._summarize_old_build_failures(project_id)
        created += self._summarize_repeated_fixes(project_id)
        return {'created': created}

    def _summarize_old_agent_tasks(self, project_id: int, keep_recent: int = 12) -> int:
        tasks = AITaskService(self.db).list(project_id)
        old = tasks[keep_recent:]
        if not old:
            return 0
        kinds = Counter(t.task_type for t in old)
        status = Counter(t.status for t in old)
        top_outputs = [t.output_text[:120] for t in old[:5] if t.output_text]
        content = f'task_types={dict(kinds)}; statuses={dict(status)}; samples={top_outputs}'
        self.add_typed(project_id, 'project_summary', 'old_agent_tasks_summary', content[:600], importance=3, source='maintenance')
        return 1

    def _summarize_old_build_failures(self, project_id: int, keep_recent: int = 8) -> int:
        jobs = BuildService(self.db).list_jobs(project_id)
        failed = [j for j in jobs if j.status == 'failed']
        old = failed[keep_recent:]
        if not old:
            return 0
        snippets = [j.error_summary[:160] for j in old[:8] if j.error_summary]
        content = f'old_failed_builds={len(old)}; repeated_patterns={snippets}'
        self.add_typed(project_id, 'repeated_failure_pattern', 'old_build_failures_summary', content[:600], importance=4, source='maintenance')
        return 1

    def _summarize_repeated_fixes(self, project_id: int) -> int:
        fixes = [x for x in self.list_typed(project_id) if str(x.get('memory_type')) == 'successful_fix']
        if len(fixes) < 3:
            return 0
        title_counter = Counter(str(x.get('title', '')).lower() for x in fixes)
        common = [f'{k} (x{v})' for k, v in title_counter.items() if v > 1][:10]
        if not common:
            return 0
        self.add_typed(project_id, 'successful_fix', 'repeated_fixes_summary', '; '.join(common), importance=4, source='maintenance')
        return 1

    def _prompt_memory(self, project_id: int) -> list[dict[str, object]]:
        current = PromptService(self.db).get_current_prompt(project_id)
        versions = PromptVersionService(self.db).list_versions(project_id)[:5]
        rows: list[dict[str, object]] = [
            {
                'key': 'prompt_rule:current_prompt',
                'memory_type': 'prompt_rule',
                'title': 'current_prompt',
                'content': current[:900],
                'importance': 4,
                'source': 'prompt',
                'created_at': versions[0].created_at.isoformat() if versions else '',
            }
        ]
        for row in versions:
            rows.append(
                {
                    'key': f'prompt_rule:{row.version}',
                    'memory_type': 'prompt_rule',
                    'title': row.version,
                    'content': row.prompt_text[:600],
                    'importance': 3,
                    'source': 'prompt',
                    'created_at': row.created_at.isoformat(),
                }
            )
        return rows

    def _score_memory_item(self, item: dict[str, object], *, task_text: str, opened_file_path: str | None) -> dict[str, object]:
        task_tokens = self._tokens(task_text)
        text = f"{item.get('title', '')} {item.get('content', '')}".lower()
        overlap = len(task_tokens.intersection(self._tokens(text)))
        relevance = min(1.0, overlap / 4)

        type_norm = self._normalize_memory_type(str(item.get('memory_type', 'project_summary')))
        type_weight = self.TYPE_WEIGHT.get(type_norm, 0.8)
        importance = min(1.0, int(item.get('importance', 3)) / 5)
        recency = 1.0
        focus = 1.0 if opened_file_path and opened_file_path.lower() in text else 0.0

        score = round(relevance * 40 + importance * 30 + type_weight * 20 + recency * 5 + focus * 5, 2)
        item2 = dict(item)
        item2['memory_type'] = type_norm
        item2['score'] = score
        item2['score_breakdown'] = {
            'relevance': relevance * 40,
            'importance': importance * 30,
            'type_weight': type_weight * 20,
            'recency': recency * 5,
            'focus': focus * 5,
        }
        return item2

    @staticmethod
    def _strip_scoring(item: dict[str, object]) -> dict[str, object]:
        return item

    def _normalize_memory_type(self, memory_type: str) -> str:
        raw = memory_type.strip().lower()
        raw = self.TYPE_ALIAS.get(raw, raw)
        return raw if raw in self.MEMORY_TYPES else 'project_summary'

    @staticmethod
    def _split_key(key: str) -> tuple[str, str]:
        if ':' not in key:
            return 'project_summary', key
        memory_type, title = key.split(':', 1)
        return memory_type, title

    @staticmethod
    def _parse_payload(value: str) -> dict[str, object]:
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
        return {'content': value, 'importance': 3, 'source': 'legacy'}

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {t for t in re.split(r'[^a-zA-Z0-9_./-]+', text.lower()) if len(t) >= 3}
