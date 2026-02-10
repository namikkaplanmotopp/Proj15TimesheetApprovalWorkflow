from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import DbUser, DbProject, DbTimesheetEntry
from auth.hash import hash_password
from enums import UserRole
from datetime import date, timedelta

router = APIRouter(
    prefix="/seed",
    tags=["seed"]
)


@router.post("/database")
def seed_database(db: Session = Depends(get_db)):
    """
    Seed the database with test data for development
    
    Creates:
    - 2 managers
    - 4 employees (2 per manager)
    - 3 projects
    - Sample timesheet entries for the current week
    """
    # Clear existing data
    db.query(DbTimesheetEntry).delete()
    db.query(DbUser).delete()
    db.query(DbProject).delete()
    
    # Create managers
    manager1 = DbUser(
        username="alice_manager",
        email="alice@example.com",
        password=hash_password("password123"),
        role=UserRole.MANAGER,
        manager_id=None
    )
    
    manager2 = DbUser(
        username="bob_manager",
        email="bob@example.com",
        password=hash_password("password123"),
        role=UserRole.MANAGER,
        manager_id=None
    )
    
    db.add(manager1)
    db.add(manager2)
    db.commit()
    db.refresh(manager1)
    db.refresh(manager2)
    
    # Create employees for manager1
    employee1 = DbUser(
        username="charlie_emp",
        email="charlie@example.com",
        password=hash_password("password123"),
        role=UserRole.EMPLOYEE,
        manager_id=manager1.id
    )
    
    employee2 = DbUser(
        username="diana_emp",
        email="diana@example.com",
        password=hash_password("password123"),
        role=UserRole.EMPLOYEE,
        manager_id=manager1.id
    )
    
    # Create employees for manager2
    employee3 = DbUser(
        username="eve_emp",
        email="eve@example.com",
        password=hash_password("password123"),
        role=UserRole.EMPLOYEE,
        manager_id=manager2.id
    )
    
    employee4 = DbUser(
        username="frank_emp",
        email="frank@example.com",
        password=hash_password("password123"),
        role=UserRole.EMPLOYEE,
        manager_id=manager2.id
    )
    
    db.add_all([employee1, employee2, employee3, employee4])
    db.commit()
    db.refresh(employee1)
    db.refresh(employee2)
    db.refresh(employee3)
    db.refresh(employee4)
    
    # Create projects
    project1 = DbProject(
        name="Website Redesign",
        description="Complete overhaul of company website"
    )
    
    project2 = DbProject(
        name="Mobile App Development",
        description="iOS and Android app for customers"
    )
    
    project3 = DbProject(
        name="Internal Tools",
        description="Development of internal automation tools"
    )
    
    db.add_all([project1, project2, project3])
    db.commit()
    db.refresh(project1)
    db.refresh(project2)
    db.refresh(project3)
    
    # Create sample timesheet entries for current week
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    
    entries = []
    
    # Charlie's entries (employee1)
    for day in range(5):  # Monday to Friday
        entry_date = start_of_week + timedelta(days=day)
        entries.append(DbTimesheetEntry(
            employee_id=employee1.id,
            project_id=project1.id,
            date=entry_date,
            hours=8.0,
            description=f"Working on {project1.name}"
        ))
    
    # Diana's entries (employee2)
    for day in range(5):
        entry_date = start_of_week + timedelta(days=day)
        entries.append(DbTimesheetEntry(
            employee_id=employee2.id,
            project_id=project2.id,
            date=entry_date,
            hours=7.5,
            description=f"Development work on {project2.name}"
        ))
    
    # Eve's entries (employee3)
    for day in range(3):  # Only 3 days
        entry_date = start_of_week + timedelta(days=day)
        entries.append(DbTimesheetEntry(
            employee_id=employee3.id,
            project_id=project3.id,
            date=entry_date,
            hours=8.0,
            description=f"Building {project3.name}"
        ))
    
    # Frank's entries (employee4) - mixed projects
    entries.append(DbTimesheetEntry(
        employee_id=employee4.id,
        project_id=project1.id,
        date=start_of_week,
        hours=4.0,
        description="Assistance on website"
    ))
    entries.append(DbTimesheetEntry(
        employee_id=employee4.id,
        project_id=project3.id,
        date=start_of_week,
        hours=4.0,
        description="Internal tools development"
    ))
    
    db.add_all(entries)
    db.commit()
    
    return {
        "message": "Database seeded successfully",
        "users": {
            "managers": 2,
            "employees": 4,
            "total": 6
        },
        "projects": 3,
        "timesheet_entries": len(entries),
        "credentials": {
            "managers": [
                {"username": "alice_manager", "password": "password123"},
                {"username": "bob_manager", "password": "password123"}
            ],
            "employees": [
                {"username": "charlie_emp", "password": "password123"},
                {"username": "diana_emp", "password": "password123"},
                {"username": "eve_emp", "password": "password123"},
                {"username": "frank_emp", "password": "password123"}
            ]
        }
    }
