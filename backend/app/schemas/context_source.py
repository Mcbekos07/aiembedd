from pydantic import BaseModel, Field


class ContextSourceMeta(BaseModel):
    source_type: str
    project_scope: int
    freshness: str
    estimated_size: int
    priority: int
    retrievable: bool = True
    summary_available: bool = False


class ContextSourceFragment(BaseModel):
    source_type: str
    content: str
    metadata: ContextSourceMeta


class ContextSourceQueryRequest(BaseModel):
    source_types: list[str] = Field(default_factory=list)
    opened_file_path: str | None = None
    opened_file_content: str | None = None
    max_items_per_source: int = 5
    task_text: str = ''


class ContextSourceListResponse(BaseModel):
    items: list[ContextSourceMeta] = Field(default_factory=list)


class ContextSourceFragmentsResponse(BaseModel):
    items: list[ContextSourceFragment] = Field(default_factory=list)


class ContextRetrievalScore(BaseModel):
    total: float
    relevance_to_task: float
    recency: float
    build_runtime_relation: float
    centrality: float
    user_focus: float
    memory_importance: float
    weighted_breakdown: dict[str, float] = Field(default_factory=dict)
    reasons: list[str] = Field(default_factory=list)


class ContextRetrievalFileItem(BaseModel):
    path: str
    file_type: str
    score: ContextRetrievalScore
    snippet: str = ''


class ContextRetrievalMemoryItem(BaseModel):
    key: str
    memory_type: str
    title: str
    content: str
    score: ContextRetrievalScore


class ContextRetrievalHistoryItem(BaseModel):
    item_type: str
    title: str
    content: str
    score: ContextRetrievalScore


class ContextRetrievalResult(BaseModel):
    files: list[ContextRetrievalFileItem] = Field(default_factory=list)
    fragments: list[ContextRetrievalFileItem] = Field(default_factory=list)
    memory: list[ContextRetrievalMemoryItem] = Field(default_factory=list)
    history: list[ContextRetrievalHistoryItem] = Field(default_factory=list)


class ContextRetrievalRequest(BaseModel):
    task_text: str = ''
    opened_file_path: str | None = None
    opened_file_content: str | None = None
    max_files: int = 8
    max_fragments: int = 8
    max_memory: int = 8
    max_history: int = 8


class ContextRetrievalResponse(BaseModel):
    items: ContextRetrievalResult


class PromptPackRequest(BaseModel):
    mode: str = 'quick_diagnosis'
    task_text: str = ''
    opened_file_path: str | None = None
    opened_file_content: str | None = None


class PromptPackResponse(BaseModel):
    items: dict[str, object]
