from contextlib import closing
from datetime import date
from collections import Counter
import csv
import io
import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    Response,
)
import mysql.connector
from mysql.connector import Error
from functools import wraps


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "database": os.getenv("DB_NAME", "event_portal"),
}

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as err:
        app.logger.error("DB connection failed: %s", err)
        return None


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please log in to continue", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)

    return wrapper


@app.route("/")
def root():
    if session.get("admin_logged_in"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            session["admin_username"] = username
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")


@app.route("/admin/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("login"))


@app.route("/admin/dashboard")
@login_required
def dashboard():
    stats = {
        "students": 0,
        "events": 0,
        "registrations": 0,
        "feedback": 0,
    }

    conn = get_db_connection()
    if conn is None:
        flash("Could not connect to the database", "danger")
        return render_template("dashboard.html", stats=stats)

    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT COUNT(*) FROM student")
            stats["students"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM event")
            stats["events"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM registration")
            stats["registrations"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM feedback")
            stats["feedback"] = cursor.fetchone()[0]
    finally:
        conn.close()

    return render_template("dashboard.html", stats=stats)


@app.route("/admin/dashboard/events")
@login_required
def events_dashboard():
    stats = {
        "total_events": 0,
        "total_capacity": 0,
        "seats_filled": 0,
        "avg_fill": 0,
        "upcoming": 0,
    }
    events = []
    highlights = []

    conn = get_db_connection()
    if conn is None:
        flash("Database unavailable", "danger")
        return render_template(
            "events_dashboard.html", stats=stats, events=events, highlights=highlights
        )

    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            cursor.execute(
                """
                SELECT e.event_id, e.name, e.description, e.date, e.time, e.venue,
                       e.organizer, e.max_seats,
                       COALESCE(e.registration_count,
                                (SELECT COUNT(*) FROM registration r WHERE r.event_id = e.event_id),
                                0) AS registered,
                       (SELECT ROUND(AVG(rating), 1) FROM feedback f WHERE f.event_id = e.event_id) AS avg_rating
                FROM event e
                ORDER BY e.date ASC
                """
            )
            events = cursor.fetchall()
    finally:
        conn.close()

    if events:
        stats["total_events"] = len(events)
        stats["total_capacity"] = sum((event.get("max_seats") or 0) for event in events)
        stats["seats_filled"] = sum((event.get("registered") or 0) for event in events)
        stats["avg_fill"] = (
            int((stats["seats_filled"] / stats["total_capacity"]) * 100)
            if stats["total_capacity"]
            else 0
        )
        stats["upcoming"] = sum(
            1
            for event in events
            if not event.get("date") or event["date"] >= date.today()
        )

        for event in events:
            max_seats = event.get("max_seats") or 0
            registered = event.get("registered") or 0
            event["fill_percent"] = int((registered / max_seats) * 100) if max_seats else 0
            event["status"] = "Full" if max_seats and registered >= max_seats else "Open"

        highlights = sorted(events, key=lambda e: e["fill_percent"], reverse=True)[:3]

    return render_template(
        "events_dashboard.html",
        stats=stats,
        events=events,
        highlights=highlights,
    )


@app.route("/admin/dashboard/registrations")
@login_required
def registrations_dashboard():
    query = request.args.get("q", "").strip()
    registrations = []
    stats = {
        "visible": 0,
        "unique_students": 0,
        "per_department": [],
        "latest_registration": None,
        "busiest_event": None,
    }

    conn = get_db_connection()
    if conn is None:
        flash("Database unavailable", "danger")
        return render_template(
            "registrations_dashboard.html",
            registrations=registrations,
            stats=stats,
            query=query,
        )

    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            sql = (
                """
                SELECT r.reg_id, r.registration_date, e.event_id, e.name AS event_name,
                       s.USN, s.name AS student_name, s.department
                FROM registration r
                JOIN event e ON e.event_id = r.event_id
                JOIN student s ON s.USN = r.USN
                """
            )
            params = []
            if query:
                sql += (
                    " WHERE e.name LIKE %s OR s.name LIKE %s OR s.USN LIKE %s OR s.department LIKE %s"
                )
                like = f"%{query}%"
                params = [like, like, like, like]
            sql += " ORDER BY r.registration_date DESC"
            cursor.execute(sql, params)
            registrations = cursor.fetchall()
    finally:
        conn.close()

    if registrations:
        stats["visible"] = len(registrations)
        stats["unique_students"] = len({row["USN"] for row in registrations})
        stats["latest_registration"] = registrations[0]
        counts = Counter(row["event_name"] for row in registrations)
        stats["busiest_event"] = counts.most_common(1)[0] if counts else None

        dept_counter = Counter((row["department"] or "Unknown") for row in registrations)
        stats["per_department"] = dept_counter.most_common()

    return render_template(
        "registrations_dashboard.html",
        registrations=registrations,
        stats=stats,
        query=query,
    )


@app.route("/admin/dashboard/feedback")
@login_required
def feedback_dashboard():
    rating_filter = request.args.get("rating", "").strip()
    feedback_rows = []
    stats = {
        "total": 0,
        "avg_rating": None,
        "positive_pct": 0,
        "trending_event": None,
    }
    rating_distribution = {rating: 0 for rating in range(1, 6)}

    conn = get_db_connection()
    if conn is None:
        flash("Database unavailable", "danger")
        return render_template(
            "feedback_dashboard.html",
            feedback=feedback_rows,
            stats=stats,
            rating_filter=rating_filter,
            rating_distribution=rating_distribution,
        )

    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            sql = (
                """
                SELECT f.feedback_id, f.rating, f.comment, f.submitted_at,
                       e.event_id, e.name AS event_name,
                       s.USN, s.name AS student_name
                FROM feedback f
                JOIN event e ON e.event_id = f.event_id
                JOIN student s ON s.USN = f.USN
                """
            )
            clauses = []
            params = []
            if rating_filter == "good":
                clauses.append("f.rating >= 4")
            elif rating_filter == "average":
                clauses.append("f.rating = 3")
            elif rating_filter == "poor":
                clauses.append("f.rating <= 2")
            if clauses:
                sql += " WHERE " + " AND ".join(clauses)
            sql += " ORDER BY f.submitted_at DESC"
            cursor.execute(sql, params)
            feedback_rows = cursor.fetchall()
    finally:
        conn.close()

    if feedback_rows:
        stats["total"] = len(feedback_rows)
        total_rating = sum(row["rating"] for row in feedback_rows)
        stats["avg_rating"] = round(total_rating / stats["total"], 1)
        positive = sum(1 for row in feedback_rows if row["rating"] >= 4)
        stats["positive_pct"] = int((positive / stats["total"]) * 100)
        counts = Counter(row["event_name"] for row in feedback_rows)
        stats["trending_event"] = counts.most_common(1)[0] if counts else None

        for row in feedback_rows:
            rating_distribution[row["rating"]] += 1

    return render_template(
        "feedback_dashboard.html",
        feedback=feedback_rows,
        stats=stats,
        rating_filter=rating_filter,
        rating_distribution=rating_distribution,
    )


@app.route("/admin/students")
@login_required
def students():
    query = request.args.get("q", "").strip()
    conn = get_db_connection()
    results = []
    if conn is None:
        flash("Database unavailable", "danger")
        return render_template("students.html", students=results, query=query)

    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            if query:
                like = f"%{query}%"
                cursor.execute(
                    """
                    SELECT USN, name, department, email, phone
                    FROM student
                    WHERE USN LIKE %s OR name LIKE %s
                    ORDER BY name ASC
                    """,
                    (like, like),
                )
            else:
                cursor.execute(
                    "SELECT USN, name, department, email, phone FROM student ORDER BY name ASC"
                )
            results = cursor.fetchall()
    finally:
        conn.close()

    return render_template("students.html", students=results, query=query)


@app.route("/admin/events")
@login_required
def events():
    conn = get_db_connection()
    rows = []
    if conn is None:
        flash("Database unavailable", "danger")
        return render_template("events.html", events=rows)

    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            cursor.execute(
                """
                SELECT event_id, name, date, time, venue, organizer,
                       max_seats, IFNULL(registration_count, 0) AS registration_count
                FROM event
                ORDER BY date ASC
                """
            )
            rows = cursor.fetchall()
    finally:
        conn.close()

    return render_template("events.html", events=rows)


@app.route("/admin/events/delete/<int:event_id>", methods=["POST"])
@login_required
def delete_event(event_id: int):
    conn = get_db_connection()
    if conn is None:
        flash("Database unavailable", "danger")
        return redirect(url_for("events"))

    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute("DELETE FROM event WHERE event_id = %s", (event_id,))
            conn.commit()
            flash("Event deleted", "success")
    except Error as err:
        conn.rollback()
        flash(f"Failed to delete event: {err}", "danger")
    finally:
        conn.close()
    return redirect(url_for("events"))


@app.route("/admin/event/<int:event_id>/registrations")
@login_required
def event_registrations(event_id: int):
    conn = get_db_connection()
    registrations = []
    event = None
    if conn is None:
        flash("Database unavailable", "danger")
        return render_template("registrations.html", registrations=registrations, event=event)

    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            cursor.execute("SELECT event_id, name FROM event WHERE event_id = %s", (event_id,))
            event = cursor.fetchone()
            if event:
                cursor.execute(
                    """
                    SELECT r.reg_id, r.registration_date, s.USN, s.name AS student_name, s.department
                    FROM registration r
                    JOIN student s ON s.USN = r.USN
                    WHERE r.event_id = %s
                    ORDER BY r.registration_date DESC
                    """,
                    (event_id,),
                )
                registrations = cursor.fetchall()
    finally:
        conn.close()

    if not event:
        flash("Event not found", "warning")
        return redirect(url_for("events"))

    return render_template("registrations.html", registrations=registrations, event=event)


@app.route("/admin/event/<int:event_id>/feedback")
@login_required
def event_feedback(event_id: int):
    conn = get_db_connection()
    feedback_rows = []
    event = None
    if conn is None:
        flash("Database unavailable", "danger")
        return render_template("feedback.html", feedback=feedback_rows, event=event)

    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            cursor.execute("SELECT event_id, name FROM event WHERE event_id = %s", (event_id,))
            event = cursor.fetchone()
            if event:
                cursor.execute(
                    """
                    SELECT f.feedback_id, f.rating, f.comment, f.submitted_at,
                           s.USN, s.name AS student_name
                    FROM feedback f
                    JOIN student s ON s.USN = f.USN
                    WHERE f.event_id = %s
                    ORDER BY f.submitted_at DESC
                    """,
                    (event_id,),
                )
                feedback_rows = cursor.fetchall()
    finally:
        conn.close()

    if not event:
        flash("Event not found", "warning")
        return redirect(url_for("events"))

    return render_template("feedback.html", feedback=feedback_rows, event=event)


@app.route("/admin/export/registrations")
@login_required
def export_registrations():
    conn = get_db_connection()
    if conn is None:
        flash("Database unavailable", "danger")
        return redirect(url_for("dashboard"))

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Registration ID", "Event", "USN", "Student", "Department", "Registered At"])

    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            cursor.execute(
                """
                SELECT r.reg_id, e.name AS event_name, s.USN, s.name AS student_name,
                       s.department, r.registration_date
                FROM registration r
                JOIN event e ON e.event_id = r.event_id
                JOIN student s ON s.USN = r.USN
                ORDER BY r.registration_date DESC
                """
            )
            for row in cursor.fetchall():
                writer.writerow(
                    [
                        row["reg_id"],
                        row["event_name"],
                        row["USN"],
                        row["student_name"],
                        row["department"],
                        row["registration_date"],
                    ]
                )
    finally:
        conn.close()

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=registrations.csv"},
    )


@app.route("/admin/export/feedback")
@login_required
def export_feedback():
    conn = get_db_connection()
    if conn is None:
        flash("Database unavailable", "danger")
        return redirect(url_for("dashboard"))

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Feedback ID", "Event", "USN", "Student", "Rating", "Comment", "Submitted At"])

    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            cursor.execute(
                """
                SELECT f.feedback_id, e.name AS event_name, s.USN, s.name AS student_name,
                       f.rating, f.comment, f.submitted_at
                FROM feedback f
                JOIN event e ON e.event_id = f.event_id
                JOIN student s ON s.USN = f.USN
                ORDER BY f.submitted_at DESC
                """
            )
            for row in cursor.fetchall():
                writer.writerow(
                    [
                        row["feedback_id"],
                        row["event_name"],
                        row["USN"],
                        row["student_name"],
                        row["rating"],
                        row.get("comment", ""),
                        row["submitted_at"],
                    ]
                )
    finally:
        conn.close()

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=feedback.csv"},
    )


if __name__ == "__main__":
    app.run(debug=True, port=5004)
