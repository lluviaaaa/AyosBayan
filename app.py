from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

app = Flask(__name__)

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


@app.route('/')
def role_selection():
    return render_template('index.html')

@app.route('/citizen')
def citizen_home():
    return render_template('citizen_home.html')

@app.route('/report/step1')
def report_step1():
    return render_template('report_step1.html')

@app.route('/report/step2')
def report_step2():
    # Catch the street name passed from Step 1
    citizen_street = request.args.get('street')
    
    # Hand it over to the Step 2 HTML page
    return render_template('report_step2.html', street=citizen_street)

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
    return redirect('/report/success')


@app.route('/report/success')
def report_success():
    # Make sure 'report_success.html' matches the actual name of your success HTML file! 
    # (It might be just 'success.html' in your templates folder)
    return render_template('report_success.html')


# NEW Route for Citizen Screen 5: Public Board
@app.route('/board')
def public_board():
    # This is "dummy data" simulating our database ledger for now
    fake_reports = [
        {"id": "AB-1029", "type": "Deep Pothole", "street": "Rizal St.", "status": "Open", "date": "May 17, 2026", "badge_color": "gray"},
        {"id": "AB-0984", "type": "Uncollected Garbage", "street": "Mabini St.", "status": "In Progress", "date": "May 16, 2026", "badge_color": "orange"},
        {"id": "AB-0811", "type": "Broken Streetlight", "street": "Luna St.", "status": "Resolved", "date": "May 10, 2026", "badge_color": "green"}
    ]
    return render_template('public_board.html', reports=fake_reports)

# NEW Route for Citizen Screen 6: Specific Ticket View
# The <ticket_id> acts as a variable that changes based on what the user clicks
@app.route('/ticket/<ticket_id>')
def view_ticket(ticket_id):
    # In the future, this is where we will ask MySQL for the real ticket data.
    # For now, we will generate some dummy data to make the screen look real.
    mock_ticket = {
        "id": ticket_id,
        "type": "Deep Pothole",
        "street": "Rizal St.",
        "description": "The pothole is getting wider and takes up half the lane.",
        "status": "Open",
        "date": "May 17, 2026",
    }
    return render_template('ticket_detail.html', ticket=mock_ticket)



# --- ADMIN ROUTES ---

# Route for Admin Screen 1: Login
@app.route('/admin')
def admin_login():
    return render_template('admin_login.html')


# Route for Admin Screen 2: Main Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    # 1. Grab EVERY ticket from the database
    all_tickets = Ticket.query.all()

    # 2. Count the tickets for our top metric cards
    open_count = Ticket.query.filter_by(status='Open').count()
    progress_count = Ticket.query.filter_by(status='In Progress').count()
    resolved_count = Ticket.query.filter_by(status='Resolved').count()

    # 3. Send the tickets and the math to the HTML dashboard
    return render_template(
        'admin_dashboard.html', 
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
    
    # In the future, this is where we will tell MySQL to save the new status!
    # For now, we will just send the admin back to the dashboard.
    return redirect('/admin/dashboard')


if __name__ == '__main__':
    app.run(debug=True)