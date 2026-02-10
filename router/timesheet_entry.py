from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_timesheet_entry
from schemas import TimesheetEntryCreate, TimesheetEntryUpdate, TimesheetEntryDisplay
from auth.oauth2 import get_current_user
from db.models import DbUser
from enums import UserRole
from typing import List

router = APIRouter(
    prefix="/timesheet-entries",
    tags=["timesheet-entries"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TimesheetEntryDisplay)
def create_entry(
    request: TimesheetEntryCreate,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Create a new timesheet entry for the authenticated user
    """
    return db_timesheet_entry.create_entry(db, request, current_user.id)


@router.get("/my-entries", response_model=List[TimesheetEntryDisplay])
def get_my_entries(
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Get all timesheet entries for the authenticated user
    """
    return db_timesheet_entry.get_my_entries(db, current_user.id)


@router.get("/team-entries", response_model=List[TimesheetEntryDisplay])
def get_team_entries(
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Get all timesheet entries for the manager's team
    (Manager role required)
    """
    if current_user.role != UserRole.MANAGER:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can view team entries"
        )
    
    return db_timesheet_entry.get_team_entries(db, current_user.id)


@router.get("/{entry_id}", response_model=TimesheetEntryDisplay)
def get_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Get a specific timesheet entry by ID
    """
    return db_timesheet_entry.get_entry(db, entry_id)


@router.put("/{entry_id}", response_model=TimesheetEntryDisplay)
def update_entry(
    entry_id: int,
    request: TimesheetEntryUpdate,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Update a timesheet entry (only owner can update)
    """
    return db_timesheet_entry.update_entry(db, entry_id, request, current_user.id)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Delete a timesheet entry (only owner can delete)
    """
    db_timesheet_entry.delete_entry(db, entry_id, current_user.id)
