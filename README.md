# 🎓 CSSS Online Examination System

An online examination platform built with **Django + PostgreSQL**, designed for academic use at the **Computer Science Success School (CSSS)**.  
The system supports **students**, **staff (teachers)**, and **admins**, providing features for exams, automated grading, and results analytics.

---

## 🚀 Features

### 👩‍🎓 Students
- Register/login with student ID (`CSSS25xxx`)
- View modules and upcoming exams
- Take exams (one question per page, navigation allowed)
- Auto-submit on timer expiry or exam close
- View results with correct/wrong breakdown

### 👩‍🏫 Staff (Teachers)
- Create and manage exams
- Add/manage exam questions
- View results per student or per question
- Export results as CSV
- Dashboard with module & student statistics

### 🛠 Admin
- Full Django Admin panel (branded as CSSS Administration)
- Manage users, exams, modules
- Seed or reset demo data with management commands

---

## ⚙️ Installation & Setup

    # 1) Clone the repository
    git clone https://github.com/yourusername/online_exam_system.git
    cd online_exam_system

    # 2) Create and activate a virtual environment
    python3 -m venv .venv
    source .venv/bin/activate        # Windows: .venv\Scripts\activate

    # 3) Install dependencies
    pip install -r requirements.txt

    # 4) Apply migrations
    python manage.py migrate

    # 5) Create an admin (superuser)
    python manage.py createsuperuser

    # 6) Run the development server
    python manage.py runserver

Visit: http://127.0.0.1:8000

---

## 🐘 PostgreSQL Setup

Create the database and user (adjust names/passwords if needed):

    CREATE DATABASE exam_system;
    CREATE USER exam_user WITH PASSWORD 'password123';
    GRANT ALL PRIVILEGES ON DATABASE exam_system TO exam_user;

Connection settings (already set in `settings.py`):

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'exam_system',
            'USER': 'exam_user',
            'PASSWORD': 'password123',
            'HOST': 'localhost',
            'PORT': '5432',
            'CONN_MAX_AGE': 60,
        }
    }

---

## 🌱 Seeding Demo Data

The project includes seed commands to populate demo data quickly:

    # Clear all student attempts & answers (optional before reseeding)
    python manage.py reset_attempts

    # Seed core data
    python manage.py seed_staff
    python manage.py seed_students
    python manage.py seed_modules
    python manage.py seed_exams
    python manage.py seed_questions
    python manage.py seed_attempts_results

**Default demo passwords**
- Students → `Stu1234!`  
- Staff → `Teach1234!`

---

## 🔑 Demo Accounts

- **Superuser/Admin** → created via `createsuperuser`
- **Staff** (examples from seeder) → `alice@csss.com`, `john@csss.com` (password `Teach1234!`)
- **Students** → `CSSS251001@csss.com`, `CSSS251002@csss.com`, … (password `Stu1234!`)

(Staff/student usernames without the domain also work for login depending on your auth form configuration.)

---

## 🧪 Running Tests

    python manage.py test

---

## 📂 Project Structure

    online_exam_system/
    │
    ├── accounts/         # Custom user model (student, staff, admin), auth, registration, dashboards
    ├── exams/            # Exam models, attempts, results, analytics, seed commands
    ├── questions/        # Question models & exam linkage
    │
    ├── templates/        # Bootstrap-based HTML templates (students, staff, partials, base)
    ├── static/           # CSSS logo and other static assets
    │
    ├── config/           # Django settings, URLs, WSGI
    ├── manage.py
    └── README.md

---

## 📜 License

This project was developed for academic purposes as part of an **MSc Computer Science project**.
