from pydantic import BaseModel, Field


class DiagnosisRequest(BaseModel):
    task_text: str = ''
    mode: str = 'deep_build_fix'
    opened_file_path: str | None = None
    opened_file_content: str | None = None


class DiagnosisResult(BaseModel):
    problem_summary: str
    probable_cause: str
    impacted_files: list[str] = Field(default_factory=list)
    confidence_level: str
    recommended_fix_actions: list[str] = Field(default_factory=list)
    safe_auto_fix_possible: bool
