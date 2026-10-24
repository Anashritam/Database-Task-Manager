# tests/test_services.py
import pytest
import sqlite3
from pathlib import Path
from task_manager.database import initialize_database, get_connection
from task_manager import services, repository

@pytest.fixture
def db_conn(tmp_path):
    """Fixture to set up a fresh database for every test."""
    db_path = tmp_path / "test_svc.db"
    initialize_database(db_path)
    conn = get_connection(db_path)
    
    # Create a default project
    conn.execute("INSERT INTO projects (name) VALUES (?)", ("Test Project",))
    conn.commit()
    
    yield conn
    conn.close()

def test_create_task_service_valid(db_conn):
    task_id = services.create_task_service(db_conn, 1, "  Service Task  ")
    task = repository.get_task_by_id(db_conn, task_id)
    
    assert task is not None
    # Verify it stripped the whitespace
    assert task["title"] == "Service Task" 

def test_create_task_service_empty_title(db_conn):
    with pytest.raises(ValueError, match="Task title cannot be empty."):
        services.create_task_service(db_conn, 1, "   ")

def test_create_task_service_bad_project(db_conn):
    with pytest.raises(sqlite3.IntegrityError):
        services.create_task_service(db_conn, 9999, "Ghost Task")
        
    # Verify rollback: no tasks should exist
    assert repository.list_tasks(db_conn) == []

def test_get_task_service(db_conn):
    task_id = services.create_task_service(db_conn, 1, "Get Me")
    
    task = services.get_task_service(db_conn, task_id)
    assert task["title"] == "Get Me"
    
    missing = services.get_task_service(db_conn, 9999)
    assert missing is None

def test_update_task_title_service(db_conn):
    task_id = services.create_task_service(db_conn, 1, "Original")
    
    success = services.update_task_title_service(db_conn, task_id, "  Updated  ")
    assert success is True
    
    task = services.get_task_service(db_conn, task_id)
    assert task["title"] == "Updated"

def test_update_task_title_service_empty(db_conn):
    task_id = services.create_task_service(db_conn, 1, "Original")
    
    with pytest.raises(ValueError):
        services.update_task_title_service(db_conn, task_id, "   ")

def test_delete_task_service(db_conn):
    task_id = services.create_task_service(db_conn, 1, "Delete Me")
    
    success = services.delete_task_service(db_conn, task_id)
    assert success is True
    
    assert services.get_task_service(db_conn, task_id) is None
    
    # Try deleting again
    success = services.delete_task_service(db_conn, task_id)
    assert success is False

# tests/test_services.py (add to the bottom)

def test_list_tasks_service_empty(db_conn):
    """Verify that an empty database returns an empty list."""
    tasks = services.list_tasks_service(db_conn)
    assert tasks == []

def test_list_tasks_service_with_data(db_conn):
    """Verify that the service returns all created tasks."""
    # Create two tasks using the service layer
    services.create_task_service(db_conn, 1, "First Task")
    services.create_task_service(db_conn, 1, "Second Task")
    
    # Retrieve the list
    tasks = services.list_tasks_service(db_conn)
    
    # Verify the count and contents
    assert len(tasks) == 2
    assert tasks[0]["title"] == "First Task"
    assert tasks[1]["title"] == "Second Task"