from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import date, datetime
from enums import UserRole, TimesheetStatus
from typing import Optional, List


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.EMPLOYEE
    manager_id: Optional[int] = None


class UserCreate(UserBase):
    password: str


class UserDisplay(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: str
    role: UserRole
    manager_id: Optional[int]


class UserAuth(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole


# Project schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectDisplay(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str]


# Timesheet Entry schemas
class TimesheetEntryBase(BaseModel):
    timesheet_id: int
    project_id: int
    date: date
    hours: float
    description: Optional[str] = None


class TimesheetEntryCreate(TimesheetEntryBase):
    pass


class TimesheetEntryUpdate(BaseModel):
    project_id: Optional[int] = None
    date: Optional[date] = None
    hours: Optional[float] = None
    description: Optional[str] = None


class TimesheetEntryDisplay(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    employee_id: int
    timesheet_id: int
    project_id: int
    date: date
    hours: float
    description: Optional[str]


# Timesheet schemas
class TimesheetCreate(BaseModel):
    week_number: int
    year: int
    
    @field_validator("week_number")
    @classmethod
    def validate_week_number(cls, v: int) -> int:
        if v < 1 or v > 53:
            raise ValueError("week_number must be between 1 and 53")
        return v
    
    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        if v < 2020 or v > 2030:
            raise ValueError("year must be between 2020 and 2030")
        return v


class TimesheetReject(BaseModel):
    rejection_comment: str
    
    @field_validator("rejection_comment")
    @classmethod
    def validate_rejection_comment(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("rejection_comment cannot be empty")
        return v


class TimesheetDisplay(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    employee_id: int
    week_number: int
    year: int
    status: TimesheetStatus
    submitted_at: Optional[datetime]
    reviewed_at: Optional[datetime]
    reviewed_by: Optional[int]
    rejection_comment: Optional[str]


class TimesheetListItem(TimesheetDisplay):
    entries_count: int
    total_hours: Optional[float] = None
    employee_name: Optional[str] = None


class TimesheetWithEntries(TimesheetDisplay):
    entries: List[TimesheetEntryDisplay] = []
