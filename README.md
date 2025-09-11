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

Run test module:

    # Login tests
    python manage.py test accounts.tests.test_login

    # Registration tests
    python manage.py test accounts.tests.test_registration

    # Student exam flow tests
    python manage.py test exams.tests.test_student_exam_flow

    # Staff exam flow tests
    python manage.py test exams.tests.test_staff_exam_flow

    # Permissions / access control tests
    python manage.py test exams.tests.test_permissions

### ✅ Test Coverage Summary

- **Login & Registration**
  - Student/staff login redirects
  - Invalid login remains on page
  - Valid/invalid registration cases

- **Student Exam Flow**
  - Full exam attempt with correct answers → 100% score
  - Exam attempt with wrong answers → 0% score
  - Navigation (next, back, submit) and result page checks

- **Staff Exam Flow**
  - Exam creation (auto-linked to staff module)
  - Add/manage/delete exam questions
  - Results overview, per-exam results, per-question stats
  - Attempt detail view and CSV export

- **Permissions & Access Control**
  - Students cannot access staff views
  - Staff cannot access student views
  - Anonymous users redirected to login
  - Staff blocked from managing exams in other modules

---

## 📂 Project Structure

    online_exam_system/
    │
    ├── accounts/         
    │   ├── models.py         # Custom user model (student, staff, admin)
    │   ├── views.py          # Auth, registration, dashboards
    │   ├── forms.py          # Registration & login forms
    │   ├── management/
    │   │   └── commands/
    │   │       ├── seed_staff.py       # Seeder for staff users
    │   │       └── seed_students.py    # Seeder for student users
    │   └── tests/
    │       ├── test_login.py           # Login tests
    │       └── test_registration.py    # Registration tests
    │
    ├── exams/
    │   ├── models.py         # Exam, ExamQuestion, StudentAttempt, StudentAnswer
    │   ├── views.py          # Student + staff exam flow, analytics
    │   ├── forms.py          # Exam creation & question forms
    │   ├── management/
    │   │   └── commands/
    │   │       ├── fix_exam_timings.py       # Adjust exam open/close times
    │   │       ├── reset_attempts.py         # Reset attempts/answers
    │   │       ├── seed_exams.py             # Seeder for exams
    │   │       ├── seed_modules.py           # Seeder for modules
    │   │       ├── seed_questions.py         # Seeder for questions
    │   │       └── seed_attempts_results.py  # Seeder for attempts + results
    │   └── tests/
    │       ├── test_student_exam_flow.py     # Student exam flow tests
    │       ├── test_staff_exam_flow.py       # Staff exam flow tests
    │       └── test_permissions.py           # Role restrictions tests
    │
    ├── questions/
    │   ├── models.py         # Question model (MCQ, TF, Fill-in-the-gap)
    │   └── forms.py          # Question creation forms
    │
    ├── templates/            # Bootstrap-based HTML templates
    │   ├── accounts/         # Login, registration, dashboards
    │   ├── exams/            # Exam flow, results, staff views
    │   └── base.html         # Global layout
    │
    ├── static/               
    │   └── images/           # CSSS logo
    │
    ├── config/               # Django settings, URLs, WSGI
    ├── manage.py
    └── README.md

---

## 📜 License

This project was developed for academic purposes as part of an **MSc Computer Science project**.
