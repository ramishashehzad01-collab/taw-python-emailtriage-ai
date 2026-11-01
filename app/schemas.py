from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class EmailCreate(BaseModel):
    sender: str = Field(min_length=3, max_length=320)
    subject: str = Field(default="(no subject)", max_length=500)
    body: str = Field(min_length=1, max_length=30000)


class TriageResult(BaseModel):
    category: str
    priority: str
    summary: str
    draft_reply: str


class EmailRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    gmail_id: str | None
    gmail_draft_id: str | None
    thread_id: str | None
    sender: str
    subject: str
    body: str
    category: str
    priority: str
    summary: str
    draft_reply: str
    status: str
    created_at: datetime


class DraftUpdate(BaseModel):
    draft_reply: str = Field(min_length=1, max_length=10000)
