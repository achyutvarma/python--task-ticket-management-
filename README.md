# 🛠️ Task & Ticket Management System

A **Flask-based web application** for managing users, support tickets, and tasks with **role-based permissions** (Admin and Regular Users).

---

## 🚀 Features

### 🔐 User Authentication
- Secure login and logout powered by `Flask-Login`.

### 👥 Role-Based Access Control
- **Admin users** can:
  - Create, edit, and delete users.
  - View and filter all tasks and tickets.
- **Regular users** can:
  - Perform actions associated only with their own account.

### 🧑‍💼 User Management (Admin Only)
- Create new users with roles (`admin` or `user`).
- Prevent deletion of:
  - Logged-in admin's own account.
  - Default admin account.
- Delete other users using a **confirmation modal**.

### 🎫 Ticket Management
- Auto-generate ticket numbers in the format `SRXXXXXX` (e.g., `SRB7X9NJ`) with:
  - `SR` prefix
  - Random uppercase letters/digits.
- Ticket number is shown **on creation and listing**, consistently.
- Filter tickets by **status** (`New`, `In Progress`, `On Hold`, `Closed`) with access control:
  - Admin sees all tickets.
  - Regular users see only their own.

### ✅ Task Management
- Create tasks associated only with **open tickets**.
- Time Spent field accepts only **numeric input** (int or float).
- Admin can **filter tasks by user**.
- Regular users see only their own tasks.

---

## 🧾 Components & File Structure

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
- **Models**: SQLAlchemy models (`User`, `Ticket`, `Task`, `Comment`)
- **Routes**:
  - Login/logout
     <img width="1886" height="947" alt="image" src="https://github.com/user-attachments/assets/89e609ba-b868-473a-adfc-355317b1d4ec" />

  - Dashboard view
     <img width="1862" height="946" alt="image" src="https://github.com/user-attachments/assets/63297708-bd3e-41d4-a1e9-420811a34630" />

  - User creation/deletion
      <img width="1572" height="421" alt="image" src="https://github.com/user-attachments/assets/5d5e629a-04ea-4b09-9efc-e04c8eda6ea9" />

  - Ticket/Task CRUD
      <img width="1866" height="926" alt="image" src="https://github.com/user-attachments/assets/4df91725-7fbb-4ece-904a-fb1a3da74845" />

      <img width="1899" height="923" alt="image" src="https://github.com/user-attachments/assets/daa2948b-d34f-4f3f-9f46-94ffbd013835" />

      <img width="1877" height="944" alt="image" src="https://github.com/user-attachments/assets/8a1a87de-14bf-47f5-919c-4dddc3a92ca1" />

      <img width="1878" height="923" alt="image" src="https://github.com/user-attachments/assets/0fdd9011-b84e-457b-a6c2-4e00cadbfb5e" />



- **Utilities**:
  - `generate_ticket_number()` → auto-generates ticket numbers in `SRXXXXXX` format
  - Role checks & validation logic

---

## 🧑‍💻 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/achyutvarma/python--task-ticket-management-.git
cd python--task-ticket-management-
2. Create and Activate Virtual Environment

python3 -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
3. Install Dependencies

pip install flask flask_sqlalchemy flask_login flask_migrate
4. Run the App

python app.py
Default Admin Credentials
Username: admin
Password: admin123

5. Open in Browser
Visit: http://127.0.0.1:5000
```

## Usage Tips
- Admin Dashboard:
  Create new users, assign roles.
  Filter and view all tickets and tasks.

- Regular User View:
  Cannot access user management section.
  Limited to their own tickets and tasks.

  

- Creating a Ticket:
  Auto-assigned number like SRX5B2K8 shown in form and used everywhere consistently.

- Form Validations:
  Only numeric input allowed for "Time Spent".
  Error messages shown for invalid inputs.

# ✅ Default Admin Configuration
The application defines a variable in app.py:


DEFAULT_ADMIN_USERNAME = "admin"
This ensures:

The default admin account cannot be deleted by anyone.

The username can be changed centrally in the backend without modifying HTML templates.
