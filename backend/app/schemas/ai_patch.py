from pydantic import BaseModel, Field


class PatchChange(BaseModel):
    path: str
    new_content: str


class PatchProposalRequest(BaseModel):
    project_id: int
    reason: str
    summary: str = ''
    dangerous: bool = False
    changes: list[PatchChange] = Field(default_factory=list)


class PatchApplyRequest(BaseModel):
    confirmed: bool = False


class PatchActionResponse(BaseModel):
    patch_id: int
    status: str
    diff_preview: str = ''
    files: list[str] = Field(default_factory=list)
    git_status: str = ''
