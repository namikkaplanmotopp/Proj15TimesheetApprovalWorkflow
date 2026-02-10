from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from db.database import Base
from enums import UserRole, TimesheetStatus


class DbUser(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Self-referential relationship
    manager = relationship("DbUser", remote_side=[id], backref="team_members")
    
    # Relationships
    timesheet_entries = relationship("DbTimesheetEntry", back_populates="employee", cascade="all, delete-orphan")
    timesheets = relationship("DbTimesheet", back_populates="employee", foreign_keys="DbTimesheet.employee_id")
    reviewed_timesheets = relationship("DbTimesheet", back_populates="reviewer", foreign_keys="DbTimesheet.reviewed_by")


class DbProject(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    
    # Relationships
    timesheet_entries = relationship("DbTimesheetEntry", back_populates="project")


class DbTimesheetEntry(Base):
    __tablename__ = 'timesheet_entries'
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    timesheet_id = Column(Integer, ForeignKey('timesheets.id'), nullable=True)
    date = Column(Date, nullable=False)
    hours = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    
    # Relationships
    employee = relationship("DbUser", back_populates="timesheet_entries")
    project = relationship("DbProject", back_populates="timesheet_entries")
    timesheet = relationship("DbTimesheet", back_populates="entries")


class DbTimesheet(Base):
    __tablename__ = 'timesheets'
    __table_args__ = (
        UniqueConstraint('employee_id', 'week_number', 'year', name='unique_employee_week_timesheet'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    week_number = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(Enum(TimesheetStatus), nullable=False, default=TimesheetStatus.DRAFT)
    rejection_comment = Column(String, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relationships
    employee = relationship("DbUser", back_populates="timesheets", foreign_keys=[employee_id])
    reviewer = relationship("DbUser", back_populates="reviewed_timesheets", foreign_keys=[reviewed_by])
    entries = relationship("DbTimesheetEntry", back_populates="timesheet", cascade="all, delete-orphan")
