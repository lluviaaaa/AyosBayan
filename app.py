from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- DATABASE CONNECTION SETTINGS ---

# We tell Flask exactly where to find the database and how to log in.
# Format: database_type+connector://username:password@server_address/database_name
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Mysqlr00tp%40ssw0rd828@localhost/ayosbayan'

# We turn off an automatic tracking feature we don't need, which keeps our app running fast and prevents warning messages.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# We activate the SQLAlchemy translator and link it directly to our Flask app.
db = SQLAlchemy(app)

# ------------------------------------

# --- DATABASE BLUEPRINTS (MODELS) ---

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Auto-numbers every new admin (1, 2, 3...)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

class Ticket(db.Model):
    id = db.Column(db.String(20), primary_key=True) # This will be our "AB-1234" format
    issue_type = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Open') # Automatically sets new tickets to 'Open'
    date_reported = db.Column(db.String(50), nullable=False)

# ------------------------------------


def get_ticket_image_url(ticket_id):
    for ext in ALLOWED_EXTENSIONS:
        filename = f"{ticket_id}{ext}"
        path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(path):
            return url_for('static', filename=f'uploads/{filename}')
    return None

@app.route('/')
def role_selection():
    return render_template('index.html')

@app.route('/citizen')
def citizen_home():
    return render_template('citizen_home.html')

@app.route('/report/step1')
def report_step1():
    return render_template('report_step1.html')

@app.route('/report/step2', methods=['GET', 'POST'])
def report_step2():
    if request.method == 'POST':
        citizen_street = request.form.get('street')
        image_files = request.files.getlist('issue_photo')
        image_filename = None
        image_url = None

        if image_files:
            image_file = next((f for f in image_files if f and f.filename), None)
            if image_file:
                original_filename = secure_filename(image_file.filename)
                _, ext = os.path.splitext(original_filename)
                ext = ext.lower()
                if ext in ALLOWED_EXTENSIONS:
                    image_filename = f"tmp_{uuid.uuid4().hex}{ext}"
                    save_path = os.path.join(UPLOAD_FOLDER, image_filename)
                    image_file.save(save_path)
                    image_url = url_for('static', filename=f'uploads/{image_filename}')

        return render_template('report_step2.html', street=citizen_street, image_url=image_url, image_filename=image_filename)

    return redirect('/report/step1')

@app.route('/submit_report', methods=['POST'])
def submit_report():
    # 1. Grab what the citizen typed into the HTML form
    # (Make sure these names match the "name=" attributes in your HTML form!)
    form_issue = request.form.get('issue_type')
    form_street = request.form.get('street')
    form_desc = request.form.get('description')

    # 2. Generate the ID and get today's exact date
    new_id = f"AB-{random.randint(1000, 9999)}"
    today = datetime.now().strftime("%B %d, %Y")

    # Preserve the uploaded image: if the user selected one, rename it to match the ticket ID.
    uploaded_image = request.form.get('image_filename')
    if uploaded_image:
        temp_path = os.path.join(UPLOAD_FOLDER, uploaded_image)
        if os.path.exists(temp_path):
            _, ext = os.path.splitext(uploaded_image)
            final_path = os.path.join(UPLOAD_FOLDER, f"{new_id}{ext}")
            os.replace(temp_path, final_path)

    # 3. Create the real Ticket using our Database Blueprint
    new_ticket = Ticket(
        id=new_id,
        issue_type=form_issue,
        street=form_street,
        description=form_desc,
        date_reported=today
    )

    # 4. Save it permanently to MySQL!
    db.session.add(new_ticket)
    db.session.commit()

    # 5. Send them to the success page (you can adjust this URL to match yours)
    # 5. Send them to the success page AND pass the ID!
    return redirect(f'/report/success?ticket_id={new_id}')


@app.route('/report/success')
def report_success():
    # Catch the ID from the URL
    passed_id = request.args.get('ticket_id')
    
    # Hand it to the HTML page
    return render_template('report_success.html', ticket_id=passed_id)


# NEW Route for Citizen Screen 5: Public Board
# 1. The Citizen's Public Board
@app.route('/board')
def public_board():
    all_tickets = Ticket.query.all()
    return render_template('board.html', reports=all_tickets)

# 2. The Admin's Active Ledger
@app.route('/admin/board')
def admin_board():
    all_tickets = Ticket.query.all()
    return render_template('admin_board.html', reports=all_tickets)

# NEW Route for Citizen Screen 6: Specific Ticket View
# The <ticket_id> acts as a variable that changes based on what the user clicks
@app.route('/ticket/<ticket_id>')
def view_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return redirect('/board')

    ticket_image_url = get_ticket_image_url(ticket_id)
    return render_template('ticket_detail.html', ticket=ticket, ticket_image_url=ticket_image_url)



# --- ADMIN ROUTES ---

# Route for Admin Screen 1: Login
@app.route('/admin')
def admin_login():
    return render_template('admin_login.html')


# Route for Admin Screen 2: Main Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    # 1. Grab EVERY single ticket from the database
    all_tickets = Ticket.query.all()

    # 2. Attach thumbnails for any ticket with a saved image
    for report in all_tickets:
        report.thumbnail = get_ticket_image_url(report.id)

    # 3. Count the tickets so we can update the colorful metric cards at the top
    open_count = Ticket.query.filter_by(status='Open').count()
    progress_count = Ticket.query.filter_by(status='In Progress').count()
    resolved_count = Ticket.query.filter_by(status='Resolved').count()

    # 4. Send all this real data over to the HTML file
    return render_template(
        'admin_dashboard.html', # Make sure this matches your exact filename!
        reports=all_tickets,
        open_count=open_count,
        progress_count=progress_count,
        resolved_count=resolved_count
    )


# NEW Route: Handle Admin Status Updates
@app.route('/ticket/<ticket_id>/update', methods=['POST'])
def update_ticket(ticket_id):
    # This grabs the new status choice from the HTML dropdown
    new_status = request.form.get('status')
    ticket = Ticket.query.get(ticket_id)

    if ticket and new_status in ('Open', 'In Progress', 'Resolved'):
        ticket.status = new_status
        db.session.commit()

    return redirect('/admin/dashboard')

@app.route('/admin/resolved')
def admin_resolved():
    # Only grab tickets where the status is 'Resolved'
    resolved_tickets = Ticket.query.filter_by(status='Resolved').all()
    return render_template('admin_resolved.html', reports=resolved_tickets)

@app.route('/admin/resolve/<ticket_id>', methods=['POST'])
def resolve_ticket(ticket_id):
    # 1. Find the exact ticket in the database
    ticket = Ticket.query.get(ticket_id)
    
    # 2. If it exists, change its status and save it!
    if ticket:
        ticket.status = 'Resolved'
        db.session.commit()
        
    # 3. Reload the dashboard so the numbers update instantly
    return redirect('/admin/dashboard')

@app.route('/admin/settings')
def admin_settings():
    return render_template('admin_settings.html')

if __name__ == '__main__':
    app.run(debug=True)