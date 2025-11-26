from flask import Flask, render_template, request, redirect, jsonify, flash
import mysql.connector
from mysql.connector import Error
import re

app = Flask(__name__)
app.secret_key = "event_portal_secret_key_2024"

# --------------------------
# DATABASE CONNECTION
# --------------------------
def get_db_connection():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="dbms@2007",
            database="event_portal"
        )
        return db
    except Error as err:
        if err.errno == 2003:
            print("Error: Could not connect to MySQL Server")
        elif err.errno == 1045:
            print("Error: Invalid username or password")
        else:
            print(f"Error: {err}")
        return None

# Initialize connection
db = get_db_connection()
if db:
    cursor = db.cursor(dictionary=True)
else:
    print("Warning: Database connection failed")
    cursor = None

# Input validation functions
def is_valid_usn(usn):
    """Validate USN format"""
    return bool(re.match(r"^[A-Z0-9]{10}$", usn))

def is_valid_reg_id(reg_id):
    """Validate Registration ID format"""
    return bool(re.match(r"^[0-9]+$", reg_id))

def is_valid_rating(rating):
    """Validate rating is between 1 and 5"""
    try:
        r = int(rating)
        return 1 <= r <= 5
    except ValueError:
        return False

# --------------------------
# HOME PAGE
# --------------------------
@app.route("/")
def home():
    return render_template("index.html")

# --------------------------
# VIEW ALL EVENTS
# --------------------------
@app.route("/events")
def events():
    try:
        if cursor is None:
            return render_template("error.html", message="Database connection failed"), 500
        
        cursor.execute("SELECT * FROM event ORDER BY event_date DESC")
        data = cursor.fetchall()
        return render_template("events.html", events=data)
    except Error as err:
        return render_template("error.html", message=f"Database error: {err}"), 500

# --------------------------
# REGISTER STUDENT TO EVENT
# --------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    try:
        if cursor is None:
            return render_template("error.html", message="Database connection failed"), 500
        
        if request.method == "POST":
            reg_id = request.form.get("reg_id", "").strip()
            event_id = request.form.get("event_id", "").strip()
            usn = request.form.get("usn", "").upper().strip()

            # Input validation
            if not reg_id or not is_valid_reg_id(reg_id):
                return render_template("register.html", events=get_events(), error="Invalid Registration ID"), 400

            if not event_id:
                return render_template("register.html", events=get_events(), error="Please select an event"), 400

            if not usn or not is_valid_usn(usn):
                return render_template("register.html", events=get_events(), error="Invalid USN format (10 alphanumeric characters)"), 400

            # Check if already registered
            cursor.execute(
                "SELECT * FROM registration WHERE USN = %s AND event_id = %s",
                (usn, event_id)
            )
            if cursor.fetchone():
                return render_template("register.html", events=get_events(), error="Already registered for this event"), 400

            query = """
            INSERT INTO registration (reg_id, event_id, USN)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (reg_id, event_id, usn))
            db.commit()

            return render_template("success.html", message="Registration Successful!", link_text="View Events", link_url="/events")

        events_list = get_events()
        return render_template("register.html", events=events_list)
    except Error as err:
        db.rollback()
        return render_template("error.html", message=f"Database error: {err}"), 500

# --------------------------
# SUBMIT FEEDBACK
# --------------------------
@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    try:
        if cursor is None:
            return render_template("error.html", message="Database connection failed"), 500
        
        if request.method == "POST":
            event_id = request.form.get("event_id", "").strip()
            usn = request.form.get("usn", "").upper().strip()
            rating = request.form.get("rating", "").strip()
            comment = request.form.get("comment", "").strip()

            # Input validation
            if not event_id:
                return render_template("feedback.html", events=get_events(), error="Please select an event"), 400

            if not usn or not is_valid_usn(usn):
                return render_template("feedback.html", events=get_events(), error="Invalid USN format"), 400

            if not is_valid_rating(rating):
                return render_template("feedback.html", events=get_events(), error="Rating must be between 1 and 5"), 400

            if len(comment) > 500:
                return render_template("feedback.html", events=get_events(), error="Comment must be less than 500 characters"), 400

            query = """
            INSERT INTO feedback (event_id, USN, rating, comment)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (event_id, usn, rating, comment))
            db.commit()

            return render_template("success.html", message="Feedback Submitted Successfully!", link_text="View Events", link_url="/events")

        events_list = get_events()
        return render_template("feedback.html", events=events_list)
    except Error as err:
        db.rollback()
        return render_template("error.html", message=f"Database error: {err}"), 500

# --------------------------
# HELPER FUNCTIONS
# --------------------------
def get_events():
    """Fetch all events from database"""
    try:
        if cursor is None:
            return []
        cursor.execute("SELECT event_id, event_name FROM event ORDER BY event_date DESC")
        return cursor.fetchall()
    except Error:
        return []
   




# --------------------------
# RUN APP
# --------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5004)
    
 