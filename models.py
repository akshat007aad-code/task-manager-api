from sqlalchemy import Column, Integer, String
from database import Base
from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
 
VALID_STATUSES   = {"pending", "in-progress", "done"}
VALID_PRIORITIES = {"low", "medium", "high"}
 
 
# Database model (SQLAlchemy)
class TaskDB(Base):
    __tablename__ = "tasks"
 
    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String, nullable=False)
    description  = Column(String, nullable=True)
    status       = Column(String, default="pending")
    priority     = Column(String, default="medium")
    due_date     = Column(String, nullable=True)
    completed_at = Column(String, nullable=True)
 
 
# Pydantic models (API validation) — Pydantic V2 style
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "pending"
    priority: str = "medium"
    due_date: Optional[str] = None
 
    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()
 
    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v):
        if v not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
        return v
 
    @field_validator("priority")
    @classmethod
    def priority_must_be_valid(cls, v):
        if v not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(VALID_PRIORITIES)}")
        return v
 
 
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[str] = None
    completed_at: Optional[str] = None
 
    model_config = ConfigDict(from_attributes=True)