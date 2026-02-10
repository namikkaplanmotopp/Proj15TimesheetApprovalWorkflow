from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from db.models import DbProject
from schemas import ProjectCreate


def create_project(db: Session, request: ProjectCreate) -> DbProject:
    """Create a new project"""
    # Check if project name already exists
    existing_project = db.query(DbProject).filter(DbProject.name == request.name).first()
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project name already exists"
        )
    
    new_project = DbProject(
        name=request.name,
        description=request.description
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


def get_project(db: Session, project_id: int) -> DbProject:
    """Get project by ID"""
    project = db.query(DbProject).filter(DbProject.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    return project


def get_all_projects(db: Session):
    """Get all projects"""
    return db.query(DbProject).all()
