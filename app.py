from flask import Flask, render_template
import random # NEW: This lets us pick random numbers

app = Flask(__name__)

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
    return render_template('report_step2.html')

# NEW Route for Citizen Screen 4: Success Confirmation
@app.route('/report/success')
def report_success():
    # Generate a random 4-digit number for the ticket
    random_number = random.randint(1000, 9999)
    ticket_id = f"AB-{random_number}"
    
    # Pass the ticket_id to our HTML file
    return render_template('report_success.html', ticket_id=ticket_id)

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

# Temporary placeholder for the Admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    return "<h1>Admin Dashboard Coming Soon!</h1>"


if __name__ == '__main__':
    app.run(debug=True)