# Event Portal - Quick Start Guide

## Prerequisites
- Python 3.7+
- MySQL Server running locally
- pip (Python package manager)

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirments.txt
```

### 2. Database Setup
Make sure your MySQL database is configured with:
- Host: localhost
- User: root
- Password: dbms@2007
- Database: event_portal

If you need to create the database, run:
```bash
mysql -u root -p < db.sql
```

### 3. Run the Application
```bash
python app.py
```

The application will start at: `http://localhost:5000`

---

## Features

### 🏠 Home Page
- Welcome screen with feature overview
- Quick navigation to all main sections

### 📋 View Events
- Browse all upcoming events
- See event details: name, date, venue, capacity
- Link to register for events

### ✍️ Register for Event
- Select from available events
- Enter registration ID and USN
- Input validation for data integrity
- Duplicate registration prevention

### ⭐ Submit Feedback
- Rate events (1-5 stars)
- Leave comments with character counter
- Visual star rating display
- Easy form submission

---

## Improvements Made

### Backend
✅ Database error handling
✅ Input validation & sanitization
✅ SQL injection prevention
✅ Duplicate registration checks
✅ Transaction management
✅ Proper error responses

### Frontend
✅ Modern, responsive UI design
✅ Professional styling with CSS
✅ Navigation bar on all pages
✅ Mobile-friendly layout
✅ Form validation & helper text
✅ Success/Error pages
✅ Client-side validation
✅ Better user experience

### Security
✅ Parameterized SQL queries
✅ CSRF protection
✅ Input type validation
✅ Regular expression validation
✅ Safe error messages

---

## File Structure

```
Event_portal/
├── app.py                    # Main Flask application
├── requirments.txt           # Python dependencies
├── db.sql                    # Database schema
├── IMPROVEMENTS.md           # Detailed improvements list
├── README.md                 # This file
├── static/
│   └── styles.css           # Modern CSS styling
└── templates/
    ├── base.html            # Base template
    ├── index.html           # Home page
    ├── events.html          # Events listing
    ├── register.html        # Registration form
    ├── feedback.html        # Feedback form
    ├── success.html         # Success page
    └── error.html           # Error page
```

---

## Validation Rules

### USN (University Seat Number)
- Format: 10 alphanumeric characters
- Example: 1SI21CS101
- Case insensitive (auto-converted to uppercase)

### Registration ID
- Format: Numbers only
- Example: 12345

### Rating
- Range: 1 to 5
- Visual star display for feedback

### Comment
- Max 500 characters
- Optional field
- Character counter included

---

## Troubleshooting

### "Database connection failed"
- Check if MySQL server is running
- Verify database credentials in app.py
- Ensure database name is correct

### Port 5000 already in use
- Change port in app.py: `app.run(debug=True, port=5001)`

### Module not found errors
- Make sure you've installed requirements: `pip install -r requirments.txt`
- Check Python version compatibility

### Forms not accepting data
- Check browser console for JavaScript errors
- Verify form data format matches validation rules

---

## Development Notes

- Debug mode is enabled in development (`debug=True`)
- For production, set `debug=False`
- Database password is hardcoded (use environment variables in production)
- CSRF token is implemented with Flask's `secret_key`

---

## Support & Maintenance

For issues or improvements:
1. Check the IMPROVEMENTS.md file for all changes
2. Review the validation rules above
3. Check the database schema in db.sql
4. Test with valid input formats

---

**Version**: 2.0 Enhanced
**Last Updated**: November 25, 2024
