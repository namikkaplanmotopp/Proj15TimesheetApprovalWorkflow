from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from db.models import DbUser
from schemas import UserCreate
from auth.hash import hash_password
from enums import UserRole


def create_user(db: Session, request: UserCreate) -> DbUser:
    """Create a new user"""
    # Check if username already exists
    existing_user = db.query(DbUser).filter(DbUser.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email already exists
    existing_email = db.query(DbUser).filter(DbUser.email == request.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Validate manager_id if provided
    if request.manager_id:
        manager = db.query(DbUser).filter(DbUser.id == request.manager_id).first()
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Manager with id {request.manager_id} not found"
            )
        if manager.role != UserRole.MANAGER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned manager must have manager role"
            )
    
    # Create user
    new_user = DbUser(
        username=request.username,
        email=request.email,
        password=hash_password(request.password),
        role=request.role,
        manager_id=request.manager_id
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user(db: Session, user_id: int) -> DbUser:
    """Get user by ID"""
    user = db.query(DbUser).filter(DbUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user


def get_all_users(db: Session):
    """Get all users"""
    return db.query(DbUser).all()


def get_team_members(db: Session, manager_id: int):
    """Get all team members for a manager"""
    manager = get_user(db, manager_id)
    if manager.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a manager"
        )
    return db.query(DbUser).filter(DbUser.manager_id == manager_id).all()
