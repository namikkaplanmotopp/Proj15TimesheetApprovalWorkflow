from datetime import date


def _week_year(d: date) -> tuple[int, int]:
    iso_calendar = d.isocalendar()
    return iso_calendar[1], iso_calendar[0]


def test_employee_can_submit_timesheet(client, test_employee, test_project, auth_headers_employee):
    """Employee creates entries and submits timesheet"""
    entry_date = date(2026, 2, 5)
    week_number, year = _week_year(entry_date)
    
    # Create draft timesheet
    ts_response = client.post(
        "/timesheets/",
        json={"week_number": week_number, "year": year},
        headers=auth_headers_employee
    )
    assert ts_response.status_code == 201
    timesheet_id = ts_response.json()["id"]
    
    # Create entry linked to timesheet
    entry_response = client.post(
        "/timesheet-entries/",
        json={
            "timesheet_id": timesheet_id,
            "project_id": test_project.id,
            "date": str(entry_date),
            "hours": 8.0,
            "description": "Work on project"
        },
        headers=auth_headers_employee
    )
    assert entry_response.status_code == 201
    
    # Submit timesheet
    submit_response = client.post(
        f"/timesheets/{timesheet_id}/submit",
        headers=auth_headers_employee
    )
    assert submit_response.status_code == 200
    assert submit_response.json()["status"] == "submitted"
    
    # Verify entries linked to timesheet
    get_response = client.get(
        f"/timesheets/{timesheet_id}",
        headers=auth_headers_employee
    )
    assert get_response.status_code == 200
    data = get_response.json()
    assert len(data["entries"]) >= 1
    assert data["entries"][0]["timesheet_id"] == timesheet_id


def test_cannot_submit_without_entries(client, auth_headers_employee):
    """Submitting a timesheet without entries should fail"""
    entry_date = date(2026, 2, 5)
    week_number, year = _week_year(entry_date)
    
    ts_response = client.post(
        "/timesheets/",
        json={"week_number": week_number, "year": year},
        headers=auth_headers_employee
    )
    assert ts_response.status_code == 201
    timesheet_id = ts_response.json()["id"]
    
    submit_response = client.post(
        f"/timesheets/{timesheet_id}/submit",
        headers=auth_headers_employee
    )
    assert submit_response.status_code == 400


def test_cannot_submit_twice_same_week(client, test_project, auth_headers_employee):
    """Cannot create another timesheet for same week/year after submitting"""
    entry_date = date(2026, 2, 5)
    week_number, year = _week_year(entry_date)
    
    ts_response = client.post(
        "/timesheets/",
        json={"week_number": week_number, "year": year},
        headers=auth_headers_employee
    )
    assert ts_response.status_code == 201
    timesheet_id = ts_response.json()["id"]
    
    # Add an entry and submit
    client.post(
        "/timesheet-entries/",
        json={
            "timesheet_id": timesheet_id,
            "project_id": test_project.id,
            "date": str(entry_date),
            "hours": 8.0,
            "description": "Work on project"
        },
        headers=auth_headers_employee
    )
    client.post(
        f"/timesheets/{timesheet_id}/submit",
        headers=auth_headers_employee
    )
    
    # Try creating another timesheet for same week/year
    second_response = client.post(
        "/timesheets/",
        json={"week_number": week_number, "year": year},
        headers=auth_headers_employee
    )
    assert second_response.status_code == 409
