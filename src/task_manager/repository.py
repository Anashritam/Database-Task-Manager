import sqlite3
def create_task(
        connection: sqlite3.Connection,
        project_id: int,
        title: str,
        description: str| None=None
)-> int:
    sql = """
        INSERT INTO tasks (project_id, title, description)
        VALUES(?, ?, ?)
    """
    cursor = connection.execute(sql, (project_id, title, description))

    # connection.commit()

    return cursor.lastrowid

def get_task_by_id(
        connection: sqlite3.Connection,
        task_id: int
) -> sqlite3.Row | None:

    sql = "SELECT * FROM tasks WHERE id = ?"

    cursor = connection.execute(sql,(task_id,))

    return cursor.fetchone()

def list_tasks(
        connection: sqlite3.Connection,
)-> list[sqlite3.Row]:
    sql = "SELECT * FROM tasks ORDER BY id ASC"

    cursor = connection.execute(sql)

    return cursor.fetchall()

def update_task_title(
        connection: sqlite3.Connection,
        task_id: int,
        new_title: str,
)-> bool:

    sql = "UPDATE tasks SET title = ? WHERE id = ?"

    cursor = connection.execute(sql, (new_title, task_id))

    return cursor.rowcount>0

def delete_task(
        connection: sqlite3.Connection,
        task_id:int
) -> bool:
    sql = "DELETE FROM tasks WHERE id = ?"

    cursor = connection.execute(sql,(task_id,))

    return cursor.rowcount > 0