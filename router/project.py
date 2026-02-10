from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_project
from schemas import ProjectCreate, ProjectDisplay
from auth.oauth2 import get_current_user
from db.models import DbUser
from typing import List

router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProjectDisplay)
def create_project(
    request: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Create a new project (authenticated users only)
    """
    return db_project.create_project(db, request)


@router.get("/{project_id}", response_model=ProjectDisplay)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Get project by ID
    """
    return db_project.get_project(db, project_id)


@router.get("/", response_model=List[ProjectDisplay])
def get_all_projects(
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Get all projects
    """
    return db_project.get_all_projects(db)
