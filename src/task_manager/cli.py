import argparse
import sys
import sqlite3
from pathlib import Path

from task_manager.database import get_connection, initialize_database
from task_manager import services

DB_PATH = Path("data/task_manager.db")

def main():
    # 1. Set up the argument parser FIRST (No database connection yet!)
    parser = argparse.ArgumentParser(description="Database Task Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: project
    project_parser = subparsers.add_parser("project", help="Manage projects")
    project_subparsers = project_parser.add_subparsers(dest="project_command", required=True)
    project_create_parser = project_subparsers.add_parser("create", help="Create a new project")
    project_create_parser.add_argument("name", type=str, help="Project name")

    # Command: create (task)
    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("project_id", type=int, help="Project ID")
    create_parser.add_argument("title", type=str, help="Task title")
    create_parser.add_argument("--description", type=str, help="Task description", default=None)

    # Command: list
    subparsers.add_parser("list", help="List all tasks")

    # Command: show
    show_parser = subparsers.add_parser("show", help="Show a specific task")
    show_parser.add_argument("task_id", type=int, help="Task ID")

    # Command: update
    update_parser = subparsers.add_parser("update", help="Update a task's title")
    update_parser.add_argument("task_id", type=int, help="Task ID")
    update_parser.add_argument("new_title", type=str, help="New task title")

    # Command: delete
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", type=int, help="Task ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 2. Initialize connection to None so the finally block can check it safely
    conn = None
    
    try:
        # 3. NOW we initialize the database and open the connection INSIDE the try block
        initialize_database(DB_PATH)
        conn = get_connection(DB_PATH)

        # 4. Execute the requested command using the SERVICE layer
        if args.command == "project" and args.project_command == "create":
            project_id = services.create_project_service(conn, args.name)
            print(f"Success: Created project with ID {project_id}")

        elif args.command == "create":
            task_id = services.create_task_service(
                conn, args.project_id, args.title, args.description
            )
            print(f"Success: Created task with ID {task_id}")

        elif args.command == "list":
            tasks = services.list_tasks_service(conn)
            if not tasks:
                print("No tasks found.")
            else:
                for task in tasks:
                    print(f"[{task['id']}] {task['title']} (Status: {task['status']}, Priority: {task['priority']})")

        elif args.command == "show":
            task = services.get_task_service(conn, args.task_id)
            if task:
                print(f"Task ID: {task['id']}")
                print(f"Title:   {task['title']}")
                print(f"Status:  {task['status']}")
                print(f"Priority:{task['priority']}")
            else:
                print(f"Error: Task with ID {args.task_id} not found.")

        elif args.command == "update":
            success = services.update_task_title_service(conn, args.task_id, args.new_title)
            if success:
                print(f"Success: Updated task {args.task_id}.")
            else:
                print(f"Error: Task with ID {args.task_id} not found.")

        elif args.command == "delete":
            success = services.delete_task_service(conn, args.task_id)
            if success:
                print(f"Success: Deleted task {args.task_id}.")
            else:
                print(f"Error: Task with ID {args.task_id} not found.")

    # 5. Handle errors gracefully
    except ValueError as e:
        print(f"Validation Error: {e}")
        sys.exit(1)
    except sqlite3.IntegrityError as e:
        # FIX 2: Removed "Invalid relationship." to avoid misleading the user 
        # if the error was actually a UNIQUE or NOT NULL constraint violation.
        print(f"Database Error: {e}")
        sys.exit(1)
    except sqlite3.Error as e:
        print(f"Database Error: An unexpected database error occurred. {e}")
        sys.exit(1)
    finally:
        # FIX 1: Only close the connection if it was successfully created.
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    main()