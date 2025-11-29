# Event Registration & Feedback – Admin Portal

A lightweight Flask + MySQL admin console for managing events, students, registrations, and feedback within the Event Registration & Feedback System.

## 📁 Project Structure

```
admin_portal/
├── app.py                 # Flask application with admin routes
├── db.sql                 # MySQL schema + trigger + seed data
├── README.md              # Setup instructions (this file)
├── static/
│   └── css/
│       └── admin.css      # Optional Bootstrap overrides
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
   ├── events_dashboard.html
   ├── registrations_dashboard.html
   ├── feedback_dashboard.html
    ├── students.html
    ├── events.html
    ├── registrations.html
    └── feedback.html
```

## 🛠️ Tech Stack
- **Backend:** Python 3 + Flask
- **Database:** MySQL (via `mysql-connector-python`)
- **Frontend:** HTML, Jinja2 templates, Bootstrap 5, custom CSS

## 🚀 Getting Started
1. **Create & activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS / Linux
   .venv\Scripts\activate     # Windows
   ```
2. **Install dependencies:**
   ```bash
   pip install flask mysql-connector-python python-dotenv
   ```
3. **Configure your environment:**
   - Copy `.env.example` (if you create one) or set these variables however you prefer:
     - `ADMIN_USERNAME` (default: `admin`)
     - `ADMIN_PASSWORD` (default: `admin123`)
     - `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
     - `FLASK_SECRET_KEY`
4. **Provision the database:**
   - Create a MySQL schema (example name: `event_portal_admin`).
   - Run `db.sql` in your MySQL client to create tables, trigger, and sample data.
5. **Run the server:**
   ```bash
   python app.py
   ```
6. **Visit the admin UI:**
   - Open [http://localhost:5000](http://localhost:5000) and log in with your admin credentials.

## ✨ Features
- Session-based admin authentication (username/password)
- Dashboard metrics (students, events, registrations, feedback)
- Dedicated analytics dashboards for events, registrations, and feedback trends
- Student directory with search by name or USN
- Event management page with seat utilization + delete action
- Per-event registrations & feedback views
- Export registrations/feedback to CSV

## 🔐 Authentication Notes
- Credentials are intentionally simple for classroom/demo use.
- For production, store hashes in the database or integrate with your institution's SSO.

## 🧪 Testing the Database Trigger
The schema maintains `event.registration_count` via an `AFTER INSERT` trigger on the `registration` table. Insert a new registration row and observe the count increment automatically.

## 📄 License
This sample is provided for educational use within DBMS coursework. Modify freely for your institution's needs.
