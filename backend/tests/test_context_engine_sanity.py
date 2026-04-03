from types import SimpleNamespace

from app.services.ai.ai_memory_service import AIMemoryService
from app.services.context.context_pipeline_service import ContextPipelineService
from app.services.context.project_context_retrieval_service import ProjectContextRetrievalService
from app.services.prompts.prompt_packer_service import PromptPackerService


class _FakeDB:
    pass


def test_token_packer_priority_and_drop() -> None:
    packer = PromptPackerService()
    fragments = [
        {'id': 'task', 'category': 'task_instruction', 'title': 'task', 'content': 'fix build', 'rank': 100},
        {'id': 'log', 'category': 'critical_log', 'title': 'log', 'content': 'E' * 6000, 'rank': 95},
        {'id': 'code', 'category': 'code_fragment', 'title': 'main.c', 'content': 'C' * 6000, 'rank': 80},
        {'id': 'warm', 'category': 'warm_memory', 'title': 'warm', 'content': 'W' * 6000, 'rank': 60},
    ]
    out = packer.pack(mode='quick_diagnosis', system_prompt='sys', task_text='fix build', fragments=fragments)
    assert out['included_fragments']
    assert out['budget_debug']['used_retrieval_tokens'] <= out['token_budget']['available_retrieval_budget']
    assert any(x['category'] == 'task_instruction' for x in out['included_fragments'])


def test_memory_ranking_layers_sanity() -> None:
    service = AIMemoryService(_FakeDB())
    service.list_typed = lambda project_id: [  # type: ignore[method-assign]
        {'key': 'successful_fix:a', 'memory_type': 'known_good_fix', 'title': 'uart fix', 'content': 'fix uart timeout', 'importance': 5, 'source': 'history', 'created_at': '2026-01-01'},
        {'key': 'project_summary:b', 'memory_type': 'project_summary', 'title': 'legacy', 'content': 'old note', 'importance': 1, 'source': 'history', 'created_at': '2025-01-01'},
    ]
    service._prompt_memory = lambda project_id: []  # type: ignore[method-assign]

    layers = service.get_memory_layers(1, task_text='fix uart timeout', include_cold=True)
    assert layers['active']
    assert isinstance(layers['cold'], list)


def test_retrieval_scoring_sanity() -> None:
    svc = ProjectContextRetrievalService(_FakeDB())
    score = svc._score_file(
        'src/main.c',
        file_type='source',
        task_tokens={'main', 'fix', 'uart'},
        task_file_mentions={'src/main.c'},
        opened_file_path='src/main.c',
        changed_files={'src/main.c'},
        failing_files={'src/main.c'},
        centrality={'src/main.c': 0.9},
        memory_refs={'src/main.c'},
        risky_files={'src/main.c'},
        successful_fix_files={'src/main.c'},
    )
    assert score.total > 50
    assert 'user-focus' in score.reasons


def test_project_isolation_sanity(monkeypatch) -> None:
    project = SimpleNamespace(id=42, path='.', name='p', platform='x', board='y', current_branch='main', current_version='1')

    called = {'project_ids': []}

    def fake_active(self, project_id, **kwargs):
        called['project_ids'].append(project_id)
        return [{'key': f'{project_id}:a'}]

    def fake_warm(self, project_id, **kwargs):
        called['project_ids'].append(project_id)
        return [{'key': f'{project_id}:w'}]

    monkeypatch.setattr(AIMemoryService, 'get_active_memory_for_task', fake_active)
    monkeypatch.setattr(AIMemoryService, 'get_relevant_warm_memory', fake_warm)
    monkeypatch.setattr(ProjectContextRetrievalService, 'retrieve', lambda self, project, **kwargs: SimpleNamespace(files=[], fragments=[]))
    monkeypatch.setattr(
        type(ContextPipelineService(_FakeDB())),
        'build',
        ContextPipelineService.build,
    )
    monkeypatch.setattr(
        __import__('app.services.context.context_source_registry', fromlist=['ContextSourceRegistry']).ContextSourceRegistry,
        'fetch_source_fragments',
        lambda self, project, **kwargs: [],
    )
    monkeypatch.setattr(
        __import__('app.services.prompts.prompt_service', fromlist=['PromptService']).PromptService,
        'get_current_prompt',
        lambda self, project_id: 'sys',
    )

    pipeline = ContextPipelineService(_FakeDB()).build(project, task_text='t', mode='quick_diagnosis')
    assert pipeline['report']['project_id'] == 42
    assert called['project_ids'] and all(pid == 42 for pid in called['project_ids'])
