from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from db.models import DbTimesheet, DbTimesheetEntry, DbUser
from enums import TimesheetStatus, UserRole
from schemas import TimesheetCreate, TimesheetReject


def _timesheet_base_dict(timesheet: DbTimesheet) -> dict:
    return {
        "id": timesheet.id,
        "employee_id": timesheet.employee_id,
        "week_number": timesheet.week_number,
        "year": timesheet.year,
        "status": timesheet.status,
        "submitted_at": timesheet.submitted_at,
        "reviewed_at": timesheet.reviewed_at,
        "reviewed_by": timesheet.reviewed_by,
        "rejection_comment": timesheet.rejection_comment,
    }


def _entries_stats(db: Session, timesheet_id: int) -> tuple[int, float]:
    entries = db.query(DbTimesheetEntry).filter(DbTimesheetEntry.timesheet_id == timesheet_id).all()
    entries_count = len(entries)
    total_hours = sum(e.hours for e in entries) if entries else 0.0
    return entries_count, total_hours


def create_timesheet(db: Session, request: TimesheetCreate, employee_id: int) -> DbTimesheet:
    new_timesheet = DbTimesheet(
        employee_id=employee_id,
        week_number=request.week_number,
        year=request.year,
        status=TimesheetStatus.DRAFT,
    )
    try:
        db.add(new_timesheet)
        db.commit()
        db.refresh(new_timesheet)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Timesheet already exists for week {request.week_number}, {request.year}"
        )
    return new_timesheet


def submit_timesheet(db: Session, timesheet_id: int, current_user_id: int) -> DbTimesheet:
    timesheet = db.query(DbTimesheet).filter(DbTimesheet.id == timesheet_id).first()
    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet doesn't exist"
        )
    
    if timesheet.employee_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your timesheet"
        )
    
    if timesheet.status != TimesheetStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timesheet is not DRAFT"
        )
    
    entries_count = db.query(DbTimesheetEntry).filter(
        DbTimesheetEntry.timesheet_id == timesheet_id
    ).count()
    if entries_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot submit empty timesheet"
        )
    
    timesheet.status = TimesheetStatus.SUBMITTED
    timesheet.submitted_at = datetime.utcnow()
    db.commit()
    db.refresh(timesheet)
    return timesheet


def approve_timesheet(db: Session, timesheet_id: int, current_user: DbUser) -> DbTimesheet:
    timesheet = db.query(DbTimesheet).filter(DbTimesheet.id == timesheet_id).first()
    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet doesn't exist"
        )
    
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a manager"
        )
    
    if timesheet.employee_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Trying to approve own timesheet"
        )
    
    employee = db.query(DbUser).filter(DbUser.id == timesheet.employee_id).first()
    if not employee or employee.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not the employee's manager"
        )
    
    if timesheet.status != TimesheetStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timesheet not in SUBMITTED status"
        )
    
    timesheet.status = TimesheetStatus.APPROVED
    timesheet.reviewed_at = datetime.utcnow()
    timesheet.reviewed_by = current_user.id
    db.commit()
    db.refresh(timesheet)
    return timesheet


def reject_timesheet(db: Session, timesheet_id: int, request: TimesheetReject, current_user: DbUser) -> DbTimesheet:
    timesheet = db.query(DbTimesheet).filter(DbTimesheet.id == timesheet_id).first()
    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet doesn't exist"
        )
    
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a manager"
        )
    
    if timesheet.employee_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Trying to approve own timesheet"
        )
    
    employee = db.query(DbUser).filter(DbUser.id == timesheet.employee_id).first()
    if not employee or employee.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not the employee's manager"
        )
    
    if timesheet.status != TimesheetStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timesheet not in SUBMITTED status"
        )
    
    timesheet.status = TimesheetStatus.REJECTED
    timesheet.rejection_comment = request.rejection_comment
    timesheet.reviewed_at = datetime.utcnow()
    timesheet.reviewed_by = current_user.id
    db.commit()
    db.refresh(timesheet)
    return timesheet


def get_my_timesheets(db: Session, current_user_id: int, status_filter: TimesheetStatus | None, year: int | None, week_number: int | None):
    query = db.query(DbTimesheet).filter(DbTimesheet.employee_id == current_user_id)
    if status_filter:
        query = query.filter(DbTimesheet.status == status_filter)
    if year:
        query = query.filter(DbTimesheet.year == year)
    if week_number:
        query = query.filter(DbTimesheet.week_number == week_number)
    
    timesheets = query.all()
    result = []
    for t in timesheets:
        entries_count, total_hours = _entries_stats(db, t.id)
        item = _timesheet_base_dict(t)
        item["entries_count"] = entries_count
        item["total_hours"] = total_hours
        result.append(item)
    return result


def get_pending_approvals(db: Session, current_user: DbUser):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a manager"
        )
    
    timesheets = db.query(DbTimesheet).join(DbUser, DbUser.id == DbTimesheet.employee_id).filter(
        DbTimesheet.status == TimesheetStatus.SUBMITTED,
        DbUser.manager_id == current_user.id
    ).all()
    
    result = []
    for t in timesheets:
        entries_count, total_hours = _entries_stats(db, t.id)
        item = _timesheet_base_dict(t)
        item["entries_count"] = entries_count
        item["total_hours"] = total_hours
        item["employee_name"] = t.employee.username if t.employee else None
        result.append(item)
    return result


def get_timesheet_with_entries(db: Session, timesheet_id: int, current_user: DbUser) -> DbTimesheet:
    timesheet = db.query(DbTimesheet).filter(DbTimesheet.id == timesheet_id).first()
    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet doesn't exist"
        )
    
    if current_user.role == UserRole.MANAGER:
        if timesheet.employee_id == current_user.id:
            return timesheet
        employee = db.query(DbUser).filter(DbUser.id == timesheet.employee_id).first()
        if not employee or employee.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not the employee's manager"
            )
    else:
        if timesheet.employee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your timesheet"
            )
    
    return timesheet
