# tests/test_repository.py
import pytest
import sqlite3
from pathlib import Path
from task_manager.database import initialize_database, get_connection
from task_manager import repository

@pytest.fixture
def db_conn(tmp_path):
    """Fixture to set up a fresh database for every test."""
    db_path = tmp_path / "test_repo.db"
    initialize_database(db_path)
    conn = get_connection(db_path)
    
    # Create a default project for the tests to use
    conn.execute("INSERT INTO projects (name) VALUES (?)", ("Test Project",))
    conn.commit()
    
    yield conn
    
    conn.close()

def test_create_and_get_task(db_conn):
    task_id = repository.create_task(db_conn, 1, "Repo Task", "Testing repo")
    db_conn.commit() # Manually commit since repo doesn't do it
    
    task = repository.get_task_by_id(db_conn, task_id)
    assert task is not None
    assert task["title"] == "Repo Task"

def test_get_nonexistent_task(db_conn):
    task = repository.get_task_by_id(db_conn, 9999)
    assert task is None

def test_list_tasks(db_conn):
    # Initially empty
    assert repository.list_tasks(db_conn) == []
    
    repository.create_task(db_conn, 1, "Task A")
    repository.create_task(db_conn, 1, "Task B")
    db_conn.commit()
    
    tasks = repository.list_tasks(db_conn)
    assert len(tasks) == 2
    assert tasks[0]["title"] == "Task A"
    assert tasks[1]["title"] == "Task B"

def test_update_task_title(db_conn):
    task_id = repository.create_task(db_conn, 1, "Old Title")
    db_conn.commit()
    
    success = repository.update_task_title(db_conn, task_id, "New Title")
    db_conn.commit()
    
    assert success is True
    task = repository.get_task_by_id(db_conn, task_id)
    assert task["title"] == "New Title"

def test_update_nonexistent_task(db_conn):
    success = repository.update_task_title(db_conn, 9999, "Ghost")
    db_conn.commit()
    assert success is False

def test_delete_task(db_conn):
    task_id = repository.create_task(db_conn, 1, "To Delete")
    db_conn.commit()
    
    success = repository.delete_task(db_conn, task_id)
    db_conn.commit()
    
    assert success is True
    assert repository.get_task_by_id(db_conn, task_id) is None

def test_delete_nonexistent_task(db_conn):
    success = repository.delete_task(db_conn, 9999)
    db_conn.commit()
    assert success is False