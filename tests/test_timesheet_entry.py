import pytest
from datetime import date


def test_create_timesheet_entry(client, test_employee, test_project, test_timesheet, auth_headers_employee):
    """Test creating a timesheet entry"""
    response = client.post(
        "/timesheet-entries/",
        json={
            "timesheet_id": test_timesheet.id,
            "project_id": test_project.id,
            "date": str(date(2026, 2, 5)),
            "hours": 8.0,
            "description": "Working on feature X"
        },
        headers=auth_headers_employee
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["project_id"] == test_project.id
    assert data["hours"] == 8.0
    assert data["employee_id"] == test_employee.id


def test_get_my_entries(client, test_employee, test_project, test_timesheet, auth_headers_employee):
    """Test getting own timesheet entries"""
    # Create an entry first
    client.post(
        "/timesheet-entries/",
        json={
            "timesheet_id": test_timesheet.id,
            "project_id": test_project.id,
            "date": str(date(2026, 2, 5)),
            "hours": 8.0,
            "description": "Test work"
        },
        headers=auth_headers_employee
    )
    
    # Get my entries
    response = client.get(
        "/timesheet-entries/my-entries",
        headers=auth_headers_employee
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["employee_id"] == test_employee.id


def test_manager_can_view_team_entries(client, test_manager, test_employee, test_project, test_timesheet, auth_headers_manager, auth_headers_employee):
    """Test that manager can view team member entries"""
    # Employee creates entry
    client.post(
        "/timesheet-entries/",
        json={
            "timesheet_id": test_timesheet.id,
            "project_id": test_project.id,
            "date": str(date(2026, 2, 5)),
            "hours": 8.0,
            "description": "Team work"
        },
        headers=auth_headers_employee
    )
    
    # Manager views team entries
    response = client.get(
        "/timesheet-entries/team-entries",
        headers=auth_headers_manager
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["employee_id"] == test_employee.id


def test_employee_cannot_view_team_entries(client, auth_headers_employee):
    """Test that employee cannot access team entries endpoint"""
    response = client.get(
        "/timesheet-entries/team-entries",
        headers=auth_headers_employee
    )
    
    assert response.status_code == 403


def test_update_own_entry(client, test_employee, test_project, test_timesheet, auth_headers_employee):
    """Test updating own timesheet entry"""
    # Create entry
    create_response = client.post(
        "/timesheet-entries/",
        json={
            "timesheet_id": test_timesheet.id,
            "project_id": test_project.id,
            "date": str(date(2026, 2, 5)),
            "hours": 8.0,
            "description": "Original description"
        },
        headers=auth_headers_employee
    )
    entry_id = create_response.json()["id"]
    
    # Update entry
    response = client.put(
        f"/timesheet-entries/{entry_id}",
        json={
            "hours": 6.5,
            "description": "Updated description"
        },
        headers=auth_headers_employee
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["hours"] == 6.5
    assert data["description"] == "Updated description"


def test_delete_own_entry(client, test_employee, test_project, test_timesheet, auth_headers_employee):
    """Test deleting own timesheet entry"""
    # Create entry
    create_response = client.post(
        "/timesheet-entries/",
        json={
            "timesheet_id": test_timesheet.id,
            "project_id": test_project.id,
            "date": str(date(2026, 2, 5)),
            "hours": 8.0,
            "description": "To be deleted"
        },
        headers=auth_headers_employee
    )
    entry_id = create_response.json()["id"]
    
    # Delete entry
    response = client.delete(
        f"/timesheet-entries/{entry_id}",
        headers=auth_headers_employee
    )
    
    assert response.status_code == 204
    
    # Verify entry is gone
    get_response = client.get(
        f"/timesheet-entries/{entry_id}",
        headers=auth_headers_employee
    )
    assert get_response.status_code == 404


def test_cannot_create_entry_with_invalid_hours(client, test_project, test_timesheet, auth_headers_employee):
    """Test validation: hours must be between 0 and 24"""
    response = client.post(
        "/timesheet-entries/",
        json={
            "timesheet_id": test_timesheet.id,
            "project_id": test_project.id,
            "date": str(date(2026, 2, 5)),
            "hours": 25.0,  # Invalid: more than 24 hours
            "description": "Invalid hours"
        },
        headers=auth_headers_employee
    )
    
    assert response.status_code == 400
