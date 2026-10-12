from datetime import datetime

from pydantic import BaseModel, field_validator


class TicketRequest(BaseModel):
    student_name: str
    location: str
    issue_type: str
    description: str


class TicketResponse(BaseModel):
    id: int
    student_name: str
    location: str
    issue_type: str
    description: str
    status: str
    created_at: datetime
    priority: str


class TicketUpdateRequest(BaseModel):
    student_name: str | None = None
    location: str | None = None
    issue_type: str | None = None
    description: str | None = None
    priority: str | None = None
    status: str | None = None

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str | None) -> str | None:
        if value is not None:
            allowed_priorities = ["low", "medium", "high"]
            if value not in allowed_priorities:
                raise ValueError(f"Priority must be one of: {', '.join(allowed_priorities)}")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is not None:
            allowed_statuses = ["pending", "in_progress", "resolved", "closed"]
            if value not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return value
