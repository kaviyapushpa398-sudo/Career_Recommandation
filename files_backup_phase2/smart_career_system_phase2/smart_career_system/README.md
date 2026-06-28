# Smart Career Recommendation System — Phase 1
### User Registration, Login, Password Hashing, Sessions (Flask + MySQL)

## 📁 Project Folder Structure

```
smart_career_system/
│
├── app.py                     # Main Flask application (routes, API logic)
├── db.py                      # MySQL database connection handler
├── database.sql               # SQL script to create database + users table
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment variables (rename to .env)
│
├── templates/                  # HTML pages (Jinja2 templates)
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
│
└── static/
    ├── css/
    │   └── style.css           # Styling for all pages
    └── js/
        ├── validation.js       # Shared validation helper functions
        ├── login.js             # Login form logic
        ├── register.js          # Registration form logic
        └── dashboard.js         # Logout logic
```

---

## ✅ Prerequisites

- Python 3.9+ installed
- MySQL Server installed and running
- pip (Python package manager)

---

## 🔧 Step-by-Step Setup Instructions

### Step 1: Place the project files
Create a folder named `smart_career_system` and place all the provided files inside it, matching the folder structure above exactly.

### Step 2: Create a virtual environment (recommended)
```bash
cd smart_career_system
python3 -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set up the MySQL database
Open your MySQL client (MySQL Workbench, terminal, or phpMyAdmin) and run the script in `database.sql`:

```bash
mysql -u root -p < database.sql
```
This will:
- Create the `smart_career_system` database
- Create the `users` table with columns for full name, email, username, and hashed password

### Step 5: Configure environment variables
1. Copy `.env.example` and rename the copy to `.env`
2. Open `.env` and fill in your actual MySQL credentials:

```
SECRET_KEY=replace_this_with_a_long_random_secret_string
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=smart_career_system
DB_PORT=3306
```

> ⚠️ Never commit your real `.env` file to version control (e.g., GitHub).

### Step 6: Test the database connection (optional but recommended)
```bash
python db.py
```
You should see:
```
✅ Successfully connected to MySQL database.
```
If you see a connection error, double-check your `.env` credentials and that MySQL is running.

### Step 7: Run the Flask application
```bash
python app.py
```
You should see output like:
```
* Running on http://0.0.0.0:5000
```

### Step 8: Open the application in your browser
Navigate to:
```
http://localhost:5000
```
This will redirect you to the **Login page**. Click "Register here" to create a new account first.

---

## 🧪 Testing the Flow

1. Go to `/register` and create a new account (full name, email, username, password).
2. On success, you'll be redirected to `/login`.
3. Log in using your **username or email** + password.
4. On success, you'll land on `/dashboard`, which confirms your session is active.
5. Click **Log Out** to clear your session and return to the login page.

---

## 🔐 Security Notes (Phase 1)

- Passwords are hashed using Werkzeug's `generate_password_hash` (PBKDF2-based) — plain-text passwords are never stored.
- Sessions are managed via Flask's signed session cookies using `app.secret_key`.
- Server-side validation is enforced on every API endpoint in addition to client-side JavaScript validation, since client-side checks can be bypassed.
- SQL queries use parameterized statements (`%s` placeholders) to prevent SQL injection.

---

## ➡️ What's Next (Future Phases)

Phase 1 only covers authentication. Future phases will add:
- User profile and skills input
- Career recommendation logic/ML model
- Resume analysis
- Admin dashboard

---

## 🛠️ Troubleshooting

| Issue | Likely Cause | Fix |
|---|---|---|
| `Database connection failed` | MySQL not running or wrong credentials | Check `.env` and confirm MySQL service is active |
| `ModuleNotFoundError` | Dependencies not installed | Run `pip install -r requirements.txt` again inside your virtual environment |
| Page shows raw text instead of styled page | Static files not loading | Confirm folder structure matches exactly (`static/css`, `static/js`) |
| "Email or username already registered" | Duplicate entry | Use a different email/username, or check the `users` table |
