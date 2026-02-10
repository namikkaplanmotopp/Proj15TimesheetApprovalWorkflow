from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from db.models import DbTimesheetEntry, DbUser, DbProject, DbTimesheet
from schemas import TimesheetEntryCreate, TimesheetEntryUpdate
from enums import UserRole, TimesheetStatus
from datetime import date


def get_week_from_date(d: date) -> tuple[int, int]:
    """Get ISO week number and year from a date."""
    iso_calendar = d.isocalendar()
    return iso_calendar[1], iso_calendar[0]


def create_entry(db: Session, request: TimesheetEntryCreate, employee_id: int) -> DbTimesheetEntry:
    """Create a new timesheet entry"""
    # Validate timesheet exists
    timesheet = db.query(DbTimesheet).filter(DbTimesheet.id == request.timesheet_id).first()
    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timesheet with id {request.timesheet_id} not found"
        )
    
    # Validate timesheet ownership
    if timesheet.employee_id != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add entries to your own timesheet"
        )
    
    # Validate timesheet status
    if timesheet.status != TimesheetStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add entries to submitted/approved timesheet"
        )
    
    # Validate entry date is within timesheet week
    week_number, year = get_week_from_date(request.date)
    if week_number != timesheet.week_number or year != timesheet.year:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Entry date must be in week {timesheet.week_number}, {timesheet.year}"
        )
    
    # Validate project exists
    project = db.query(DbProject).filter(DbProject.id == request.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {request.project_id} not found"
        )
    
    # Validate hours
    if request.hours <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hours must be greater than 0"
        )
    
    if request.hours > 24:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hours cannot exceed 24 in a single day"
        )
    
    new_entry = DbTimesheetEntry(
        employee_id=employee_id,
        timesheet_id=request.timesheet_id,
        project_id=request.project_id,
        date=request.date,
        hours=request.hours,
        description=request.description
    )
    
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry


def get_entry(db: Session, entry_id: int) -> DbTimesheetEntry:
    """Get timesheet entry by ID"""
    entry = db.query(DbTimesheetEntry).filter(DbTimesheetEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timesheet entry with id {entry_id} not found"
        )
    return entry


def get_my_entries(db: Session, employee_id: int):
    """Get all entries for an employee"""
    return db.query(DbTimesheetEntry).filter(
        DbTimesheetEntry.employee_id == employee_id
    ).all()


def get_team_entries(db: Session, manager_id: int):
    """Get all entries for a manager's team"""
    # Get all team members
    team_member_ids = db.query(DbUser.id).filter(DbUser.manager_id == manager_id).all()
    team_member_ids = [id[0] for id in team_member_ids]
    
    # Get entries for all team members
    return db.query(DbTimesheetEntry).filter(
        DbTimesheetEntry.employee_id.in_(team_member_ids)
    ).all()


def update_entry(db: Session, entry_id: int, request: TimesheetEntryUpdate, current_user_id: int) -> DbTimesheetEntry:
    """Update a timesheet entry (only by owner)"""
    entry = get_entry(db, entry_id)
    
    # Check if current user is the owner
    if entry.employee_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own entries"
        )
    
    # Update fields if provided
    if request.project_id is not None:
        project = db.query(DbProject).filter(DbProject.id == request.project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {request.project_id} not found"
            )
        entry.project_id = request.project_id
    
    if request.date is not None:
        entry.date = request.date
    
    if request.hours is not None:
        if request.hours <= 0 or request.hours > 24:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hours must be between 0 and 24"
            )
        entry.hours = request.hours
    
    if request.description is not None:
        entry.description = request.description
    
    db.commit()
    db.refresh(entry)
    return entry


def delete_entry(db: Session, entry_id: int, current_user_id: int):
    """Delete a timesheet entry (only by owner)"""
    entry = get_entry(db, entry_id)
    
    # Check if current user is the owner
    if entry.employee_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own entries"
        )
    
    db.delete(entry)
    db.commit()
    return {"message": "Entry deleted successfully"}
