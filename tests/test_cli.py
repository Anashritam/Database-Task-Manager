import pytest
import sys
import sqlite3
from pathlib import Path

from task_manager.database import initialize_database, get_connection
from task_manager import cli

@pytest.fixture
def cli_env(tmp_path, monkeypatch):
    """
    Sets up a temporary database for the CLI to use.
    We use monkeypatch to change the hardcoded DB_PATH in cli.py 
    so our tests don't overwrite your actual development database.
    """
    db_path = tmp_path / "test_cli.db"
    
    # 1. Patch the DB_PATH variable inside the cli module
    monkeypatch.setattr(cli, "DB_PATH", db_path)
    
    # 2. Initialize the DB and create a default project (ID 1) for the tests
    initialize_database(db_path)
    conn = get_connection(db_path)
    conn.execute("INSERT INTO projects (name) VALUES (?)", ("Test Project",))
    conn.commit()
    conn.close()
    
    return db_path

def run_cli(monkeypatch, capsys, args: list[str]):
    """
    Helper function to simulate running the CLI from the terminal.
    It patches sys.argv, runs main(), catches any sys.exit() calls, 
    and captures the printed output.
    """
    # Simulate typing: python cli.py <args>
    monkeypatch.setattr(sys, "argv", ["cli.py"] + args)
    
    try:
        cli.main()
        exit_code = 0  # If it finishes normally, exit code is 0
    except SystemExit as e:
        # If it calls sys.exit(1), we catch it here
        exit_code = e.code if e.code is not None else 0
        
    # Capture whatever was printed to the terminal
    captured = capsys.readouterr()
    
    return exit_code, captured.out, captured.err


# ==========================================
# The Actual Tests
# ==========================================

def test_help_command(cli_env, monkeypatch, capsys):
    """Verify --help prints usage and exits cleanly."""
    code, out, err = run_cli(monkeypatch, capsys, ["--help"])
    
    assert code == 0
    assert "usage:" in out.lower()
    assert "create" in out
    assert "list" in out

def test_no_arguments(cli_env, monkeypatch, capsys):
    """Verify running with no arguments shows help and exits with error code 1."""
    code, out, err = run_cli(monkeypatch, capsys, [])
    
    assert code == 1
    assert "usage:" in out.lower()

def test_list_empty(cli_env, monkeypatch, capsys):
    """Verify list command on an empty database."""
    code, out, err = run_cli(monkeypatch, capsys, ["list"])
    
    assert code == 0
    assert "No tasks found." in out

def test_create_success(cli_env, monkeypatch, capsys):
    """Verify creating a valid task."""
    code, out, err = run_cli(monkeypatch, capsys, ["create", "1", "CLI Test Task"])
    
    assert code == 0
    assert "Success: Created task with ID" in out

def test_create_invalid_title(cli_env, monkeypatch, capsys):
    """Verify the CLI catches the ValueError from the service layer."""
    code, out, err = run_cli(monkeypatch, capsys, ["create", "1", "   "])
    
    assert code == 1
    assert "Validation Error: Task title cannot be empty." in out

def test_create_invalid_project(cli_env, monkeypatch, capsys):
    """Verify the CLI catches the IntegrityError from the database."""
    code, out, err = run_cli(monkeypatch, capsys, ["create", "9999", "Ghost Task"])
    
    assert code == 1
    # NEW ASSERTION: Check for the generic prefix and the actual SQLite error
    assert "Database Error:" in out
    assert "FOREIGN KEY constraint failed" in out

def test_project_create_success(cli_env, monkeypatch, capsys):
    """Verify creating a valid project via CLI."""
    code, out, err = run_cli(monkeypatch, capsys, ["project", "create", "CLI Project"])
    
    assert code == 0
    assert "Success: Created project with ID" in out

def test_project_create_empty_name(cli_env, monkeypatch, capsys):
    """Verify the CLI catches the ValueError for an empty project name."""
    code, out, err = run_cli(monkeypatch, capsys, ["project", "create", "   "])
    
    assert code == 1
    assert "Validation Error: Project name cannot be empty." in out