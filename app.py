# Flask App Structure with Templates and Static Files

# File: app.py
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required,current_user
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timezone
import uuid
from flask_migrate import Migrate


app = Flask(__name__)
app.secret_key = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dashboard.db'
db = SQLAlchemy(app)
# After initializing db
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # your login route name

import os
from werkzeug.utils import secure_filename

# Ensure the uploads/ directory exists
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# ------------------ MODELS ------------------

# Your models here

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    ticket = db.relationship("Ticket", back_populates="comments")

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_no = db.Column(db.String(50), unique=True, default=lambda: str(uuid.uuid4())[:8])
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    comments = db.relationship("Comment", back_populates="ticket", cascade="all, delete-orphan")
    status = db.Column(db.String(50), default='New')
    severity = db.Column(db.String(10))
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id')) 
    assigned_user = db.relationship('User', backref='tickets') # You can use comma-separated user names or a many-to-many relation
    requested_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    attachment = db.Column(db.String(200))  # store the uploaded filename


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), default='admin') 

    def __repr__(self):
        return f'<User {self.username}>'


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    time_spent = db.Column(db.Integer)
    tool_used = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 👈 Add this line
    created_by = db.relationship('User', backref='created_tasks') 

    ticket = db.relationship('Ticket', backref='tasks')
    

class TicketChangeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'))
    changed_by = db.Column(db.String(50))
    change_description = db.Column(db.Text)
    changed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# ------------------ ROUTES ------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if current_user.role!= 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'user')  # default to user

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error = "Username already exists."
            return render_template('create_user.html', error= error)

        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash(f"User {username} created with role {role}.", "success")
        return redirect(url_for('home'))

    return render_template('create_user.html',error=None)

@app.route('/users')
def list_users():
    if current_user.role!= 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    users = User.query.all()
    return render_template('user.html', users=users)


DEFAULT_ADMIN_USERNAME = "admin" 
@app.route('/')
@login_required
def home():
    users = []
    if current_user.role == 'admin':
        users = User.query.all()
    return render_template('dashboard.html', users=users,default_admin=DEFAULT_ADMIN_USERNAME)


from flask_login import login_user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()

        if user and user.password == request.form['password']:  # ideally hash check
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

from flask_login import logout_user

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if current_user.role!= 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home'))

    user = User.query.get_or_404(user_id)
    if user.username == current_user.username:
        flash('You cannot delete yourself.', 'warning')
        return redirect(url_for('home'))
    
    if user.username == DEFAULT_ADMIN_USERNAME:
        flash('You cannot delete the default admin.', 'danger')
        return redirect(url_for('home'))

    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted successfully.', 'success')
    return redirect(url_for('home'))

from flask_login import current_user

from flask_login import login_required, current_user

@app.route('/tasks/')
@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    selected_user_id = request.args.get('user_id')

    if current_user.role == 'admin':
        users = User.query.all()

        if selected_user_id:
            tasks = Task.query.filter_by(created_by_id=selected_user_id).all()
        else:
            tasks = Task.query.all()

        return render_template('tasks.html', tasks=tasks, users=users, selected_user_id=selected_user_id)
    
    else:
        # Normal user: only see their own tasks
        tasks = Task.query.filter_by(created_by_id=current_user.id).all()
        return render_template('tasks.html', tasks=tasks, users=None)

# Add login_required to ensure only logged-in users can access this
@app.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    open_tickets = Ticket.query.filter(Ticket.status != 'Closed').all()

    if request.method == 'POST':
        description = request.form['description']
        ticket_id = request.form['ticket_id']
        time_spent = request.form['time_spent']
        tool_used = request.form['tool_used']
        try:
            # Validate and convert to float
            time_spent = float(request.form['time_spent'])

            # Optional: You can check for negative numbers
            if time_spent < 0:
                raise ValueError("Time spent must be non-negative.")

        except ValueError:
            flash("Please enter a valid number for time spent.", "danger")
            return render_template('create_task.html', tickets=open_tickets)
        #  Include created_by_id from current_user.id
        task = Task(
            description=description,
            ticket_id=ticket_id,
            time_spent=time_spent,
            tool_used=tool_used,
            created_by_id=current_user.id
        )

        db.session.add(task)
        db.session.commit()
        return redirect(url_for('tasks'))

    return render_template('create_task.html', tickets=open_tickets)

@app.route('/tasks/<int:task_id>', methods=['GET', 'POST'])
@login_required
def view_task(task_id):
    task = Task.query.get_or_404(task_id)
    tickets = Ticket.query.filter(Ticket.status != 'Closed').all()

    if request.method == 'POST':
        task.description = request.form['description']
        task.ticket_id = request.form['ticket_id']
        task.time_spent = request.form['time_spent']
        task.tool_used = request.form['tool_used']
        db.session.commit()
        flash("Task updated successfully", "success")
        return redirect(url_for('tasks'))

    return render_template('view_task.html', task=task, tickets=tickets)

import random
import string

def generate_ticket_number():
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"SR{random_part}"



from flask_login import current_user, login_required
from flask import redirect, url_for, flash



@app.route('/tickets')
def list_tickets():
    if not current_user.is_authenticated:
        flash('Please log in to view tickets.', 'danger')
        return redirect(url_for('login'))

    selected_user_id = request.args.get('user', type=int)
    selected_status = request.args.get('status', default='open')
   

    query = Ticket.query

    # Role-based ticket visibility
    if current_user.role == 'admin':
        if selected_user_id:
            query = query.filter(Ticket.assigned_to == selected_user_id)
    else:
        query = query.filter(
            (Ticket.requested_by == current_user.id) |
            (Ticket.assigned_user.has(id=current_user.id))
        )

    # Status filter
    if selected_status == 'open':
        query = query.filter(Ticket.status != 'Closed')
    elif selected_status == 'closed':
        query = query.filter(Ticket.status == 'Closed')
    # else 'all' – no additional filter

    tickets = query.all()
    users = User.query.all() if current_user.role == 'admin' else []

    return render_template(
        'tickets.html',
        tickets=tickets,
        users=users,
        selected_user_id=selected_user_id,
        current_user_role=current_user.role,
        selected_status=selected_status
    )


import os
from flask import request, redirect, render_template, url_for, flash
from werkzeug.utils import secure_filename

@app.route('/create_ticket', methods=['GET', 'POST'])
def create_ticket():
    users = User.query.all()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        status = request.form.get('status', 'New')
        severity = request.form.get('severity')
        assigned_to = request.form.get('assigned_to')
        assigned_to = int(assigned_to) if assigned_to else None 
        requested_by = current_user.username # or however you're tracking login
        created_at = datetime.now(timezone.utc) 
        ticket_no = request.form['ticket_no'] 

        file = request.files['attachment']
        filename = None
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join('uploads', filename))  # Ensure uploads/ folder exists

        ticket = Ticket(
            title=title,
            description=description,
            status=status,
            severity=severity,
            assigned_to=assigned_to,
            requested_by=requested_by,
            created_at=created_at,
            ticket_no=ticket_no,
            attachment=filename
        )

        db.session.add(ticket)
        db.session.commit()
        return redirect(url_for('list_tickets'))
    
    users = User.query.all()
    ticket_no = generate_ticket_number() 
    return render_template('create_ticket.html', users=users,ticket_no=ticket_no)


@app.route('/update_ticket/<int:id>', methods=['POST'])
def update_ticket(id):
    ticket = Ticket.query.get_or_404(id)
    new_status = request.form['status']
    ticket.status = new_status
    db.session.commit()
    return redirect('/tickets')

@app.route('/ticket/<int:ticket_id>', methods=['GET', 'POST'])
def ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    users = User.query.all()

    if request.method == 'POST':
        ticket.status = request.form['status']
        ticket.description = request.form['description']
        assigned_user_id = request.form.get('assigned_to')
        ticket.assigned_to = assigned_user_id
        db.session.commit()
        flash("Ticket updated successfully!", "success")
        return redirect(url_for('list_tickets'))

    return render_template('ticket_detail.html', ticket=ticket, users=users)

@app.route('/edit_ticket/<int:ticket_id>', methods=['GET', 'POST'])
def edit_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    users = User.query.all()

    if request.method == 'POST':
        if 'new_comment' in request.form:
            # This is a comment submission
            new_comment = request.form.get('new_comment')
            if new_comment:
                comment = Comment(
                    content=new_comment,
                    ticket_id=ticket.id,
                    author=current_user.username if current_user.is_authenticated else 'Anonymous'# fallback
                )
                db.session.add(comment)
                db.session.commit()
                flash('Comment added successfully!', 'success')
        else:
            # This is a ticket update submission
            ticket.status = request.form.get('status')
            assigned_to = request.form.get('assigned_to')
            ticket.assigned_to = int(assigned_to) if assigned_to else None
            ticket.description = request.form.get('description')
            db.session.commit()
            flash('Ticket updated successfully!', 'success')

        return redirect(url_for('ticket_detail', ticket_id=ticket.id))

    return render_template('ticket_detail.html', ticket=ticket, users=users)




# ------------------ MAIN ------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        #  Auto-create admin user if it doesn't exist
        if not User.query.filter_by(username=DEFAULT_ADMIN_USERNAME).first():
            admin_user = User(username=DEFAULT_ADMIN_USERNAME, password='admin123')
            db.session.add(admin_user)
            db.session.commit()
            print(" Admin user created: admin / admin123")
        else:
            print("Admin user already exists.")

        #  Print all registered routes
        print("\nAll registered routes:")
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule}")

    app.run(debug=True)


# ------------------ Folder Structure ------------------
# task_manager/
# ├── app.py
# ├── dashboard.db
# ├── venv/
# ├── static/
# │   ├── css/
# │   │   └── styles.css
# │   ├── js/
# │   │   └── main.js
# │   └── images/
# │       ├── logo.png
# │       └── user-avatar.png
# └── templates/
#     ├── login.html
#     ├── dashboard.html
#     ├── tasks.html
#     └── tickets.html

# ------------------ Static Files ------------------
# static/css/styles.css
# body {
#   background-color: #121212;
#   color: #ffffff;
# }
# a {
#   color: #cccccc;
# }
# a:hover {
#   color: #ffffff;
#   text-decoration: none;
# }

# static/js/main.js
# console.log("Dashboard script loaded.");

# static/images/
# logo.png - (example: a small brand logo)
# user-avatar.png - (example: placeholder avatar image)
