from __future__ import annotations

from app.db.models.project import Project
from app.services.ai.ai_memory_service import AIMemoryService
from app.services.context.context_source_registry import ContextSourceRegistry
from app.services.context.project_context_retrieval_service import ProjectContextRetrievalService
from app.services.prompts.prompt_packer_service import PromptPackerService
from app.services.prompts.prompt_service import PromptService


class ContextPipelineService:
    def __init__(self, db: object) -> None:
        self.db = db

    def build(
        self,
        project: Project,
        *,
        task_text: str,
        mode: str,
        opened_file_path: str | None = None,
        opened_file_content: str | None = None,
    ) -> dict[str, object]:
        retrieval = ProjectContextRetrievalService(self.db).retrieve(
            project,
            task_text=task_text,
            opened_file_path=opened_file_path,
            opened_file_content=opened_file_content,
        )
        memory = AIMemoryService(self.db)
        active = memory.get_active_memory_for_task(project.id, task_text=task_text, opened_file_path=opened_file_path)
        warm = memory.get_relevant_warm_memory(project.id, task_text=task_text, opened_file_path=opened_file_path)

        sources = ContextSourceRegistry(self.db).fetch_source_fragments(
            project,
            source_types=['important_build_logs', 'important_runtime_logs', 'retrieval_top_history'],
            opened_file_path=opened_file_path,
            opened_file_content=opened_file_content,
            task_text=task_text,
        )

        fragments: list[dict[str, object]] = [
            {'id': 'task', 'category': 'task_instruction', 'title': 'task', 'content': task_text, 'rank': 100},
            {'id': 'active_memory', 'category': 'active_memory', 'title': 'active_memory', 'content': str(active), 'rank': 85},
            {'id': 'warm_memory', 'category': 'warm_memory', 'title': 'warm_memory', 'content': str(warm), 'rank': 65},
        ]

        for idx, item in enumerate(retrieval.fragments[:8]):
            fragments.append(
                {
                    'id': f'code_{idx}',
                    'category': 'code_fragment',
                    'title': item.path,
                    'path': item.path,
                    'content': item.snippet,
                    'rank': item.score.total,
                }
            )

        for src in sources:
            fragments.append(
                {
                    'id': src.source_type,
                    'category': 'critical_log' if src.source_type in {'important_build_logs', 'important_runtime_logs'} else 'git_history',
                    'title': src.source_type,
                    'content': src.content,
                    'rank': float(src.metadata.priority),
                }
            )

        system_prompt = PromptService(self.db).get_current_prompt(project.id)
        packed = PromptPackerService().pack(mode=mode, system_prompt=system_prompt, task_text=task_text, fragments=fragments)

        prompt_text = str(packed['final_context_payload']['prompt_text'])
        return {
            'prompt_text': prompt_text,
            'report': {
                'project_id': project.id,
                'mode': mode,
                'selected_files': [x.path for x in retrieval.files[:8]],
                'selected_files_with_relevance': [
                    {'path': x.path, 'score': x.score.total, 'reasons': x.score.reasons}
                    for x in retrieval.files[:8]
                ],
                'selected_logs': [x.source_type for x in sources if x.source_type in {'important_build_logs', 'important_runtime_logs'}],
                'selected_memory_counts': {'active': len(active), 'warm': len(warm)},
                'included_fragments': packed['included_fragments'],
                'dropped_fragments': packed['dropped_fragments'],
                'budget_debug': packed['budget_debug'],
                'final_size_chars': len(prompt_text),
            },
        }
