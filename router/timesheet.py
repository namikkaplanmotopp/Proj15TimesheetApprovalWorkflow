from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from db.database import get_db
from db import db_timesheet
from schemas import TimesheetCreate, TimesheetReject, TimesheetDisplay, TimesheetListItem, TimesheetWithEntries
from auth.oauth2 import get_current_user
from db.models import DbUser
from enums import UserRole, TimesheetStatus


router = APIRouter(
    prefix="/timesheets",
    tags=["timesheets"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TimesheetDisplay)
def create_timesheet(
    request: TimesheetCreate,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Create a new draft timesheet for a specific week (employee only)
    """
    if current_user.role != UserRole.EMPLOYEE:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employees can create timesheets"
        )
    return db_timesheet.create_timesheet(db, request, current_user.id)


@router.post("/{timesheet_id}/submit", response_model=TimesheetDisplay)
def submit_timesheet(
    timesheet_id: int,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Submit a draft timesheet for approval (employee only)
    """
    if current_user.role != UserRole.EMPLOYEE:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employees can submit timesheets"
        )
    return db_timesheet.submit_timesheet(db, timesheet_id, current_user.id)


@router.put("/{timesheet_id}/approve", response_model=TimesheetDisplay)
def approve_timesheet(
    timesheet_id: int,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Approve a submitted timesheet (manager only)
    """
    return db_timesheet.approve_timesheet(db, timesheet_id, current_user)


@router.put("/{timesheet_id}/reject", response_model=TimesheetDisplay)
def reject_timesheet(
    timesheet_id: int,
    request: TimesheetReject,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Reject a submitted timesheet with a comment (manager only)
    """
    return db_timesheet.reject_timesheet(db, timesheet_id, request, current_user)


@router.get("/my-timesheets", response_model=List[TimesheetListItem])
def get_my_timesheets(
    status_filter: Optional[TimesheetStatus] = Query(default=None, alias="status"),
    year: Optional[int] = None,
    week_number: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Get all timesheets for the current user (optional filters)
    """
    return db_timesheet.get_my_timesheets(db, current_user.id, status_filter, year, week_number)


@router.get("/pending-approvals", response_model=List[TimesheetListItem])
def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Get all pending timesheets for manager's team (manager only)
    """
    return db_timesheet.get_pending_approvals(db, current_user)


@router.get("/{timesheet_id}", response_model=TimesheetWithEntries)
def get_timesheet(
    timesheet_id: int,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Get a specific timesheet with entries
    """
    return db_timesheet.get_timesheet_with_entries(db, timesheet_id, current_user)
