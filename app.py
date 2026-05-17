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

if __name__ == '__main__':
    app.run(debug=True)