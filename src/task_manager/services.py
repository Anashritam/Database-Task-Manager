import sqlite3
from . import repository

def create_task_service(
        connection: sqlite3.Connection,
        project_id: int,
        title: str,
        description: str | None=None,
) -> int:

    title = title.strip()
    if not title:
        raise ValueError("Task title cannot be empty.")

    with connection:
        task_id = repository.create_task(
            connection,
            project_id,
            title,
            description,
        )

    return task_id

def get_task_service(
        connection: sqlite3.Connection,
        task_id: int,
) -> sqlite3.Row | None:

    return repository.get_task_by_id(connection, task_id)

def update_task_title_service(
        connection: sqlite3.Connection,
        task_id: int,
        new_title: str,
)-> bool:

    new_title = new_title.strip()

    if not new_title:
        raise ValueError("Task title cannot be empty.")

    with connection:
        success = repository.update_task_title(connection, task_id, new_title)

    return success

def delete_task_service(
        connection: sqlite3.Connection,
        task_id: int,
)-> bool:

    with connection:
        success= repository.delete_task(connection, task_id)

    return success

def list_tasks_service(
    connection: sqlite3.Connection,
) -> list[sqlite3.Row]:
    """Retrieve all tasks from the database."""
    # Read operation: no transaction block needed.
    return repository.list_tasks(connection)


def create_project_service(
    connection: sqlite3.Connection,
    name: str,
) -> int:
    name = name.strip()

    if not name:
        raise ValueError("Project name cannot be empty.")

    with connection:
        project_id = repository.create_project(connection, name)

    return project_id