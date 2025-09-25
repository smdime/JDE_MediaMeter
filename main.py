import mysql.connector
from mysql.connector import Error
import uuid
from datetime import datetime
class Task:
    """Represents a single task entity"""
    def __init__(self, task_id, title, description, due_date, priority, status, created_at):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.status = status
        self.created_at = created_at

    def __str__(self):
        return (f"[{self.task_id}] {self.title} | {self.priority} | {self.status} "
                f"| Due: {self.due_date} | Created: {self.created_at}")

class TaskManager:
    """Handles database operations for tasks"""
    def __init__(self, user, password, host="localhost", db="task_manager"):
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=db
            )
            self.cursor = self.conn.cursor(dictionary=True)
        except Error as e:
            print("Error connecting to MySQL:", e)
            self.conn = None
            self.cursor = None

    def __del__(self):
        if hasattr(self, 'conn') and self.conn and self.conn.is_connected():
            self.conn.close()

    def create_table(self):
        """Create the tasks table if it doesn't exist"""
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id VARCHAR(36) PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    due_date DATETIME,
                    priority ENUM('Low','Medium','High') DEFAULT 'Medium',
                    status ENUM('Pending','In Progress','Completed') DEFAULT 'Pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        self.conn.commit()

    def add_task(self, title, description=None, due_date=None, priority="Medium"):
        """Insert a new task"""
        tid = str(uuid.uuid4())
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tasks (task_id, title, description, due_date, priority, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (tid, title, description, due_date, priority, "Pending", datetime.now()))
        self.conn.commit()
        print(f"✅ Task added with ID {tid}")

    def list_tasks(self, status=None, priority=None):
        """List tasks with optional filters"""
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        if status:
            query += " AND status=%s"
            params.append(status)
        if priority:
            query += " AND priority=%s"
            params.append(priority)

        with self.conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            for row in rows:
                task = Task(**row)
                print(task)

    def update_task(self, task_id, field, value):
        """Update a specific field of a task"""
        if field not in ["title", "description", "due_date", "priority", "status"]:
            print("❌ Invalid field")
            return
        query = f"UPDATE tasks SET {field}=%s WHERE task_id=%s"
        with self.conn.cursor() as cur:
            cur.execute(query, (value, task_id))
        self.conn.commit()
        print("✅ Task updated")

    def mark_completed(self, task_id):
        """Mark a task as completed"""
        self.update_task(task_id, "status", "Completed")

    def delete_task(self, task_id):
        """Delete a task by ID"""
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE task_id=%s", (task_id,))
        self.conn.commit()
        print("🗑️ Task deleted")

    def __del__(self):
        self.conn.close()

# CLI
def main():
    manager = TaskManager(user="root", password="password", db="task_manager")

    while True:
        print("\n--- Task Manager (MySQL, raw SQL) ---")
        cmd = input("Enter command (add/list/update/complete/delete/quit): ").strip().lower()

        if cmd == "add":
            title = input("Title: ")
            desc = input("Description: ")
            due = input("Due date (YYYY-MM-DD or blank): ")
            priority = input("Priority (Low/Medium/High): ") or "Medium"
            due_date = datetime.strptime(due, "%Y-%m-%d") if due else None
            manager.add_task(title, desc, due_date, priority)

        elif cmd == "list":
            status = input("Filter by status (Pending/In Progress/Completed or blank): ")
            priority = input("Filter by priority (Low/Medium/High or blank): ")
            manager.list_tasks(status or None, priority or None)

        elif cmd == "update":
            tid = input("Task ID: ")
            field = input("Field (title/description/due_date/priority/status): ")
            value = input("New value: ")
            if field == "due_date":
                value = datetime.strptime(value, "%Y-%m-%d")
            manager.update_task(tid, field, value)

        elif cmd == "complete":
            tid = input("Task ID: ")
            manager.mark_completed(tid)

        elif cmd == "delete":
            tid = input("Task ID: ")
            manager.delete_task(tid)

        elif cmd in ("quit", "exit"):
            break
        else:
            print("❌ Invalid command")

if __name__ == "__main__":
    main()
