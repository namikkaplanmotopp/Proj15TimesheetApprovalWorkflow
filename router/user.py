from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_user
from schemas import UserCreate, UserDisplay
from auth.oauth2 import get_current_user
from db.models import DbUser
from typing import List

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserDisplay)
def create_user(
    request: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user (employee or manager)
    """
    return db_user.create_user(db, request)


@router.get("/me", response_model=UserDisplay)
def get_current_user_info(
    current_user: DbUser = Depends(get_current_user)
):
    """
    Get current authenticated user information
    """
    return current_user


@router.get("/{user_id}", response_model=UserDisplay)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Get user by ID (authenticated users only)
    """
    return db_user.get_user(db, user_id)


@router.get("/", response_model=List[UserDisplay])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Get all users (authenticated users only)
    """
    return db_user.get_all_users(db)


@router.get("/manager/{manager_id}/team", response_model=List[UserDisplay])
def get_team_members(
    manager_id: int,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    """
    Get all team members for a manager
    """
    return db_user.get_team_members(db, manager_id)
