# Flask Task Manager

A lightweight task and ticket management web application built with Flask, SQLAlchemy, and SQLite.

## 🚀 Features

- Create tickets with **auto-generated ticket numbers**
- Assign tickets to users, track statuses (New, In Progress, On Hold, Closed)
- Add comments/logs to tickets via a detailed view
- Create tasks associated with **open tickets**, tracking:
  - Description
  - Time spent
  - Tool used
  - Assignment and status
- Modern UI using Bootstrap for responsive, clean layouts

## 🧭 Project Structure

```
flask-taskmanager/
├── app.py                 # Main Flask app with routes and models
├── dashboard.db           # SQLite database
├── templates/             # Jinja templates
│   ├── login.html
│   ├── dashboard.html
│   ├── tickets.html
│   ├── create_ticket.html
│   ├── ticket_detail.html
│   ├── tasks.html
│   └── create_task.html
├── static/
│   ├── css/
│   └── js/
└── README.md
```



## 🛠️ Getting Started

### Prerequisites

- Python 3.8+
- `pip` package manager

### Installation

```bash
git clone https://github.com/achyutvarma/flask-taskmanager.git
cd flask-taskmanager
python -m venv venv
source venv/bin/activate        # On Windows use: venv\Scripts\activate
pip install Flask Flask-SQLAlchemy Flask-Migrate

# Run the Application
python app.py

Access at http://127.0.0.1:5000/ and log in with default credentials:
admin / admin123
```

###

# Login
<img width="943" height="470" alt="image" src="https://github.com/user-attachments/assets/418918b8-dce4-475c-aac4-1773e63c51d7" />

# Dahboard

<img width="943" height="483" alt="image" src="https://github.com/user-attachments/assets/e69e94bf-025b-4d9a-a855-de16e8e73f5d" />

# Core Models
- User: holds username, password, full name.
- Ticket: tracks tickets with ticket_no, title, description, status, assigned user, comments.
- Comment: linked to tickets — logged by users when updating tickets.
- Task: associated with open tickets, capturing time spent, tool, description, status.

# Usage Flow
- Sign in as a user.
- Navigate to /tickets to see all tickets.
- Create a new ticket via /create_ticket, then view ticket details.
- In the Ticket Detail page:
- Change status or assignee.
- Use the Add Comment section to log notes.
  # Create user
  <img width="950" height="474" alt="image" src="https://github.com/user-attachments/assets/fdb30ea7-55ee-4618-bc28-52a802793a7a" />

  # After creating the users
  <img width="949" height="475" alt="image" src="https://github.com/user-attachments/assets/b869ada3-468c-451a-b411-c3c2db4e8425" />

  # Tickets(/tickets)
   <img width="941" height="440" alt="image" src="https://github.com/user-attachments/assets/91bd0cd5-399b-4bca-a3c1-5791ec8dba2f" />

  # Create tickets
  <img width="915" height="473" alt="image" src="https://github.com/user-attachments/assets/082294ff-65c4-46ae-87c1-1767e4c07324" />

  # View ticket
  <img width="938" height="482" alt="image" src="https://github.com/user-attachments/assets/1dcbe671-f2ca-485e-a346-b91077127bdd" />


- Go to /tasks/add to create a new task:
  - Select from tickets with statuses other than Closed.
  - Provide description, time spent, tool used, etc.
- Review all tasks on the main /tasks page.

  # Tasks
  <img width="956" height="468" alt="image" src="https://github.com/user-attachments/assets/75b30437-acf2-4882-a056-c9d9b050889b" />

  # Create tasks
  <img width="958" height="470" alt="image" src="https://github.com/user-attachments/assets/243a4566-ce1d-4eed-aeea-9881591e0c58" />

  # View/Edit
  <img width="951" height="467" alt="image" src="https://github.com/user-attachments/assets/72a276da-3c00-4f1c-8f85-bc5bc1468a0f" />


# Development Notes
- Use Flask-Migrate to handle schema changes going forward.
- For production, consider using PostgreSQL or MySQL instead of SQLite.
- Expandable features: user permissions, file attachments preview, email notifications, API endpoints.





