import os
import shutil
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from backend.core.config import UPLOAD_DIR
from backend.custom_errors import ForbiddenError, NotFoundError
from backend.dependencies.auth import verify_token
from backend.dependencies.db import get_db
from backend.repositories.sqlalchemy_repos import SqlAlchemyTicketRepository, SqlAlchemyUserRepository
from backend.schemas.tickets import TicketResponse, TicketUpdateRequest
from backend.services.ai_service import analyze_image_for_ticket
from backend.services.ticket_service import ensure_admin, get_ticket_for_owner, get_ticket_or_404
from backend.services.user_service import get_user_or_404

router = APIRouter(tags=["tickets"])


def _handle_ticket_error(exc: Exception) -> None:
    if isinstance(exc, ForbiddenError):
        raise HTTPException(status_code=403, detail=str(exc))
    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=404, detail=str(exc))
    raise exc


@router.post("/tickets/", response_model=TicketResponse)
async def create_ticket(
    student_name: str = Form(...),
    location: str = Form(...),
    image: UploadFile = File(...),
    user: dict = Depends(verify_token),
    db: Session = Depends(get_db),
):
    if not image.filename:
        raise HTTPException(status_code=400, detail="No image file provided")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_filename = f"{timestamp}_{image.filename}"
    image_path = UPLOAD_DIR / image_filename

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    analysis = analyze_image_for_ticket(str(image_path), student_name, location)

    ticket_repo = SqlAlchemyTicketRepository(db)
    ticket = ticket_repo.create(
        {
            "user_id": user["user_id"],
            "student_name": student_name,
            "location": location,
            "issue_type": analysis["issue_type"],
            "description": analysis["description"],
            "image_path": str(image_path),
            "priority": analysis["priority"],
        }
    )

    return TicketResponse(
        id=ticket.id,
        student_name=ticket.student_name,
        location=ticket.location,
        issue_type=ticket.issue_type,
        description=ticket.description,
        status=ticket.status,
        created_at=ticket.created_at,
        priority=ticket.priority,
    )


@router.get("/tickets/", response_model=list[TicketResponse])
async def get_tickets(user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user_repo = SqlAlchemyUserRepository(db)
    ticket_repo = SqlAlchemyTicketRepository(db)
    try:
        user_record = get_user_or_404(user["user_id"], user_repo)
        if user_record.role == "admin":
            tickets = ticket_repo.list_all()
        else:
            tickets = ticket_repo.list_by_user(user_record.id)

        return [
            TicketResponse(
                id=ticket.id,
                student_name=ticket.student_name,
                location=ticket.location,
                issue_type=ticket.issue_type,
                description=ticket.description,
                status=ticket.status,
                created_at=ticket.created_at,
                priority=ticket.priority,
            )
            for ticket in tickets
        ]
    except Exception as exc:
        _handle_ticket_error(exc)


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: int, user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    ticket_repo = SqlAlchemyTicketRepository(db)
    try:
        ticket = get_ticket_for_owner(ticket_repo, ticket_id, user["user_id"])
        return TicketResponse(
            id=ticket.id,
            student_name=ticket.student_name,
            location=ticket.location,
            issue_type=ticket.issue_type,
            description=ticket.description,
            status=ticket.status,
            created_at=ticket.created_at,
            priority=ticket.priority,
        )
    except Exception as exc:
        _handle_ticket_error(exc)


@router.put("/tickets/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: int,
    ticket_status: str = Query(...),
    user: dict = Depends(verify_token),
    db: Session = Depends(get_db),
):
    valid_statuses = ["pending", "in_progress", "resolved", "closed"]
    if ticket_status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
        )

    user_repo = SqlAlchemyUserRepository(db)
    ticket_repo = SqlAlchemyTicketRepository(db)

    try:
        user_record = get_user_or_404(user["user_id"], user_repo)
        ensure_admin(user_record.role)

        ticket = ticket_repo.update_status(ticket_id, ticket_status)
        if not ticket:
            raise NotFoundError("Ticket not found")

        return {
            "message": "Ticket status updated successfully",
            "ticket_id": ticket_id,
            "status": ticket_status,
        }
    except Exception as exc:
        _handle_ticket_error(exc)


@router.patch("/tickets/{ticket_id}")
async def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdateRequest,
    user: dict = Depends(verify_token),
    db: Session = Depends(get_db),
):
    user_repo = SqlAlchemyUserRepository(db)
    ticket_repo = SqlAlchemyTicketRepository(db)

    try:
        user_record = get_user_or_404(user["user_id"], user_repo)
        ticket = get_ticket_or_404(ticket_repo, ticket_id)

        if user_record.role != "admin" and ticket.user_id != user_record.id:
            raise ForbiddenError("Not authorized to update this ticket")

        updates = {
            key: value
            for key, value in ticket_update.model_dump().items()
            if value is not None
        }

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        if "status" in updates and user_record.role != "admin":
            raise ForbiddenError("Only admins can update ticket status")

        ticket = ticket_repo.update_fields(ticket, updates)

        return TicketResponse(
            id=ticket.id,
            student_name=ticket.student_name,
            location=ticket.location,
            issue_type=ticket.issue_type,
            description=ticket.description,
            status=ticket.status,
            created_at=ticket.created_at,
            priority=ticket.priority,
        )
    except Exception as exc:
        _handle_ticket_error(exc)


@router.delete("/tickets/{ticket_id}")
async def delete_ticket(
    ticket_id: int,
    user: dict = Depends(verify_token),
    db: Session = Depends(get_db),
):
    user_repo = SqlAlchemyUserRepository(db)
    ticket_repo = SqlAlchemyTicketRepository(db)

    try:
        user_record = get_user_or_404(user["user_id"], user_repo)
        ensure_admin(user_record.role)

        ticket = get_ticket_or_404(ticket_repo, ticket_id)
        image_path = ticket.image_path
        ticket_repo.delete(ticket)

        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception:
                pass

        return {
            "message": "Ticket deleted successfully",
            "ticket_id": ticket_id,
        }
    except Exception as exc:
        _handle_ticket_error(exc)
