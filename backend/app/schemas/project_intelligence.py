from pydantic import BaseModel, Field


class ProjectIntelligenceRead(BaseModel):
    project_id: int
    summary: str
    architectural_notes: str
    important_files: list[str] = Field(default_factory=list)
    risky_files: list[str] = Field(default_factory=list)
    known_build_paths: list[str] = Field(default_factory=list)
    entry_points: list[str] = Field(default_factory=list)
    dependency_map: dict[str, list[str]] = Field(default_factory=dict)
    file_classification: dict[str, str] = Field(default_factory=dict)
