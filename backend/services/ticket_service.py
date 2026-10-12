from backend.custom_errors import ForbiddenError, NotFoundError
from backend.repositories.interfaces import TicketRepository


def ensure_admin(role: str) -> None:
    if role != "admin":
        raise ForbiddenError("Admin access required")


def get_ticket_for_owner(ticket_repo: TicketRepository, ticket_id: int, user_id: int):
    ticket = ticket_repo.get_by_id_for_user(ticket_id, user_id)
    if not ticket:
        raise NotFoundError("Ticket not found")
    return ticket


def get_ticket_or_404(ticket_repo: TicketRepository, ticket_id: int):
    ticket = ticket_repo.get_by_id(ticket_id)
    if not ticket:
        raise NotFoundError("Ticket not found")
    return ticket
