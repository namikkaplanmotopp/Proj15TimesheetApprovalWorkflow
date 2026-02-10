# Timesheet API

A time tracking system built with FastAPI for employees and managers to track work hours across projects.

## Features

- **User Management**: Employee and Manager roles
- **Project Management**: Track time across multiple projects
- **Timesheet Entries**: Log hours worked per day per project
- **Team Management**: Managers can view their team's entries
- **Authentication**: JWT-based authentication
- **Authorization**: Role-based access control

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python main.py
```

The API will be available at `http://127.0.0.1:8000`

### 3. Seed Development Data

```bash
curl -X POST http://127.0.0.1:8000/seed/database
```

This creates:
- 2 managers (alice_manager, bob_manager)
- 4 employees (charlie_emp, diana_emp, eve_emp, frank_emp)
- 3 projects
- Sample timesheet entries

All test users have password: `password123`

## API Documentation

Once running, visit:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health (no authentication required)

### Health Check

The `/health` endpoint performs smoke tests **without requiring authentication**. It validates both technical functionality and data integrity:

```bash
curl http://127.0.0.1:8000/health
```

**Technical Checks:**
- Python version
- Database connectivity
- Database tables exist

**Data Integrity Checks:**
- Record counts (users, projects, entries)
- User roles distribution (managers/employees)
- Manager-employee assignments (validates foreign key relationships)

**Example response:**
```json
{
  "status": "healthy",
  "checks": {
    "python_version": {"status": "ok", "version": "3.11.0"},
    "database_connection": {"status": "ok"},
    "database_tables": {"status": "ok", "tables": ["users", "projects", "timesheet_entries"]},
    "data_counts": {"status": "ok", "users": 6, "projects": 3, "entries": 20},
    "roles_distribution": {
      "status": "ok", 
      "managers": 2, 
      "employees": 4, 
      "employees_assigned_to_manager": 4
    }
  }
}
```

**Use cases:**
- Verify installation after `pip install`
- Check data setup after running seed endpoint
- Troubleshoot "why doesn't my test work?" issues
- Validate manager-employee relationships before testing approval workflow
- Quick sanity check during development

Use this endpoint to verify the application is running correctly after installation.

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

Tests use an in-memory SQLite database and dependency overrides.

## Architecture

```
timesheet-api/
├── auth/              # Authentication & JWT handling
├── db/                # Database models and CRUD operations
├── router/            # API endpoints (controllers)
├── tests/             # Test suite
├── schemas.py         # Pydantic models (request/response)
├── enums.py           # Enumerations
└── main.py            # FastAPI application
```

## Usage Examples

### 1. Login

```bash
curl -X POST http://127.0.0.1:8000/login \
  -d "username=charlie_emp&password=password123"
```

Returns JWT token.

### 2. Create Timesheet Entry

```bash
curl -X POST http://127.0.0.1:8000/timesheet-entries/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "date": "2026-02-05",
    "hours": 8.0,
    "description": "Working on feature X"
  }'
```

### 3. Get My Entries

```bash
curl -X GET http://127.0.0.1:8000/timesheet-entries/my-entries \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Manager: View Team Entries

```bash
curl -X GET http://127.0.0.1:8000/timesheet-entries/team-entries \
  -H "Authorization: Bearer MANAGER_TOKEN"
```

## Database

- Development: SQLite (`timesheet.db`)
- Testing: In-memory SQLite
- Can be configured via `DATABASE_URL` environment variable

## Development

### Enable Debug Mode

The application is configured for debugging by default:
- `reload=False` in `main.py` (allows breakpoints)
- `log_level="debug"` for detailed logging

### Run Tests During Development

```bash
pytest tests/ -v --tb=short
```

## Project Structure

**MVC Architecture:**
- **Model**: `db/models.py` (SQLAlchemy models) + `db/db_*.py` (CRUD operations)
- **View**: `schemas.py` (Pydantic request/response models)
- **Controller**: `router/*.py` (API endpoints)

## License

Educational project for Motopp IT Basics training program.
