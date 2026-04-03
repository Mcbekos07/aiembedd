from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models.project import Project
from app.schemas.context_source import (
    ContextRetrievalFileItem,
    ContextRetrievalHistoryItem,
    ContextRetrievalMemoryItem,
    ContextRetrievalResult,
    ContextRetrievalScore,
)
from app.services.ai.ai_memory_service import AIMemoryService
from app.services.ai.ai_task_service import AITaskService
from app.services.build.build_service import BuildService
from app.services.git.git_service import GitService
from app.services.history.history_service import HistoryService
from app.services.logs.important_log_service import ImportantLogService
from app.services.project.project_intelligence_service import ProjectIntelligenceService


class ProjectContextRetrievalService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def retrieve(
        self,
        project: Project,
        *,
        task_text: str = '',
        opened_file_path: str | None = None,
        opened_file_content: str | None = None,
        max_files: int = 8,
        max_fragments: int = 8,
        max_memory: int = 8,
        max_history: int = 8,
    ) -> ContextRetrievalResult:
        snapshot = ProjectIntelligenceService(self.db).get_or_refresh(project, refresh=False)
        task_tokens = self._tokens(task_text)
        task_file_mentions = set(self._extract_file_mentions(task_text))
        changed_files = set(self._changed_files(project.path, limit=80))
        failing_files = set(self._failing_files(project.id))
        successful_fix_files = set(self._successful_fix_files(project.id))
        centrality = self._graph_centrality(snapshot.dependency_map or {})
        memory_refs = self._memory_file_refs(project.id)

        file_items: list[ContextRetrievalFileItem] = []
        for rel_path, file_type in (snapshot.file_classification or {}).items():
            score = self._score_file(
                rel_path,
                file_type=file_type,
                task_tokens=task_tokens,
                task_file_mentions=task_file_mentions,
                opened_file_path=opened_file_path,
                changed_files=changed_files,
                failing_files=failing_files,
                centrality=centrality,
                memory_refs=memory_refs,
                risky_files=set(snapshot.risky_files or []),
                successful_fix_files=successful_fix_files,
            )
            snippet = self._snippet(project.path, rel_path, opened_file_path, opened_file_content)
            file_items.append(ContextRetrievalFileItem(path=rel_path, file_type=file_type, score=score, snippet=snippet))

        ranked_files = sorted(file_items, key=lambda x: x.score.total, reverse=True)[:max_files]
        ranked_fragments = sorted(file_items, key=lambda x: x.score.total, reverse=True)[:max_fragments]

        memory_items = self._rank_memory(project.id, task_tokens=task_tokens, failing_files=failing_files, limit=max_memory)
        history_items = self._rank_history(project, task_tokens=task_tokens, failing_files=failing_files, limit=max_history)

        return ContextRetrievalResult(
            files=ranked_files,
            fragments=ranked_fragments,
            memory=memory_items,
            history=history_items,
        )

    def _score_file(
        self,
        rel_path: str,
        *,
        file_type: str,
        task_tokens: set[str],
        task_file_mentions: set[str],
        opened_file_path: str | None,
        changed_files: set[str],
        failing_files: set[str],
        centrality: dict[str, float],
        memory_refs: set[str],
        risky_files: set[str],
        successful_fix_files: set[str],
    ) -> ContextRetrievalScore:
        rel_low = rel_path.lower()
        name_tokens = self._tokens(rel_low.replace('/', ' '))

        task_overlap = min(1.0, len(task_tokens.intersection(name_tokens)) / max(1, len(task_tokens)))
        task_file_hit = 1.0 if rel_low in task_file_mentions else 0.0
        user_focus = 1.0 if opened_file_path and rel_low == opened_file_path.lower() else task_file_hit
        build_runtime_relation = 1.0 if rel_low in failing_files else 0.0
        recency = 1.0 if rel_low in changed_files else 0.0
        graph_centrality = float(centrality.get(rel_path, 0.0))
        memory_importance = 1.0 if rel_low in memory_refs else 0.0
        risky = 0.4 if rel_low in risky_files else 0.0
        prior_fix = 0.8 if rel_low in successful_fix_files else 0.0

        relevance_to_task = min(1.0, task_overlap + task_file_hit)

        weighted = {
            'relevance_to_task': relevance_to_task * 40,
            'recency': recency * 15,
            'build_runtime_relation': build_runtime_relation * 18,
            'centrality': graph_centrality * 10,
            'user_focus': user_focus * 20,
            'memory_importance': memory_importance * 10,
            'risky_bonus': risky * 8,
            'previous_fix_bonus': prior_fix * 8,
        }
        total = round(sum(weighted.values()), 2)

        reasons: list[str] = []
        if user_focus > 0:
            reasons.append('user-focus')
        if build_runtime_relation > 0:
            reasons.append('mentioned-in-failing-logs')
        if recency > 0:
            reasons.append('recent-changes')
        if relevance_to_task > 0:
            reasons.append('task-overlap')
        if memory_importance > 0:
            reasons.append('known-from-memory')
        if rel_low in risky_files:
            reasons.append('risky-file')
        if rel_low in successful_fix_files:
            reasons.append('previous-successful-fix')
        if file_type in {'main/entry', 'build'}:
            reasons.append('critical-project-role')

        return ContextRetrievalScore(
            total=total,
            relevance_to_task=round(relevance_to_task, 3),
            recency=round(recency, 3),
            build_runtime_relation=round(build_runtime_relation, 3),
            centrality=round(graph_centrality, 3),
            user_focus=round(user_focus, 3),
            memory_importance=round(memory_importance, 3),
            weighted_breakdown=weighted,
            reasons=reasons,
        )

    def _rank_memory(self, project_id: int, *, task_tokens: set[str], failing_files: set[str], limit: int) -> list[ContextRetrievalMemoryItem]:
        layers = AIMemoryService(self.db).get_memory_layers(project_id, task_text=' '.join(sorted(task_tokens)), include_cold=False)
        typed = layers['active'] + layers['warm']
        ranked: list[ContextRetrievalMemoryItem] = []
        for item in typed:
            content = str(item.get('content', ''))
            title = str(item.get('title', ''))
            text = f'{title} {content}'.lower()
            overlap = len(task_tokens.intersection(self._tokens(text)))
            build_relation = 1.0 if any(path in text for path in failing_files) else 0.0
            importance = min(1.0, int(item.get('importance', 0)) / 5.0)
            base_score = float(item.get('score', 0.0))
            score = ContextRetrievalScore(
                total=round(base_score + build_relation * 10 + min(1.0, overlap / 4) * 10, 2),
                relevance_to_task=round(min(1.0, overlap / 4), 3),
                recency=1.0,
                build_runtime_relation=build_relation,
                centrality=0.0,
                user_focus=0.0,
                memory_importance=importance,
                weighted_breakdown={
                    'layer_score': base_score,
                    'task_overlap_bonus': min(1.0, overlap / 4) * 10,
                    'build_relation_bonus': build_relation * 10,
                },
                reasons=['active-or-warm-memory', 'task-overlap'] if overlap else ['active-or-warm-memory'],
            )
            ranked.append(
                ContextRetrievalMemoryItem(
                    key=str(item.get('key', '')),
                    memory_type=str(item.get('memory_type', '')),
                    title=title,
                    content=content[:700],
                    score=score,
                )
            )
        return sorted(ranked, key=lambda x: x.score.total, reverse=True)[:limit]

    def _rank_history(self, project: Project, *, task_tokens: set[str], failing_files: set[str], limit: int) -> list[ContextRetrievalHistoryItem]:
        rows: list[ContextRetrievalHistoryItem] = []

        for event in HistoryService(self.db).list_events(project.id)[: max(12, limit * 2)]:
            text = f'{event.title} {event.details}'.lower()
            overlap = len(task_tokens.intersection(self._tokens(text)))
            build_relation = 1.0 if any(path in text for path in failing_files) else 0.0
            score = ContextRetrievalScore(
                total=round(min(1.0, overlap / 4) * 55 + build_relation * 25 + 20, 2),
                relevance_to_task=round(min(1.0, overlap / 4), 3),
                recency=1.0,
                build_runtime_relation=build_relation,
                centrality=0.0,
                user_focus=0.0,
                memory_importance=0.0,
                weighted_breakdown={
                    'task_overlap': min(1.0, overlap / 4) * 55,
                    'build_relation': build_relation * 25,
                    'recency': 20,
                },
                reasons=['history-event', 'task-overlap'] if overlap else ['history-event'],
            )
            rows.append(
                ContextRetrievalHistoryItem(
                    item_type='history',
                    title=event.title,
                    content=(event.details or '')[:500],
                    score=score,
                )
            )

        commits = self._recent_commits(project.path, limit=max(6, limit))
        for commit in commits:
            low = commit.lower()
            overlap = len(task_tokens.intersection(self._tokens(low)))
            score = ContextRetrievalScore(
                total=round(min(1.0, overlap / 3) * 65 + 25, 2),
                relevance_to_task=round(min(1.0, overlap / 3), 3),
                recency=1.0,
                build_runtime_relation=0.0,
                centrality=0.0,
                user_focus=0.0,
                memory_importance=0.0,
                weighted_breakdown={'task_overlap': min(1.0, overlap / 3) * 65, 'recency': 25},
                reasons=['git-history', 'task-overlap'] if overlap else ['git-history'],
            )
            rows.append(ContextRetrievalHistoryItem(item_type='git', title='commit', content=commit, score=score))

        return sorted(rows, key=lambda x: x.score.total, reverse=True)[:limit]

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {t for t in re.split(r'[^a-zA-Z0-9_./-]+', text.lower()) if len(t) >= 3}

    @staticmethod
    def _extract_file_mentions(text: str) -> list[str]:
        matches = re.findall(r'([\w./-]+\.(?:c|cpp|cc|h|hpp|py|ts|js|vue|json|toml|ini|yaml|yml|md|sh))', text, flags=re.IGNORECASE)
        return [m.lower() for m in matches]

    @staticmethod
    def _graph_centrality(dep_map: dict[str, list[str]]) -> dict[str, float]:
        if not dep_map:
            return {}
        counts: dict[str, int] = {}
        for node, deps in dep_map.items():
            counts[node] = counts.get(node, 0) + len(deps)
            for dep in deps:
                counts[dep] = counts.get(dep, 0) + 1
        max_count = max(counts.values()) if counts else 1
        return {k: v / max_count for k, v in counts.items()}

    @staticmethod
    def _changed_files(repo_path: str, limit: int) -> list[str]:
        try:
            status = GitService().run(repo_path, ['status', '--short'])
        except Exception:
            return []
        lines = [line.strip() for line in status.splitlines() if line.strip()]
        files = [line[3:].strip().lower() for line in lines if len(line) > 3]
        return files[:limit]

    def _failing_files(self, project_id: int) -> list[str]:
        jobs = BuildService(self.db).list_jobs(project_id)
        failed = [j for j in jobs if j.status == 'failed'][:2]
        files: set[str] = set()
        extractor = ImportantLogService()
        for job in failed:
            raw = ''
            try:
                if job.log_path:
                    raw = Path(job.log_path).read_text(encoding='utf-8')
            except Exception:
                raw = ''
            if not raw:
                raw = job.error_summary or ''
            for event in extractor.extract_events(raw, limit=40):
                file_ref = event.get('file')
                if isinstance(file_ref, str) and file_ref:
                    files.add(file_ref.lower())
                msg = str(event.get('message', '')).lower()
                files.update(self._extract_file_mentions(msg))
        return sorted(files)

    def _successful_fix_files(self, project_id: int) -> list[str]:
        files: set[str] = set()
        for event in HistoryService(self.db).list_events(project_id)[:40]:
            if 'fix' not in event.title.lower() and 'patch' not in event.title.lower():
                continue
            files.update(self._extract_file_mentions(event.details or ''))

        for task in AITaskService(self.db).list(project_id)[:40]:
            if task.status != 'succeeded':
                continue
            files.update(self._extract_file_mentions(task.output_text or ''))
        return sorted(files)

    def _memory_file_refs(self, project_id: int) -> set[str]:
        refs: set[str] = set()
        for entry in AIMemoryService(self.db).list_typed(project_id):
            refs.update(self._extract_file_mentions(str(entry.get('content', ''))))
            refs.update(self._extract_file_mentions(str(entry.get('title', ''))))
        return refs

    def _snippet(self, repo_path: str, rel_path: str, opened_file_path: str | None, opened_file_content: str | None) -> str:
        if opened_file_path and opened_file_content is not None and rel_path.lower() == opened_file_path.lower():
            return opened_file_content[:1200]
        try:
            text = Path(repo_path, rel_path).read_text(encoding='utf-8', errors='ignore')
            return text[:1200]
        except Exception:
            return ''

    @staticmethod
    def _recent_commits(repo_path: str, limit: int) -> list[str]:
        try:
            output = GitService().run(repo_path, ['log', '--oneline', f'-n{max(1, limit)}'])
            return [line.strip() for line in output.splitlines() if line.strip()]
        except Exception:
            return []
