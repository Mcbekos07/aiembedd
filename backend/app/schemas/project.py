"""Schemas for project API."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import ProjectSourceType


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    description: str = ""
    platform: str = "custom"
    chip: str = ""
    board: str = ""
    build_system: str = "custom"
    toolchain: str = ""


class ProjectImportRequest(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    local_path: str
    description: str = ""
    platform: str = "custom"


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str
    path: str
    source_type: ProjectSourceType | str
    platform: str
    chip: str
    board: str
    build_system: str
    toolchain: str
    current_branch: str
    current_version: str
    default_programmer: str
    default_port: str
    ai_provider: str
    ai_model: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
