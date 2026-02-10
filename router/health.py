from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.database import get_db
from db.models import DbUser, DbProject, DbTimesheetEntry
import sys

router = APIRouter(
    tags=["health"]
)


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint - no authentication required
    
    Performs smoke tests on basic functionality:
    - Database connectivity
    - Model integrity
    - Python version
    
    Returns status and diagnostic information
    """
    checks = {
        "status": "healthy",
        "checks": {}
    }
    
    # Check 1: Python version
    try:
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        checks["checks"]["python_version"] = {
            "status": "ok",
            "version": python_version
        }
    except Exception as e:
        checks["checks"]["python_version"] = {
            "status": "error",
            "message": str(e)
        }
        checks["status"] = "unhealthy"
    
    # Check 2: Database connection
    try:
        db.execute(text("SELECT 1"))
        checks["checks"]["database_connection"] = {
            "status": "ok",
            "message": "Connected"
        }
    except Exception as e:
        checks["checks"]["database_connection"] = {
            "status": "error",
            "message": str(e)
        }
        checks["status"] = "unhealthy"
    
    # Check 3: Database tables exist
    try:
        # Try to query each table
        db.query(DbUser).first()
        db.query(DbProject).first()
        db.query(DbTimesheetEntry).first()
        
        checks["checks"]["database_tables"] = {
            "status": "ok",
            "tables": ["users", "projects", "timesheet_entries"]
        }
    except Exception as e:
        checks["checks"]["database_tables"] = {
            "status": "error",
            "message": str(e)
        }
        checks["status"] = "unhealthy"
    
    # Check 4: Count records (smoke test data existence)
    try:
        user_count = db.query(DbUser).count()
        project_count = db.query(DbProject).count()
        entry_count = db.query(DbTimesheetEntry).count()
        
        checks["checks"]["data_counts"] = {
            "status": "ok",
            "users": user_count,
            "projects": project_count,
            "entries": entry_count,
            "note": "Run POST /seed/database if counts are 0"
        }
    except Exception as e:
        checks["checks"]["data_counts"] = {
            "status": "error",
            "message": str(e)
        }
        checks["status"] = "unhealthy"
    
    # Check 5: User roles distribution
    try:
        # Check if there are managers and employees
        from enums import UserRole
        manager_count = db.query(DbUser).filter(DbUser.role == UserRole.MANAGER).count()
        employee_count = db.query(DbUser).filter(DbUser.role == UserRole.EMPLOYEE).count()
        employees_assigned = db.query(DbUser).filter(
            DbUser.manager_id.isnot(None)
        ).count()
        
        checks["checks"]["roles_distribution"] = {
            "status": "ok",
            "managers": manager_count,
            "employees": employee_count,
            "employees_assigned_to_manager": employees_assigned
        }
        
        if manager_count == 0 or employee_count == 0:
            checks["checks"]["roles_distribution"]["note"] = "Run POST /seed/database to create users"
            
    except Exception as e:
        checks["checks"]["roles_distribution"] = {
            "status": "error",
            "message": str(e)
        }
        checks["status"] = "unhealthy"
    
    return checks
