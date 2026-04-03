from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services.files.file_service import FileService
from app.services.project.project_service import ProjectService

router = APIRouter(prefix='/files', tags=['files'])


class FilePathRequest(BaseModel):
    path: str


class FileSaveRequest(BaseModel):
    path: str
    content: str


class FileRenameRequest(BaseModel):
    old_path: str
    new_path: str


class FileCreateRequest(BaseModel):
    path: str
    kind: str = 'file'


@router.get('/{project_id}/tree')
def tree(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, object]:
    project = ProjectService(db).get_project_by_id(project_id)
    return {'status': 'ok', 'items': FileService().tree(project.path)}


@router.post('/{project_id}/read')
def read(project_id: int, payload: FilePathRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    try:
        content = FileService().read(project.path, payload.path)
        return {'status': 'ok', 'content': content}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post('/{project_id}/save')
def save(project_id: int, payload: FileSaveRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    FileService().save(project.path, payload.path, payload.content)
    return {'status': 'ok', 'message': 'Файл сохранён'}


@router.post('/{project_id}/rename')
def rename(project_id: int, payload: FileRenameRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    FileService().rename(project.path, payload.old_path, payload.new_path)
    return {'status': 'ok', 'message': 'Путь переименован'}


@router.post('/{project_id}/delete')
def delete(project_id: int, payload: FilePathRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    FileService().delete(project.path, payload.path)
    return {'status': 'ok', 'message': 'Удалено'}


@router.post('/{project_id}/create')
def create(project_id: int, payload: FileCreateRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    FileService().create(project.path, payload.path, payload.kind)
    return {'status': 'ok', 'message': 'Создано'}
