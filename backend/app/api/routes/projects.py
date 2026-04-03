"""Projects route definitions."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.common import MessageResponse
from app.schemas.project import ProjectCreateRequest, ProjectImportRequest, ProjectRead
from app.schemas.project_intelligence import ProjectIntelligenceRead
from app.services.project.project_delete_service import ProjectDeleteService
from app.services.project.project_intelligence_service import ProjectIntelligenceService
from app.services.project.project_service import ProjectService

router = APIRouter(prefix='/projects', tags=['projects'])


class DeleteRequest(BaseModel):
    mode: str = 'registry_only'  # registry_only | registry_with_history | full
    confirmed: bool = False


@router.get('', response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db_session)) -> list[ProjectRead]:
    return ProjectService(db).get_project_list()


@router.get('/{project_id}', response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db_session)) -> ProjectRead:
    service = ProjectService(db)
    try:
        return service.get_project_by_id(project_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Проект не найден') from exc


@router.get('/{project_id}/intelligence', response_model=ProjectIntelligenceRead)
def get_project_intelligence(project_id: int, refresh: bool = Query(False), db: Session = Depends(get_db_session)) -> ProjectIntelligenceRead:
    project = ProjectService(db).get_project_by_id(project_id)
    snapshot = ProjectIntelligenceService(db).get_or_refresh(project, refresh=refresh)
    return ProjectIntelligenceRead(
        project_id=snapshot.project_id,
        summary=snapshot.summary,
        architectural_notes=snapshot.architectural_notes,
        important_files=snapshot.important_files,
        risky_files=snapshot.risky_files,
        known_build_paths=snapshot.known_build_paths,
        entry_points=snapshot.entry_points,
        dependency_map=snapshot.dependency_map,
        file_classification=snapshot.file_classification,
    )


@router.post('', response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreateRequest, db: Session = Depends(get_db_session)) -> ProjectRead:
    return ProjectService(db).create_project(payload)


@router.post('/import-local', response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def import_local_project(payload: ProjectImportRequest, db: Session = Depends(get_db_session)) -> ProjectRead:
    return ProjectService(db).import_local_project(payload)


@router.delete('/{project_id}', response_model=MessageResponse)
def delete_project(project_id: int, payload: DeleteRequest, db: Session = Depends(get_db_session)) -> MessageResponse:
    try:
        ProjectDeleteService(db).execute(project_id, payload.mode, payload.confirmed)
        return MessageResponse(message='Проект удалён согласно выбранному режиму')
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Проект не найден') from exc
