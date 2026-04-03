"""Common API response schemas."""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    status: str = "ok"
    message: str
