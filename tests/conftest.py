import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from db.database import Base, get_db
from main import app
from db.models import DbUser, DbProject, DbTimesheetEntry, DbTimesheet
from auth.hash import hash_password
from enums import UserRole, TimesheetStatus

# In-memory test database with StaticPool
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables once
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function", autouse=True)
def cleanup_after_test():
    """Clean database after each test function"""
    yield  # Test runs here
    
    # Cleanup after test
    db = TestingSessionLocal()
    try:
        # Delete all entries first (foreign keys)
        db.query(DbTimesheetEntry).delete()
        db.query(DbTimesheet).delete()
        db.query(DbProject).delete()
        db.query(DbUser).delete()
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Provide database session for each test"""
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="function")
def client():
    """Create test client"""
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_manager(db_session):
    """Create a test manager user"""
    manager = DbUser(
        username="test_manager",
        email="manager@test.com",
        password=hash_password("testpass123"),
        role=UserRole.MANAGER,
        manager_id=None
    )
    db_session.add(manager)
    db_session.commit()
    db_session.refresh(manager)
    return manager


@pytest.fixture
def test_employee(db_session, test_manager):
    """Create a test employee user"""
    employee = DbUser(
        username="test_employee",
        email="employee@test.com",
        password=hash_password("testpass123"),
        role=UserRole.EMPLOYEE,
        manager_id=test_manager.id
    )
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    return employee


@pytest.fixture
def test_project(db_session):
    """Create a test project"""
    project = DbProject(
        name="Test Project",
        description="A test project"
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def test_timesheet(db_session, test_employee):
    """Create a draft timesheet for the test employee"""
    timesheet = DbTimesheet(
        employee_id=test_employee.id,
        week_number=6,
        year=2026,
        status=TimesheetStatus.DRAFT
    )
    db_session.add(timesheet)
    db_session.commit()
    db_session.refresh(timesheet)
    return timesheet


@pytest.fixture
def auth_token_employee(client, test_employee):
    """Get authentication token for test employee"""
    response = client.post(
        "/login",
        data={
            "username": "test_employee",
            "password": "testpass123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_token_manager(client, test_manager):
    """Get authentication token for test manager"""
    response = client.post(
        "/login",
        data={
            "username": "test_manager",
            "password": "testpass123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_headers_employee(auth_token_employee):
    """Get authorization headers for employee"""
    return {"Authorization": f"Bearer {auth_token_employee}"}


@pytest.fixture
def auth_headers_manager(auth_token_manager):
    """Get authorization headers for manager"""
    return {"Authorization": f"Bearer {auth_token_manager}"}
