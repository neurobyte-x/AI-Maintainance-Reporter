from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from backend.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    issue_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    image_path = Column(String(500))
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, server_default=func.now())
    priority = Column(String(50), default="medium")
