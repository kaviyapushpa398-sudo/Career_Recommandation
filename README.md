# Career_Recommandation

🎓 Smart Career Recommendation System

An AI inspired full stack web application that analyzes a student's profile, GitHub activity, skills, interests, certifications, and projects to recommend suitable career paths with personalized learning roadmaps.

---

🚀 Features

🔐 Authentication

- User Registration
- Secure Login
- Password Hashing
- Session Management

👤 Student Profile

- Personal Information
- Skills Management
- Interests Management
- Certifications
- Academic & Personal Projects

💻 GitHub Analysis

- GitHub API Integration
- Repository Analysis
- Programming Language Detection
- Developer Activity Score
- Overall Developer Score

🎯 Career Recommendation Engine

- Career Match Percentage
- Career Score Calculation
- Ranked Career Recommendations
- Skill Gap Analysis
- Learning Roadmap
- Certification Suggestions
- Course Recommendations

📊 Dashboard

- Student Overview
- GitHub Statistics
- Career Recommendations
- Progress Tracking

---

🛠️ Tech Stack

Frontend

- HTML5
- CSS3
- JavaScript

Backend

- Python
- Flask

Database

- MySQL

APIs

- GitHub REST API

Libraries

- Flask
- Flask-Login
- mysql-connector-python
- Werkzeug
- Requests
- python-dotenv

---

📂 Project Structure

smart_career_system/
│
├── static/
│   ├── css/
│   └── js/
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── github.html
│   └── careers.html
│
├── app.py
├── db.py
├── github_analyzer.py
├── career_engine.py
├── database.sql
├── database_phase2.sql
├── database_phase3.sql
├── database_phase4.sql
├── requirements.txt
├── .env.example
└── README.md

---

⚙️ Installation

1. Clone the Repository

git clone https://github.com/your-username/smart-career-recommendation-system.git

cd smart-career-recommendation-system

---

2. Create a Virtual Environment

Windows

python -m venv venv
venv\Scripts\activate

Linux / macOS

python3 -m venv venv
source venv/bin/activate

---

3. Install Dependencies

pip install -r requirements.txt

---

4. Configure Environment Variables

Create a ".env" file.

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=smart_career_system
DB_PORT=3306
SECRET_KEY=your_secret_key
GITHUB_TOKEN=your_github_token

---

5. Create Database

Open MySQL and execute:

database.sql
database_phase2.sql
database_phase3.sql
database_phase4.sql

---

6. Run the Application

python app.py

Open:

http://127.0.0.1:5000

---

📸 Screens

- Login Page
- Registration Page
- Dashboard
- Student Profile
- GitHub Analysis
- Career Recommendation Dashboard

---

🎯 Career Recommendations

The system recommends careers such as:

- Software Developer
- Full Stack Developer
- Frontend Developer
- Backend Developer
- AI Engineer
- Data Analyst
- Cloud Engineer
- Cybersecurity Analyst

Each recommendation includes:

- Match Percentage
- Career Score
- Rank
- Matching Skills
- Missing Skills
- Learning Roadmap
- Certification Suggestions
- Course Recommendations

---

📊 Database

The project stores data in MySQL using the following tables:

- users
- student_profile
- skills
- interests
- certifications
- projects
- github_analysis
- github_languages
- career_recommendations
- skill_gaps

---

🔒 Security Features

- Password Hashing
- Protected Routes
- Session-Based Authentication
- Input Validation
- SQL Parameterized Queries

---

📈 Future Enhancements

- AI Powered Resume Analyzer
- Resume Builder
- Interview Preparation Module
- Job Recommendation System
- LinkedIn Integration
- Real-Time Career Analytics
- Email Notifications
- Admin Dashboard
- AI Chatbot Career Assistant

---

🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a new feature branch.
3. Commit your changes.
4. Push to your branch.
5. Open a Pull Request.

---

📄 License

This project is developed for educational and learning purposes.

---

👩‍💻 Author

Kaviya B

Computer Science Student

If you found this project useful, consider giving it a ⭐ on GitHub.
