from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from backend.models.ticket import Ticket
from backend.models.user import User


class UserRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, email: str, password_hash: str, full_name: str, role: str) -> User:
        raise NotImplementedError


class TicketRepository(ABC):
    @abstractmethod
    def create(self, data: dict[str, Any]) -> Ticket:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> Sequence[Ticket]:
        raise NotImplementedError

    @abstractmethod
    def list_by_user(self, user_id: int) -> Sequence[Ticket]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id_for_user(self, ticket_id: int, user_id: int) -> Ticket | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, ticket_id: int) -> Ticket | None:
        raise NotImplementedError

    @abstractmethod
    def update_status(self, ticket_id: int, status: str) -> Ticket | None:
        raise NotImplementedError

    @abstractmethod
    def update_fields(self, ticket: Ticket, fields: dict[str, Any]) -> Ticket:
        raise NotImplementedError

    @abstractmethod
    def delete(self, ticket: Ticket) -> None:
        raise NotImplementedError
