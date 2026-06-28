"""
app.py
-------
Main Flask backend for the Smart Career Recommendation System.
Phase 1: User Registration, Login, Password Hashing, Session Management.
Phase 2: Student Profile, Skills, Interests, Certifications, Projects.
"""

import os
import re
import functools
from datetime import datetime
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


def login_required(view_func):
    """
    Decorator for routes that require an active session.
    Redirects to login page (for page routes) or returns 401 JSON (for API routes).
    """
    @functools.wraps(view_func)
    def wrapped(*args, **kwargs):
        if not is_logged_in():
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "message": "You must be logged in."}), 401
            return redirect(url_for("login_page"))
        return view_func(*args, **kwargs)
    return wrapped


def parse_date(value):
    """
    Safely parses a 'YYYY-MM-DD' string into a date object.
    Returns None if value is empty or invalid.
    """
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def parse_year(value):
    """Safely parses a 4-digit year string into an int, or None."""
    if not value:
        return None
    try:
        year = int(value)
        if 1900 <= year <= 2100:
            return year
        return None
    except (ValueError, TypeError):
        return None


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
@login_required
def dashboard():
    """A simple protected page to confirm login/session works."""
    return render_template("dashboard.html", full_name=session.get("full_name"))


@app.route("/profile")
@login_required
def profile_page():
    """Renders the student profile management page (Phase 2)."""
    return render_template("profile.html", full_name=session.get("full_name"))


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
# Routes: API (Student Profile) - Phase 2
# =====================================================

@app.route("/api/profile", methods=["GET"])
@login_required
def api_get_profile():
    """Fetches the logged-in user's profile + basic account info."""
    user_id = session["user_id"]
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT full_name, email, username FROM users WHERE id = %s",
            (user_id,)
        )
        account = cursor.fetchone()

        cursor.execute(
            """
            SELECT phone, date_of_birth, gender, education_level,
                   institution_name, field_of_study, graduation_year,
                   bio, linkedin_url, github_url
            FROM student_profile WHERE user_id = %s
            """,
            (user_id,)
        )
        profile = cursor.fetchone()

        # Convert date/year fields to strings for JSON serialization
        if profile:
            if profile.get("date_of_birth"):
                profile["date_of_birth"] = profile["date_of_birth"].isoformat()
            if profile.get("graduation_year"):
                profile["graduation_year"] = int(profile["graduation_year"])

        return jsonify({
            "success": True,
            "account": account,
            "profile": profile  # None if not yet created
        }), 200

    except Exception as e:
        print(f"[GET PROFILE ERROR] {e}")
        return jsonify({"success": False, "message": "Could not fetch profile."}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/api/profile", methods=["POST"])
@login_required
def api_save_profile():
    """
    Creates or updates the logged-in user's student profile.
    Performs an UPSERT (INSERT ... ON DUPLICATE KEY UPDATE).
    """
    user_id = session["user_id"]
    data = request.get_json(silent=True) or {}

    phone = (data.get("phone") or "").strip() or None
    date_of_birth = parse_date(data.get("date_of_birth"))
    gender = (data.get("gender") or "").strip() or None
    education_level = (data.get("education_level") or "").strip() or None
    institution_name = (data.get("institution_name") or "").strip() or None
    field_of_study = (data.get("field_of_study") or "").strip() or None
    graduation_year = parse_year(data.get("graduation_year"))
    bio = (data.get("bio") or "").strip() or None
    linkedin_url = (data.get("linkedin_url") or "").strip() or None
    github_url = (data.get("github_url") or "").strip() or None

    valid_genders = {"Male", "Female", "Other", "Prefer not to say", None}
    valid_education = {
        "High School", "Diploma", "Undergraduate",
        "Postgraduate", "PhD", "Other", None
    }

    if gender not in valid_genders:
        return jsonify({"success": False, "message": "Invalid gender value."}), 400

    if education_level not in valid_education:
        return jsonify({"success": False, "message": "Invalid education level."}), 400

    if data.get("date_of_birth") and date_of_birth is None:
        return jsonify({"success": False, "message": "Invalid date of birth format. Use YYYY-MM-DD."}), 400

    if data.get("graduation_year") and graduation_year is None:
        return jsonify({"success": False, "message": "Invalid graduation year."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO student_profile (
                user_id, phone, date_of_birth, gender, education_level,
                institution_name, field_of_study, graduation_year,
                bio, linkedin_url, github_url
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                phone = VALUES(phone),
                date_of_birth = VALUES(date_of_birth),
                gender = VALUES(gender),
                education_level = VALUES(education_level),
                institution_name = VALUES(institution_name),
                field_of_study = VALUES(field_of_study),
                graduation_year = VALUES(graduation_year),
                bio = VALUES(bio),
                linkedin_url = VALUES(linkedin_url),
                github_url = VALUES(github_url)
            """,
            (
                user_id, phone, date_of_birth, gender, education_level,
                institution_name, field_of_study, graduation_year,
                bio, linkedin_url, github_url
            )
        )
        conn.commit()

        return jsonify({"success": True, "message": "Profile saved successfully."}), 200

    except Exception as e:
        print(f"[SAVE PROFILE ERROR] {e}")
        return jsonify({"success": False, "message": "Could not save profile."}), 500

    finally:
        cursor.close()
        conn.close()


# =====================================================
# Routes: API (Skills) - Phase 2
# =====================================================

@app.route("/api/skills", methods=["GET"])
@login_required
def api_get_skills():
    """Fetches all skills belonging to the logged-in user."""
    user_id = session["user_id"]
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, skill_name, proficiency FROM skills WHERE user_id = %s ORDER BY skill_name ASC",
            (user_id,)
        )
        skills = cursor.fetchall()
        return jsonify({"success": True, "skills": skills}), 200

    except Exception as e:
        print(f"[GET SKILLS ERROR] {e}")
        return jsonify({"success": False, "message": "Could not fetch skills."}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/api/skills", methods=["POST"])
@login_required
def api_add_skill():
    """Adds a new skill for the logged-in user."""
    user_id = session["user_id"]
    data = request.get_json(silent=True) or {}

    skill_name = (data.get("skill_name") or "").strip()
    proficiency = (data.get("proficiency") or "Beginner").strip()

    valid_proficiencies = {"Beginner", "Intermediate", "Advanced", "Expert"}

    if not skill_name:
        return jsonify({"success": False, "message": "Skill name is required."}), 400

    if len(skill_name) > 100:
        return jsonify({"success": False, "message": "Skill name is too long."}), 400

    if proficiency not in valid_proficiencies:
        return jsonify({"success": False, "message": "Invalid proficiency level."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM skills WHERE user_id = %s AND skill_name = %s",
            (user_id, skill_name)
        )
        if cursor.fetchone():
            return jsonify({"success": False, "message": "This skill is already in your list."}), 409

        cursor.execute(
            "INSERT INTO skills (user_id, skill_name, proficiency) VALUES (%s, %s, %s)",
            (user_id, skill_name, proficiency)
        )
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Skill added successfully.",
            "skill": {"id": cursor.lastrowid, "skill_name": skill_name, "proficiency": proficiency}
        }), 201

    except Exception as e:
        print(f"[ADD SKILL ERROR] {e}")
        return jsonify({"success": False, "message": "Could not add skill."}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/api/skills/<int:skill_id>", methods=["PUT"])
@login_required
def api_update_skill(skill_id):
    """Updates an existing skill's proficiency (only if it belongs to the user)."""
    user_id = session["user_id"]
    data = request.get_json(silent=True) or {}

    proficiency = (data.get("proficiency") or "").strip()
    valid_proficiencies = {"Beginner", "Intermediate", "Advanced", "Expert"}

    if proficiency not in valid_proficiencies:
        return jsonify({"success": False, "message": "Invalid proficiency level."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE skills SET proficiency = %s WHERE id = %s AND user_id = %s",
            (proficiency, skill_id, user_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Skill not found."}), 404

        return jsonify({"success": True, "message": "Skill updated successfully."}), 200

    except Exception as e:
        print(f"[UPDATE SKILL ERROR] {e}")
        return jsonify({"success": False, "message": "Could not update skill."}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/api/skills/<int:skill_id>", methods=["DELETE"])
@login_required
def api_delete_skill(skill_id):
    """Deletes a skill belonging to the logged-in user."""
    user_id = session["user_id"]
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM skills WHERE id = %s AND user_id = %s",
            (skill_id, user_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Skill not found."}), 404

        return jsonify({"success": True, "message": "Skill deleted successfully."}), 200

    except Exception as e:
        print(f"[DELETE SKILL ERROR] {e}")
        return jsonify({"success": False, "message": "Could not delete skill."}), 500

    finally:
        cursor.close()
        conn.close()


# =====================================================
# Routes: API (Interests) - Phase 2
# =====================================================

@app.route("/api/interests", methods=["GET"])
@login_required
def api_get_interests():
    """Fetches all interests belonging to the logged-in user."""
    user_id = session["user_id"]
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, interest_name FROM interests WHERE user_id = %s ORDER BY interest_name ASC",
            (user_id,)
        )
        interests = cursor.fetchall()
        return jsonify({"success": True, "interests": interests}), 200

    except Exception as e:
        print(f"[GET INTERESTS ERROR] {e}")
        return jsonify({"success": False, "message": "Could not fetch interests."}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/api/interests", methods=["POST"])
@login_required
def api_add_interest():
    """Adds a new interest for the logged-in user."""
    user_id = session["user_id"]
    data = request.get_json(silent=True) or {}

    interest_name = (data.get("interest_name") or "").strip()

    if not interest_name:
        return jsonify({"success": False, "message": "Interest name is required."}), 400

    if len(interest_name) > 100:
        return jsonify({"success": False, "message": "Interest name is too long."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM interests WHERE user_id = %s AND interest_name = %s",
            (user_id, interest_name)
        )
        if cursor.fetchone():
            return jsonify({"success": False, "message": "This interest is already in your list."}), 409

        cursor.execute(
            "INSERT INTO interests (user_id, interest_name) VALUES (%s, %s)",
            (user_id, interest_name)
        )
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Interest added successfully.",
            "interest": {"id": cursor.lastrowid, "interest_name": interest_name}
        }), 201

    except Exception as e:
        print(f"[ADD INTEREST ERROR] {e}")
        return jsonify({"success": False, "message": "Could not add interest."}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/api/interests/<int:interest_id>", methods=["DELETE"])
@login_required
def api_delete_interest(interest_id):
    """Deletes an interest belonging to the logged-in user."""
    user_id = session["user_id"]
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM interests WHERE id = %s AND user_id = %s",
            (interest_id, user_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Interest not found."}), 404

        return jsonify({"success": True, "message": "Interest deleted successfully."}), 200

    except Exception as e:
        print(f"[DELETE INTEREST ERROR] {e}")
        return jsonify({"success": False, "message": "Could not delete interest."}), 500

    finally:
        cursor.close()
        conn.close()


# =====================================================
# Routes: API (Certifications) - Phase 2
# =====================================================

@app.route("/api/certifications", methods=["GET"])
@login_required
def api_get_certifications():
    """Fetches all certifications belonging to the logged-in user."""
    user_id = session["user_id"]
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, certification_name, issuing_organization,
                   issue_date, expiry_date, credential_url
            FROM certifications
            WHERE user_id = %s
            ORDER BY issue_date DESC, certification_name ASC
            """,
            (user_id,)
        )
        certifications = cursor.fetchall()

        for cert in certifications:
            if cert.get("issue_date"):
                cert["issue_date"] = cert["issue_date"].isoformat()
            if cert.get("expiry_date"):
                cert["expiry_date"] = cert["expiry_date"].isoformat()

        return jsonify({"success": True, "certifications": certifications}), 200

    except Exception as e:
        print(f"[GET CERTIFICATIONS ERROR] {e}")
        return jsonify({"success": False, "message": "Could not fetch certifications."}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/api/certifications", methods=["POST"])
@login_required
def api_add_certification():
    """Adds a new certification for the logged-in user."""
    user_id = session["user_id"]
    data = request.get_json(silent=True) or {}

    certification_name = (data.get("certification_name") or "").strip()
    issuing_organization = (data.get("issuing_organization") or "").strip() or None
    issue_date = parse_date(data.get("issue_date"))
    expiry_date = parse_date(data.get("expiry_date"))
    credential_url = (data.get("credential_url") or "").strip() or None

    if not certification_name:
        return jsonify({"success": False, "message": "Certification name is required."}), 400

    if len(certification_name) > 150:
        return jsonify({"success": False, "message": "Certification name is too long."}), 400

    if data.get("issue_date") and issue_date is None:
        return jsonify({"success": False, "message": "Invalid issue date format. Use YYYY-MM-DD."}), 400

    if data.get("expiry_date") and expiry_date is None:
        return jsonify({"success": False, "message": "Invalid expiry date format. Use YYYY-MM-DD."}), 400

    if issue_date and expiry_date and expiry_date < issue_date:
        return jsonify({"success": False, "message": "Expiry date cannot be before issue date."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO certifications (
                user_id, certification_name, issuing_organization,
                issue_date, expiry_date, credential_url
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user_id, certification_name, issuing_organization, issue_date, expiry_date, credential_url)
        )
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Certification added successfully.",
            "certification_id": cursor.lastrowid
        }), 201

    except Exception as e:
        print(f"[ADD CERTIFICATION ERROR] {e}")
        return jsonify({"success": False, "message": "Could not add certification."}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/api/certifications/<int:certification_id>", methods=["DELETE"])
@login_required
def api_delete_certification(certification_id):
    """Deletes a certification belonging to the logged-in user."""
    user_id = session["user_id"]
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM certifications WHERE id = %s AND user_id = %s",
            (certification_id, user_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Certification not found."}), 404

        return jsonify({"success": True, "message": "Certification deleted successfully."}), 200

    except Exception as e:
        print(f"[DELETE CERTIFICATION ERROR] {e}")
        return jsonify({"success": False, "message": "Could not delete certification."}), 500

    finally:
        cursor.close()
        conn.close()


# =====================================================
# Routes: API (Projects) - Phase 2
# =====================================================

@app.route("/api/projects", methods=["GET"])
@login_required
def api_get_projects():
    """Fetches all projects belonging to the logged-in user."""
    user_id = session["user_id"]
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, project_title, description, technologies_used,
                   project_url, start_date, end_date, is_ongoing
            FROM projects
            WHERE user_id = %s
            ORDER BY start_date DESC, project_title ASC
            """,
            (user_id,)
        )
        projects = cursor.fetchall()

        for proj in projects:
            if proj.get("start_date"):
                proj["start_date"] = proj["start_date"].isoformat()
            if proj.get("end_date"):
                proj["end_date"] = proj["end_date"].isoformat()
            proj["is_ongoing"] = bool(proj["is_ongoing"])

        return jsonify({"success": True, "projects": projects}), 200

    except Exception as e:
        print(f"[GET PROJECTS ERROR] {e}")
        return jsonify({"success": False, "message": "Could not fetch projects."}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/api/projects", methods=["POST"])
@login_required
def api_add_project():
    """Adds a new project for the logged-in user."""
    user_id = session["user_id"]
    data = request.get_json(silent=True) or {}

    project_title = (data.get("project_title") or "").strip()
    description = (data.get("description") or "").strip() or None
    technologies_used = (data.get("technologies_used") or "").strip() or None
    project_url = (data.get("project_url") or "").strip() or None
    start_date = parse_date(data.get("start_date"))
    end_date = parse_date(data.get("end_date"))
    is_ongoing = bool(data.get("is_ongoing"))

    if not project_title:
        return jsonify({"success": False, "message": "Project title is required."}), 400

    if len(project_title) > 150:
        return jsonify({"success": False, "message": "Project title is too long."}), 400

    if data.get("start_date") and start_date is None:
        return jsonify({"success": False, "message": "Invalid start date format. Use YYYY-MM-DD."}), 400

    if data.get("end_date") and end_date is None:
        return jsonify({"success": False, "message": "Invalid end date format. Use YYYY-MM-DD."}), 400

    if is_ongoing:
        end_date = None  # Ongoing projects have no end date

    if start_date and end_date and end_date < start_date:
        return jsonify({"success": False, "message": "End date cannot be before start date."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO projects (
                user_id, project_title, description, technologies_used,
                project_url, start_date, end_date, is_ongoing
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id, project_title, description, technologies_used,
                project_url, start_date, end_date, is_ongoing
            )
        )
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Project added successfully.",
            "project_id": cursor.lastrowid
        }), 201

    except Exception as e:
        print(f"[ADD PROJECT ERROR] {e}")
        return jsonify({"success": False, "message": "Could not add project."}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/api/projects/<int:project_id>", methods=["DELETE"])
@login_required
def api_delete_project(project_id):
    """Deletes a project belonging to the logged-in user."""
    user_id = session["user_id"]
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Database connection failed."}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM projects WHERE id = %s AND user_id = %s",
            (project_id, user_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Project not found."}), 404

        return jsonify({"success": True, "message": "Project deleted successfully."}), 200

    except Exception as e:
        print(f"[DELETE PROJECT ERROR] {e}")
        return jsonify({"success": False, "message": "Could not delete project."}), 500

    finally:
        cursor.close()
        conn.close()


# =====================================================
# Run the app
# =====================================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
