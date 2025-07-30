from app import app, db, Task
from datetime import datetime

# Use application context
with app.app_context():
    task = Task(
        title="Sample Task",
        description="This is a sample task.",
        assigned_to="admin",
        status="To Do",
        due_date=datetime(2025, 7, 31)
    )
    db.session.add(task)
    db.session.commit()
    print("Task added successfully.")
