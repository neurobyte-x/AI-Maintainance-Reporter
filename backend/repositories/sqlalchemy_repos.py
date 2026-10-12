from collections.abc import Sequence
from typing import Any

from sqlalchemy.orm import Session

from backend.models.ticket import Ticket
from backend.models.user import User
from backend.repositories.interfaces import TicketRepository, UserRepository


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, email: str, password_hash: str, full_name: str, role: str) -> User:
        user = User(email=email, password_hash=password_hash, full_name=full_name, role=role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


class SqlAlchemyTicketRepository(TicketRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: dict[str, Any]) -> Ticket:
        ticket = Ticket(**data)
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def list_all(self) -> Sequence[Ticket]:
        return self.db.query(Ticket).order_by(Ticket.created_at.desc()).all()

    def list_by_user(self, user_id: int) -> Sequence[Ticket]:
        return (
            self.db.query(Ticket)
            .filter(Ticket.user_id == user_id)
            .order_by(Ticket.created_at.desc())
            .all()
        )

    def get_by_id_for_user(self, ticket_id: int, user_id: int) -> Ticket | None:
        return (
            self.db.query(Ticket)
            .filter(Ticket.id == ticket_id, Ticket.user_id == user_id)
            .first()
        )

    def get_by_id(self, ticket_id: int) -> Ticket | None:
        return self.db.query(Ticket).filter(Ticket.id == ticket_id).first()

    def update_status(self, ticket_id: int, status: str) -> Ticket | None:
        ticket = self.get_by_id(ticket_id)
        if not ticket:
            return None
        ticket.status = status
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def update_fields(self, ticket: Ticket, fields: dict[str, Any]) -> Ticket:
        for key, value in fields.items():
            setattr(ticket, key, value)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def delete(self, ticket: Ticket) -> None:
        self.db.delete(ticket)
        self.db.commit()
