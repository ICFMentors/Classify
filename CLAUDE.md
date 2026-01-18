# CLAUDE.md - Classify LMS Developer Guide

This document provides comprehensive guidance for AI assistants and developers working on the Classify Learning Management System.

## Table of Contents
- [Project Overview](#project-overview)
- [Codebase Structure](#codebase-structure)
- [Technology Stack](#technology-stack)
- [Database Schema](#database-schema)
- [Development Setup](#development-setup)
- [Architecture & Patterns](#architecture--patterns)
- [Route Organization](#route-organization)
- [Key Conventions](#key-conventions)
- [Security Considerations](#security-considerations)
- [Common Development Tasks](#common-development-tasks)
- [Code Navigation Guide](#code-navigation-guide)
- [Important Notes for AI Assistants](#important-notes-for-ai-assistants)

---

## Project Overview

**Classify** is a course management and learning management system (LMS) designed for ICF Mentors (Islamic Community Foundation) educational programs. The application facilitates:

- Multi-role user management (Students, Teachers, Parents)
- Course registration and enrollment
- Class creation and management
- Announcements with expiration dates
- FAQ system and user question submission
- Profile management for all user types

**Repository:** https://github.com/ICFMentors/Classify
**Python Version:** 3.8+
**Default Port:** 8080 (configurable in app.py line 668)

---

## Codebase Structure

```
/home/user/Classify/
├── .github/
│   └── dependabot.yml          # Automated dependency updates (weekly)
├── .vscode/
│   └── launch.json             # Chrome debugger config (localhost:8080)
├── env/                        # Python virtual environment (gitignored)
├── static/
│   ├── css/                    # 10 CSS files (~1585 lines total)
│   │   ├── styles.css          # Main stylesheet (413 lines)
│   │   ├── student-home.css    # Student dashboard styles
│   │   ├── button.css          # Button styles
│   │   ├── faq.css             # FAQ page styles
│   │   └── ...
│   └── images/                 # Logos, team photos, event flyers
├── templates/                  # 22 Jinja2 HTML templates (~2090 lines)
│   ├── base.html               # Base template with Bootstrap 5
│   ├── index.html              # Landing page
│   ├── log-in.html             # Login form
│   ├── sign-up.html            # Registration form
│   ├── student-home.html       # Student dashboard (166 lines)
│   ├── teacher-home.html       # Teacher dashboard (190 lines)
│   ├── parent-home.html        # Parent dashboard (140 lines)
│   ├── course-catalog.html     # Course browsing
│   ├── create-class.html       # Course creation
│   ├── create-announcement.html
│   ├── *-settings.html         # Role-specific settings
│   └── ...
├── app.py                      # Main Flask application (670 lines)
├── authenticate.py             # Firebase authentication testing
├── data.db                     # SQLite database (49KB, local dev)
├── data.sql                    # Database schema + sample data
├── requirements.txt            # Python dependencies (14 packages)
├── Procfile                    # Heroku deployment config
└── README.md                   # Setup instructions
```

---

## Technology Stack

### Backend
| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Flask | 2.2.5 |
| ORM | Flask-SQLAlchemy | 2.4.4 |
| Database (Local) | SQLite | 3.x |
| Database (Production) | MySQL via PyMySQL | - |
| Authentication | Firebase (Pyrebase4) | - |
| Session Management | Flask-Login | - |
| Template Engine | Jinja2 | 2.11.3 |
| WSGI Server | Gunicorn | 19.9.0 |

### Frontend
| Component | Technology | Version |
|-----------|------------|---------|
| UI Framework | Bootstrap | 5.0.2 |
| Icons | Bootstrap Icons | 1.5.0 |
| JavaScript | Bootstrap Bundle | 5.3.0 |
| Custom Styling | CSS | 1585+ lines |

### Development & Deployment
- **Package Manager:** pip
- **Virtual Environment:** virtualenv
- **Deployment:** Heroku (via Procfile)
- **IDE Support:** VS Code with Chrome debugging
- **Dependency Management:** Dependabot (weekly updates)

---

## Database Schema

### Models (SQLAlchemy ORM in app.py)

#### 1. User (app.py:62-76)
Primary user table for all roles.

```python
class User(db.Model, UserMixin):
    userID          # Integer, Primary Key
    first_name      # String(50), NOT NULL
    last_name       # String(50), NOT NULL
    email           # String(100), UNIQUE, NOT NULL
    age             # Integer, NOT NULL
    gender          # String(10), NOT NULL
    role            # String(20), DEFAULT 'student' (values: 'student', 'teacher', 'parent')
```

**Relationships:**
- `enrolled_courses` → Many-to-many with Course via Registration
- One-to-one with Teacher via `userID`

**Authentication:** Handled by Firebase (no password stored in database)

#### 2. Teacher (app.py:97-108)
Teacher-specific profile information.

```python
class Teacher(db.Model):
    teacherID       # Integer, Primary Key
    qualifications  # String(400), NOT NULL
    experience      # String(400), NOT NULL
    department      # String(255), NOT NULL
    status          # String(255), NOT NULL
    userID          # Integer, Foreign Key → User.userID
```

**Relationships:**
- `courses` → One-to-many with Course

#### 3. Course (app.py:77-94)
Course/class information.

```python
class Course(db.Model):
    courseID        # Integer, Primary Key
    courseName      # String(255), NOT NULL
    description     # String(255), NOT NULL
    section         # String(10), NOT NULL
    totalSeats      # Integer, NOT NULL
    seatsTaken      # Integer, NOT NULL
    dates           # String(255), NOT NULL (e.g., "June 1 - July 30")
    days            # String(255), NOT NULL (e.g., "Mon, Wed, Fri")
    timings         # String(255), NOT NULL (e.g., "10:00 AM - 12:00 PM")
    active          # String(255), NOT NULL (values: 'active', 'inactive')
    teacherID       # Integer, Foreign Key → Teacher.teacherID
```

**Relationships:**
- `teacher` → Many-to-one with Teacher
- `students` → Many-to-many with User via Registration
- `announcements` → One-to-many with Announcement

#### 4. Registration (app.py:49-60)
Many-to-many junction table for User-Course enrollment.

```python
class Registration(db.Model):
    user_id         # Integer, Foreign Key → User.userID, Primary Key
    course_id       # Integer, Foreign Key → Course.courseID, Primary Key
```

#### 5. Parent
Parent accounts linked to student accounts.

```python
class Parent(db.Model):
    parentID        # Integer, Primary Key
    student1ID      # Integer, Foreign Key → User.userID
    student2ID      # Integer, Foreign Key → User.userID (optional)
    student3ID      # Integer, Foreign Key → User.userID (optional)
    student4ID      # Integer, Foreign Key → User.userID (optional)
```

**Note:** Parents can be linked to 1-4 student accounts.

#### 6. FAQ
Pre-populated frequently asked questions.

```python
class FAQ(db.Model):
    faqID           # Integer, Primary Key
    question        # String(255), NOT NULL
    answer          # String(255), NOT NULL
```

#### 7. Question
User-submitted questions (not yet implemented in UI).

```python
class Question(db.Model):
    questionID      # Integer, Primary Key
    query           # String(255), NOT NULL
    answer          # String(255), nullable
    userID          # Integer, Foreign Key → User.userID
```

#### 8. Announcement
Course-specific announcements.

```python
class Announcement(db.Model):
    announcementID      # Integer, Primary Key
    text                # String(500), NOT NULL
    courseID            # Integer, Foreign Key → Course.courseID
    active              # String(10), NOT NULL (values: 'active', 'inactive')
    expiration_date     # Date, nullable
```

---

## Development Setup

### Initial Setup

```bash
# 1. Install virtualenv
pip install virtualenv

# 2. Create virtual environment
virtualenv env

# 3. Activate virtual environment
# On Windows:
.\env\Scripts\activate
# On macOS/Linux:
source env/bin/activate

# 4. Install dependencies
(env) pip install -r requirements.txt

# 5. Run the application
(env) python app.py
```

### Configuration

**Database:**
- **Local Development:** SQLite (`data.db`) - Auto-created if missing
- **Production:** MySQL at `34.106.105.100/school` (see app.py:15)
- Switch by commenting/uncommenting lines 14-15 in app.py

**Port Configuration:**
- Default: 8080 (app.py:668)
- Change by modifying: `app.run(debug=True, port=<desired_port>)`

**Debug Mode:**
- Enabled by default: `app.run(debug=True, ...)`
- Disable in production by setting `debug=False`

### Database Initialization

```python
# Run once to create tables (executed automatically if data.db doesn't exist)
if not os.path.exists('data.db'):
    db.create_all()
```

**Sample Data:** Located in `data.sql` with pre-populated users, courses, FAQs

---

## Architecture & Patterns

### MVC Pattern

**Model:** SQLAlchemy ORM classes in app.py (lines 49-160)
**View:** Jinja2 templates in templates/ directory
**Controller:** Flask route handlers in app.py (lines 170-660)

### Authentication Flow

1. **Firebase Authentication:** User credentials managed by Firebase
2. **Flask-Login:** Session management via `login_user()`, `logout_user()`
3. **Session Storage:** Flask sessions store `user_id`, `email`, `role`
4. **Route Protection:** `@login_required` decorator on protected routes

### Session Variables

```python
session['user_id']      # User.userID (integer)
session['email']        # User email (string)
session['role']         # User role: 'student', 'teacher', or 'parent'
```

### Error Handling

**404 Not Found:** Custom handler redirects to appropriate home based on role
**Firebase Errors:** Caught and displayed via `flash()` messages

---

## Route Organization

### Public Routes (No Authentication Required)

| Route | Method | Purpose | Template |
|-------|--------|---------|----------|
| `/` | GET | Landing page | index.html |
| `/sign-up` | GET, POST | User registration | sign-up.html |
| `/log-in` | GET, POST | User authentication | log-in.html |
| `/logout` | GET | End session | - (redirects to /) |

### Student Routes (`@login_required`)

| Route | Method | Purpose | Template |
|-------|--------|---------|----------|
| `/student-home` | GET | Student dashboard | student-home.html |
| `/student-settings` | GET, POST | Profile management | student-settings.html |
| `/course-catalog` | GET | Browse courses | course-catalog.html |
| `/register-course/<id>` | POST | Enroll in course | - (redirects) |
| `/faq-student` | GET | FAQ page | faq-student.html |
| `/about-us-student` | GET | About page | about-us-student.html |

### Teacher Routes (`@login_required`)

| Route | Method | Purpose | Template |
|-------|--------|---------|----------|
| `/teacher-home` | GET | Teacher dashboard | teacher-home.html |
| `/teacher-settings` | GET, POST | Profile management | teacher-settings.html |
| `/teacher-profile/<id>` | GET | View teacher profile | teacher-profile.html |
| `/create-class` | GET, POST | Create new course | create-class.html |
| `/create-announcement` | GET, POST | Create announcement | create-announcement.html |
| `/edit-announcement/<id>` | GET, POST | Edit announcement | edit-announcement.html |
| `/deactivate-announcement/<id>` | POST | Disable announcement | - (redirects) |
| `/delete_course/<id>` | POST | Deactivate course | - (redirects) |
| `/faq-teacher` | GET | FAQ page | faq-teacher.html |
| `/about-us-teacher` | GET | About page | about-us-teacher.html |

### Parent Routes (`@login_required`)

| Route | Method | Purpose | Template |
|-------|--------|---------|----------|
| `/parent-home` | GET | Parent dashboard | parent-home.html |
| `/parent-settings` | GET, POST | Parent settings | parent-settings.html |
| `/faq-parent` | GET | FAQ page | faq-parent.html |
| `/about-us-parent` | GET | About page | about-us-parent.html |

---

## Key Conventions

### Coding Style

1. **Database Queries:** Use SQLAlchemy ORM, not raw SQL
2. **Template Rendering:** Pass data via `render_template()` keyword arguments
3. **Form Handling:** Use `request.form.get()` for POST data
4. **Flash Messages:** Use `flash()` for user feedback
5. **Redirects:** Use `redirect()` for POST-success patterns

### Naming Conventions

- **Routes:** Use lowercase with hyphens (e.g., `/student-home`)
- **Templates:** Match route names (e.g., `student-home.html`)
- **CSS Files:** Match page names (e.g., `student-home.css`)
- **Database Columns:** camelCase (e.g., `userID`, `courseName`)
- **Python Variables:** snake_case (e.g., `user_id`, `course_name`)

### Template Structure

All templates extend `base.html`:

```jinja2
{% extends "base.html" %}

{% block title %}Page Title{% endblock %}

{% block head %}
    <link rel="stylesheet" href="{{ url_for('static', filename='css/page-specific.css') }}">
{% endblock %}

{% block body %}
    <!-- Page content -->
{% endblock %}
```

### Role-Based Access Control

```python
# Check user role from session
if session.get('role') == 'teacher':
    # Teacher-specific logic
elif session.get('role') == 'student':
    # Student-specific logic
```

### Course Registration Pattern

```python
# Check seats availability
if course.seatsTaken < course.totalSeats:
    # Create registration
    registration = Registration(user_id=user.userID, course_id=course.courseID)
    db.session.add(registration)

    # Update seats taken
    course.seatsTaken += 1
    db.session.commit()
```

---

## Security Considerations

### Critical Security Issues

**WARNING:** The following security issues exist in the codebase:

1. **Hardcoded Firebase Credentials** (app.py:19-28)
   - API keys exposed in source code
   - Should be moved to environment variables

2. **Hardcoded Database Credentials** (app.py:15)
   - Username: `classifydbuser`
   - Password: `WeakPass@23`
   - **Action Required:** Use environment variables + `.env` file

3. **Hardcoded Secret Key** (app.py:13)
   - `app.secret_key = 'summer2023project'`
   - Should be cryptographically random and stored securely

### Recommended Security Improvements

```python
# Use python-dotenv (already in requirements.txt)
from dotenv import load_dotenv
import os

load_dotenv()

# Secure configuration
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

# Firebase config from environment
config = {
    'apiKey': os.getenv('FIREBASE_API_KEY'),
    'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
    # ... etc
}
```

### Additional Security Measures

- **CSRF Protection:** Not currently implemented (consider Flask-WTF)
- **Input Validation:** Minimal validation on forms
- **SQL Injection:** Protected by SQLAlchemy ORM
- **XSS Protection:** Jinja2 auto-escapes by default

---

## Common Development Tasks

### Adding a New Route

```python
@app.route('/new-route', methods=['GET', 'POST'])
@login_required
def new_route():
    if request.method == 'POST':
        # Handle form submission
        data = request.form.get('field_name')
        # Process and redirect
        return redirect('/success-page')

    # Render template for GET
    return render_template('new-template.html')
```

### Creating a New Model

```python
class NewModel(db.Model):
    __tablename__ = 'new_table'
    id = db.Column(db.Integer, primary_key=True)
    field1 = db.Column(db.String(100), nullable=False)

    # After adding model, recreate database or use migrations
```

### Adding a New Template

1. Create `templates/new-page.html`
2. Extend base template
3. Add route in app.py
4. Create CSS file in `static/css/` if needed
5. Link CSS in template's `{% block head %}`

### Working with Database

```python
# Query examples
user = User.query.filter_by(email='email@example.com').first()
courses = Course.query.filter_by(active='active').all()
teacher = Teacher.query.get(teacher_id)

# Create new record
new_user = User(
    first_name='John',
    last_name='Doe',
    email='john@example.com',
    age=25,
    gender='M',
    role='student'
)
db.session.add(new_user)
db.session.commit()

# Update record
user.age = 26
db.session.commit()

# Delete (soft delete by setting active='inactive')
course.active = 'inactive'
db.session.commit()
```

### Adding Static Assets

**CSS:**
- Place in `static/css/`
- Link in template: `<link rel="stylesheet" href="{{ url_for('static', filename='css/your-file.css') }}">`

**Images:**
- Place in `static/images/`
- Reference: `<img src="{{ url_for('static', filename='images/your-image.png') }}">`

---

## Code Navigation Guide

### Key Files to Know

| File | Lines | Purpose | Key Sections |
|------|-------|---------|--------------|
| app.py | 670 | Main application | Lines 49-160: Models<br>Lines 170-660: Routes |
| base.html | ~50 | Base template | Bootstrap setup, nav structure |
| student-home.html | 166 | Student dashboard | Enrolled courses display |
| teacher-home.html | 190 | Teacher dashboard | Course management, announcements |
| styles.css | 413 | Main styles | Global styles, layout |

### Finding Functionality

**Authentication Logic:** app.py lines 190-250 (`/sign-up`, `/log-in`)
**Course Registration:** app.py lines 350-380 (`/register-course/<id>`)
**Course Creation:** app.py lines 420-460 (`/create-class`)
**Announcements:** app.py lines 480-550 (create, edit, deactivate)
**User Settings:** app.py lines 280-340 (role-specific settings)

### Template Hierarchy

```
base.html (Bootstrap, navbar)
├── index.html (landing page)
├── log-in.html (authentication)
├── sign-up.html (registration)
├── student-home.html
│   └── Includes: course cards, announcements
├── teacher-home.html
│   └── Includes: course management, announcement creation
├── parent-home.html
│   └── Includes: student information cards
└── *-settings.html (profile management)
```

---

## Important Notes for AI Assistants

### When Making Changes

1. **Always Read Before Modifying**
   - Read the entire file before making changes
   - Understand existing patterns and conventions
   - Match the existing code style

2. **Database Changes Require Care**
   - Modifying models requires database migration or recreation
   - Test with local SQLite before touching production MySQL
   - Consider data migration for existing records

3. **Respect Role-Based Architecture**
   - Student, Teacher, Parent roles have distinct workflows
   - Don't mix role-specific logic in shared routes
   - Maintain separate templates for each role

4. **Session Management**
   - Always check `session.get('user_id')` for authentication
   - Validate user role before role-specific operations
   - Clear session data on logout

5. **Firebase Integration**
   - Password management is handled by Firebase
   - Don't try to store passwords in database
   - Firebase errors should be caught and displayed to users

### Testing Considerations

**No Automated Tests:** This project currently has no test suite

**Manual Testing Checklist:**
- [ ] Test as student user
- [ ] Test as teacher user
- [ ] Test as parent user (if applicable)
- [ ] Verify database changes persist
- [ ] Check for broken links
- [ ] Validate form submissions
- [ ] Test error cases (invalid data, full courses, etc.)

### Deployment Notes

**Heroku Deployment:**
```bash
# Procfile specifies:
web: gunicorn app:app

# Ensure requirements.txt is up to date
pip freeze > requirements.txt

# Push to Heroku
git push heroku main
```

**Environment Variables for Production:**
- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: MySQL connection string
- `FIREBASE_*`: Firebase configuration values

### Common Pitfalls to Avoid

1. **Don't delete unused code without verifying**
   - The codebase has some incomplete features (e.g., Question model not fully integrated)
   - Check if features are planned for future development

2. **Be cautious with database switches**
   - SQLite (local) and MySQL (production) have different behaviors
   - Test queries that work in SQLite may fail in MySQL

3. **Respect the contributing guidelines**
   - Per README.md line 40: "Style changes, adding libraries, etc are not valid changes"
   - Focus on security fixes, bug fixes, and explicitly requested features

4. **Don't over-engineer**
   - This is a tutorial-based project
   - Keep solutions simple and maintainable
   - Match the existing complexity level

### Quick Reference: User Roles

| Role | Primary Features | Main Routes |
|------|------------------|-------------|
| **Student** | Browse courses, enroll, view announcements | `/student-home`, `/course-catalog` |
| **Teacher** | Create courses, manage announcements, view roster | `/teacher-home`, `/create-class` |
| **Parent** | View student information, track progress | `/parent-home` |

### Database Quick Reference

**Get current user:**
```python
user = User.query.get(session['user_id'])
```

**Get user's enrolled courses:**
```python
courses = user.enrolled_courses
```

**Get teacher's courses:**
```python
teacher = Teacher.query.filter_by(userID=user.userID).first()
courses = teacher.courses if teacher else []
```

**Get active announcements for a course:**
```python
announcements = Announcement.query.filter_by(
    courseID=course_id,
    active='active'
).all()
```

---

## Version History

**Last Updated:** 2026-01-18
**Repository Status:** Active development
**Python Version:** 3.8+
**Flask Version:** 2.2.5

---

## Questions or Issues?

For questions about this codebase or to report issues:
- **Repository:** https://github.com/ICFMentors/Classify
- **Issues:** https://github.com/ICFMentors/Classify/issues

---

*This document is auto-generated and should be updated when significant changes are made to the codebase structure, architecture, or conventions.*
