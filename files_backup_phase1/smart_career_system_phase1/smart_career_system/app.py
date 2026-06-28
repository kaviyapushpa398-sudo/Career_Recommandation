"""
app.py
-------
Main Flask backend for the Smart Career Recommendation System.
Phase 1: User Registration, Login, Password Hashing, Session Management.
"""

import os
import re
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from db import get_db_connection

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key_change_me")

# Session configuration
app.config["SESSION_TYPE"] = "filesystem"
app.config["PERMANENT_SESSION_LIFETIME"] = 1800  # 30 minutes


# =====================================================
# Helper Functions
# =====================================================

def is_valid_email(email):
    """Basic server-side email format validation."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def is_logged_in():
    return "user_id" in session


# =====================================================
# Routes: Pages
# =====================================================

@app.route("/")
def index():
    """Redirect root URL based on login status."""
    if is_logged_in():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login_page"))


@app.route("/register", methods=["GET"])
def register_page():
    """Render the registration page."""
    if is_logged_in():
        return redirect(url_for("dashboard"))
    return render_template("register.html")


@app.route("/login", methods=["GET"])
def login_page():
    """Render the login page."""
    if is_logged_in():
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    """A simple protected page to confirm login/session works."""
    if not is_logged_in():
        return redirect(url_for("login_page"))
    return render_template("dashboard.html", full_name=session.get("full_name"))


# =====================================================
# Routes: API (Registration / Login / Logout)
# =====================================================

@app.route("/api/register", methods=["POST"])
def api_register():
    """
    Handles new user registration.
    Expects JSON: { full_name, email, username, password, confirm_password }
    """
    data = request.get_json(silent=True) or {}

    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""

    # ----- Server-side validation -----
    if not full_name or not email or not username or not password:
        return jsonify({"success": False, "message": "All fields are required."}), 400

    if len(full_name) < 2:
        return jsonify({"success": False, "message": "Full name is too short."}), 400

    if not is_valid_email(email):
        return jsonify({"success": False, "message": "Invalid email address."}), 400

    if len(username) < 3:
        return jsonify({"success": False, "message": "Username must be at least 3 characters."}), 400

    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400

    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match."}), 400

    # ----- Hash the password -----
    password_hash = generate_password_hash(password)

    # ----- Insert into database -----
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()

        # Check if email or username already exists
        cursor.execute(
            "SELECT id FROM users WHERE email = %s OR username = %s",
            (email, username)
        )
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({"success": False, "message": "Email or username already registered."}), 409

        # Insert new user
        cursor.execute(
            """
            INSERT INTO users (full_name, email, username, password_hash)
            VALUES (%s, %s, %s, %s)
            """,
            (full_name, email, username, password_hash)
        )
        conn.commit()

        return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201

    except Exception as e:
        print(f"[REGISTER ERROR] {e}")
        return jsonify({"success": False, "message": "An error occurred during registration."}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/api/login", methods=["POST"])
def api_login():
    """
    Handles user login.
    Expects JSON: { login_identifier, password }
    login_identifier can be either email or username.
    """
    data = request.get_json(silent=True) or {}

    login_identifier = (data.get("login_identifier") or "").strip().lower()
    password = data.get("password") or ""

    if not login_identifier or not password:
        return jsonify({"success": False, "message": "Username/Email and password are required."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE email = %s OR username = %s",
            (login_identifier, login_identifier)
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({"success": False, "message": "Invalid credentials."}), 401

        if not check_password_hash(user["password_hash"], password):
            return jsonify({"success": False, "message": "Invalid credentials."}), 401

        # ----- Set session -----
        session.clear()
        session["user_id"] = user["id"]
        session["full_name"] = user["full_name"]
        session["username"] = user["username"]
        session.permanent = True

        return jsonify({
            "success": True,
            "message": "Login successful!",
            "redirect_url": url_for("dashboard")
        }), 200

    except Exception as e:
        print(f"[LOGIN ERROR] {e}")
        return jsonify({"success": False, "message": "An error occurred during login."}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/api/logout", methods=["POST"])
def api_logout():
    """Clears the session and logs the user out."""
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully.", "redirect_url": url_for("login_page")}), 200


# =====================================================
# Run the app
# =====================================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
