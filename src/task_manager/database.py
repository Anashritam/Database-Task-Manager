import sqlite3
from pathlib import Path

def get_connection(db_path: Path) -> sqlite3.Connection:
    connection= sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def initialize_database(db_path: Path)-> None:
    db_path.parent.mkdir(parents = True, exist_ok=True)
    schema_path = Path(__file__).resolve().parents[2]/"schema.sql"
    schema_sql = schema_path.read_text(encoding = "utf-8")

    connection = get_connection(db_path)

    try:
        connection.executescript(schema_sql)
    finally:
        connection.close()