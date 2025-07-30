# Flask App Structure with Templates and Static Files

# File: app.py
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


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    time_spent = db.Column(db.String(50))
    tool_used = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    ticket = db.relationship('Ticket', backref='tasks')
    

class TicketChangeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'))
    changed_by = db.Column(db.String(50))
    change_description = db.Column(db.Text)
    changed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# ------------------ ROUTES ------------------

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('create_user.html', error="User already exists")

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/users')  # or dashboard

    return render_template('create_user.html')

@app.route('/users')
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        if user:
            session['username'] = user.username
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/tasks/')
@app.route('/tasks')
def tasks():
    print("/tasks route was called")
    all_tasks = Task.query.all()
    return render_template('tasks.html', tasks=all_tasks)

@app.route('/tasks/create', methods=['GET', 'POST'])
def create_task():
    open_tickets = Ticket.query.filter(Ticket.status != 'Closed').all()

    if request.method == 'POST':
        description = request.form['description']
        ticket_id = request.form['ticket_id']
        time_spent = request.form['time_spent']
        tool_used = request.form['tool_used']

        task = Task(description=description, ticket_id=ticket_id, time_spent=time_spent, tool_used=tool_used)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('tasks'))

    return render_template('create_task.html', tickets=open_tickets)

@app.route('/tasks/<int:task_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('list_tasks'))

    return render_template('view_task.html', task=task, tickets=tickets)



@app.route('/tickets')
def tickets():
    all_tickets = Ticket.query.all()
    return render_template('tickets.html', tickets=all_tickets)

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
        requested_by = session.get('username')  # or however you're tracking login
        created_at = datetime.now(timezone.utc) 
        ticket_no = request.form.get('ticket_no')

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
        return redirect(url_for('tickets'))
    users = User.query.all()
    generated_ticket_no = str(uuid.uuid4())[:8]
    return render_template('create_ticket.html', users=users, ticket_no=generated_ticket_no)


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
        return redirect(url_for('tickets'))

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
                    author=session.get('username', 'Anonymous')  # fallback
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
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', password='admin123')
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
