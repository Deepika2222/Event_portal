from contextlib import closing
from datetime import datetime
from flask import Flask, render_template, request, flash
import mysql.connector
from mysql.connector import Error
import re

app = Flask(__name__)
app.secret_key = "event_portal_secret_key_2024"


@app.context_processor
def inject_globals():
    return {"current_year": datetime.now().year}

# --------------------------
# DATABASE CONNECTION HELPERS
# --------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "dbms@2007",
    "database": "event_portal",
    "autocommit": False,ls -a





def get_db_connection():
    """Create a new database connection."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as err:
        app.logger.error("Database connection failed: %s", err)
        return None


# Input validation functions (aligned with INT columns in DB)
def is_valid_numeric(value: str) -> bool:
    return bool(re.fullmatch(r"\d+", value or ""))


def is_valid_rating(rating: str) -> bool:
    try:
        r = int(rating)
        return 1 <= r <= 5
    except (TypeError, ValueError):
        return False

# --------------------------
# HOME PAGE
# --------------------------
@app.route("/")
def home():
    stats = {
        "total_events": 0,
        "upcoming": 0,
        "total_registrations": 0,
        "average_rating": None,
    }

    conn = get_db_connection()
    if conn is None:
        return render_template("index.html", stats=stats)

    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM event")
            stats["total_events"] = cursor.fetchone()["total"]

            cursor.execute(
                """
                SELECT COUNT(*) AS upcoming
                FROM event
                WHERE date IS NULL OR date >= CURDATE()
                """
            )
            stats["upcoming"] = cursor.fetchone()["upcoming"]

            cursor.execute("SELECT COUNT(*) AS total FROM registration")
            stats["total_registrations"] = cursor.fetchone()["total"]

            cursor.execute("SELECT ROUND(AVG(rating), 1) AS avg_rating FROM feedback")
            avg = cursor.fetchone()["avg_rating"]
            stats["average_rating"] = f"{avg}/5" if avg is not None else None

    except Error as err:
        app.logger.error("Failed to load home stats: %s", err)
    finally:
        conn.close()

    return render_template("index.html", stats=stats)

# --------------------------
# VIEW ALL EVENTS
# --------------------------
@app.route("/events")
def events():
    conn = get_db_connection()
    if conn is None:
        return render_template("error.html", message="Database connection failed"), 500

    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            cursor.execute(
                """
                SELECT 
                    event_id,
                    name,
                    description,
                    date,
                    time,
                    venue,
                    organizer,
                    max_seats,
                    IFNULL(
                        (SELECT COUNT(*) FROM registration r WHERE r.event_id = event.event_id),
                        0
                    ) AS registered_count
                FROM event
                ORDER BY date ASC, time ASC
                """
            )
            data = cursor.fetchall()

        total_capacity = sum(filter(None, (event.get("max_seats") for event in data)))
        total_registrations = sum(event.get("registered_count", 0) for event in data)
        for event in data:
            capacity = event.get("max_seats") or 0
            registered = event.get("registered_count", 0)
            event["capacity"] = capacity
            event["fill_percent"] = int((registered / capacity) * 100) if capacity else 0
            event["status"] = "Full" if capacity and registered >= capacity else "Open"

        stats = {
            "total_events": len(data),
            "upcoming": sum(1 for event in data if event.get("status") == "Open"),
            "total_registrations": total_registrations,
            "total_capacity": total_capacity,
            "avg_fill": int((total_registrations / total_capacity) * 100) if total_capacity else 0,
        }

        return render_template("events.html", events=data, stats=stats)
    except Error as err:
        app.logger.error("Failed to load events: %s", err)
        return render_template("error.html", message=f"Database error: {err}"), 500
    finally:
        conn.close()

# --------------------------
# REGISTER STUDENT TO EVENT
# --------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    event_options = get_event_options()
    conn = get_db_connection()
    if conn is None:
        return render_template("error.html", message="Database connection failed"), 500

    try:
        if request.method == "POST":
            reg_id_raw = request.form.get("reg_id", "").strip()
            event_id_raw = request.form.get("event_id", "").strip()
            usn_raw = request.form.get("usn", "").strip()

            if not is_valid_numeric(reg_id_raw):
                flash("Registration ID must be a number", "error")
                return render_template("register.html", events=event_options), 400

            if not is_valid_numeric(event_id_raw):
                flash("Please choose a valid event", "error")
                return render_template("register.html", events=event_options), 400

            if not is_valid_numeric(usn_raw):
                flash("USN must be numeric, matching the student table", "error")
                return render_template("register.html", events=event_options), 400

            reg_id = int(reg_id_raw)
            event_id = int(event_id_raw)
            usn = int(usn_raw)

            with closing(conn.cursor(dictionary=True)) as cursor:
                # Ensure student exists
                cursor.execute("SELECT name FROM student WHERE USN = %s", (usn,))
                student = cursor.fetchone()
                if not student:
                    flash("Student not found. Please verify the USN.", "error")
                    return render_template("register.html", events=event_options), 400

                # Ensure event exists and seats available
                cursor.execute("SELECT name, max_seats FROM event WHERE event_id = %s", (event_id,))
                event = cursor.fetchone()
                if not event:
                    flash("Selected event does not exist.", "error")
                    return render_template("register.html", events=event_options), 400

                cursor.execute("SELECT COUNT(*) AS cnt FROM registration WHERE event_id = %s", (event_id,))
                registered = cursor.fetchone()["cnt"]
                if event["max_seats"] is not None and registered >= event["max_seats"]:
                    flash("Event is already at capacity.", "error")
                    return render_template("register.html", events=event_options), 400

                # Duplicate checks
                cursor.execute("SELECT 1 FROM registration WHERE reg_id = %s", (reg_id,))
                if cursor.fetchone():
                    flash("Registration ID already exists.", "error")
                    return render_template("register.html", events=event_options), 400

                cursor.execute(
                    "SELECT 1 FROM registration WHERE event_id = %s AND USN = %s",
                    (event_id, usn),
                )
                if cursor.fetchone():
                    flash("Student already registered for this event.", "error")
                    return render_template("register.html", events=event_options), 400

                cursor.execute(
                    """
                    INSERT INTO registration (reg_id, event_id, USN)
                    VALUES (%s, %s, %s)
                    """,
                    (reg_id, event_id, usn),
                )
                conn.commit()

            return render_template(
                "success.html",
                message="Registration Successful!",
                link_text="View Events",
                link_url="/events",
            )

        return render_template("register.html", events=event_options)
    except Error as err:
        conn.rollback()
        app.logger.error("Registration failed: %s", err)
        return render_template("error.html", message=f"Database error: {err}"), 500
    finally:
        conn.close()

# --------------------------
# SUBMIT FEEDBACK
# --------------------------
@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    event_options = get_event_options()
    conn = get_db_connection()
    if conn is None:
        return render_template("error.html", message="Database connection failed"), 500

    try:
        if request.method == "POST":
            event_id_raw = request.form.get("event_id", "").strip()
            usn_raw = request.form.get("usn", "").strip()
            rating_raw = request.form.get("rating", "").strip()
            comment = request.form.get("comment", "").strip()

            if not is_valid_numeric(event_id_raw):
                flash("Please select a valid event.", "error")
                return render_template("feedback.html", events=event_options), 400

            if not is_valid_numeric(usn_raw):
                flash("USN must be numeric to match the student record.", "error")
                return render_template("feedback.html", events=event_options), 400

            if not is_valid_rating(rating_raw):
                flash("Rating must be between 1 and 5.", "error")
                return render_template("feedback.html", events=event_options), 400

            if len(comment) > 500:
                flash("Comment must be under 500 characters.", "error")
                return render_template("feedback.html", events=event_options), 400

            event_id = int(event_id_raw)
            usn = int(usn_raw)
            rating = int(rating_raw)

            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute("SELECT 1 FROM student WHERE USN = %s", (usn,))
                if cursor.fetchone() is None:
                    flash("Student not found. Please register the student first.", "error")
                    return render_template("feedback.html", events=event_options), 400

                cursor.execute("SELECT 1 FROM event WHERE event_id = %s", (event_id,))
                if cursor.fetchone() is None:
                    flash("Event not found.", "error")
                    return render_template("feedback.html", events=event_options), 400

                cursor.execute(
                    """
                    INSERT INTO feedback (event_id, USN, rating, comment)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (event_id, usn, rating, comment or None),
                )
                conn.commit()

            return render_template(
                "success.html",
                message="Feedback Submitted Successfully!",
                link_text="View Events",
                link_url="/events",
            )

        return render_template("feedback.html", events=event_options)
    except Error as err:
        conn.rollback()
        app.logger.error("Feedback submission failed: %s", err)
        return render_template("error.html", message=f"Database error: {err}"), 500
    finally:
        conn.close()

# --------------------------
# HELPER FUNCTIONS
# --------------------------
def get_event_options():
    """Fetch events for dropdowns."""
    conn = get_db_connection()
    if conn is None:
        return []

    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            cursor.execute(
                """
                SELECT 
                    event_id, 
                    name, 
                    date, 
                    time, 
                    venue, 
                    organizer, 
                    max_seats,
                    IFNULL((SELECT COUNT(*) FROM registration r WHERE r.event_id = event.event_id), 0) AS registered_count
                FROM event
                ORDER BY date ASC
                """
            )
            return cursor.fetchall()
    except Error as err:
        app.logger.error("Failed to fetch event options: %s", err)
        return []
    finally:
        conn.close()
   




# --------------------------
# RUN APP
# --------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5002)
    
 