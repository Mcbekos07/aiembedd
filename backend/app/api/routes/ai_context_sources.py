from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.context_source import (
    ContextRetrievalRequest,
    ContextRetrievalResponse,
    ContextSourceFragmentsResponse,
    ContextSourceListResponse,
    ContextSourceQueryRequest,
    PromptPackRequest,
    PromptPackResponse,
)
from app.services.context.context_source_registry import ContextSourceRegistry
from app.services.context.context_pipeline_service import ContextPipelineService
from app.services.context.project_context_retrieval_service import ProjectContextRetrievalService
from app.services.project.project_service import ProjectService

router = APIRouter(prefix='/ai-context-sources', tags=['ai-context-sources'])


@router.get('/{project_id}', response_model=ContextSourceListResponse)
def list_sources(project_id: int, db: Session = Depends(get_db_session)) -> ContextSourceListResponse:
    project = ProjectService(db).get_project_by_id(project_id)
    items = ContextSourceRegistry(db).list_available_sources(project)
    return ContextSourceListResponse(items=items)


@router.post('/{project_id}/fragments', response_model=ContextSourceFragmentsResponse)
def fetch_fragments(project_id: int, payload: ContextSourceQueryRequest, db: Session = Depends(get_db_session)) -> ContextSourceFragmentsResponse:
    project = ProjectService(db).get_project_by_id(project_id)
    items = ContextSourceRegistry(db).fetch_source_fragments(
        project,
        source_types=payload.source_types,
        opened_file_path=payload.opened_file_path,
        opened_file_content=payload.opened_file_content,
        max_items_per_source=payload.max_items_per_source,
        task_text=payload.task_text,
    )
    return ContextSourceFragmentsResponse(items=items)


@router.post('/{project_id}/retrieve', response_model=ContextRetrievalResponse)
def retrieve_context(project_id: int, payload: ContextRetrievalRequest, db: Session = Depends(get_db_session)) -> ContextRetrievalResponse:
    project = ProjectService(db).get_project_by_id(project_id)
    result = ProjectContextRetrievalService(db).retrieve(
        project,
        task_text=payload.task_text,
        opened_file_path=payload.opened_file_path,
        opened_file_content=payload.opened_file_content,
        max_files=payload.max_files,
        max_fragments=payload.max_fragments,
        max_memory=payload.max_memory,
        max_history=payload.max_history,
    )
    return ContextRetrievalResponse(items=result)


@router.post('/{project_id}/pack', response_model=PromptPackResponse)
def pack_context(project_id: int, payload: PromptPackRequest, db: Session = Depends(get_db_session)) -> PromptPackResponse:
    project = ProjectService(db).get_project_by_id(project_id)
    pipeline = ContextPipelineService(db).build(
        project,
        task_text=payload.task_text,
        mode=payload.mode,
        opened_file_path=payload.opened_file_path,
        opened_file_content=payload.opened_file_content,
    )
    return PromptPackResponse(items={'final_context_payload': {'prompt_text': pipeline['prompt_text']}, 'report': pipeline['report']})
