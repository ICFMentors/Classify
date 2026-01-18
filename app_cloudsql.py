"""
app_cloudsql.py - Production configuration for Google Cloud SQL

This file demonstrates how to configure Classify LMS to work with:
1. Cloud SQL via Public IP
2. Cloud SQL via Unix Socket (Cloud Run)
3. Cloud SQL via Proxy (local dev)
4. Traditional MySQL/SQLite (fallback)

USAGE:
1. Copy relevant sections to your app.py
2. Set environment variables in .env
3. Deploy to your platform
"""

from flask import Flask, render_template, request, redirect, session, flash, abort, url_for
from flask_login import current_user, login_user, logout_user, login_required, LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import sys
import os
from datetime import datetime
from sqlalchemy.orm import aliased
import pyrebase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# ===== SECURITY CONFIGURATION =====
app.secret_key = os.getenv('SECRET_KEY')

# ===== DATABASE CONFIGURATION =====

def get_database_uri():
    """
    Automatically detect the best database connection method based on environment.

    Priority order:
    1. DATABASE_URL environment variable (explicit override)
    2. Cloud SQL Unix Socket (for Cloud Run/Compute Engine)
    3. SQLite (for local development)
    """

    # Check for explicit DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url

    # Check if running on Cloud Run (has access to Cloud SQL via Unix socket)
    instance_connection_name = os.getenv('CLOUD_SQL_CONNECTION_NAME')
    if instance_connection_name:
        db_user = os.getenv('DB_USER', 'classify_app')
        db_pass = os.getenv('DB_PASSWORD')
        db_name = os.getenv('DB_NAME', 'school')

        # Cloud Run uses Unix sockets
        return f'mysql+pymysql://{db_user}:{db_pass}@/{db_name}?unix_socket=/cloudsql/{instance_connection_name}&charset=utf8mb4'

    # Default to SQLite for local development
    return 'sqlite:///data.db'

# Set database URI
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Optional: Connection pooling for production
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 5,
    'pool_recycle': 3600,  # Recycle connections after 1 hour
    'pool_pre_ping': True,  # Verify connections before using
    'max_overflow': 10,
    'connect_args': {
        'connect_timeout': 10,
    }
}

# Optional: SSL configuration for Cloud SQL
# Uncomment if you have SSL certificates
"""
if os.getenv('DB_SSL_CA'):
    app.config['SQLALCHEMY_ENGINE_OPTIONS']['connect_args']['ssl'] = {
        'ca': os.getenv('DB_SSL_CA'),
        # Optional: Client certificates for mutual TLS
        # 'cert': os.getenv('DB_SSL_CERT'),
        # 'key': os.getenv('DB_SSL_KEY'),
    }
"""

# ===== FIREBASE CONFIGURATION =====
config = {
    'apiKey': os.getenv('FIREBASE_API_KEY'),
    'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
    'projectId': os.getenv('FIREBASE_PROJECT_ID'),
    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
    'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
    'appId': os.getenv('FIREBASE_APP_ID'),
    'measurementId': os.getenv('FIREBASE_MEASUREMENT_ID'),
    'databaseURL': os.getenv('FIREBASE_DATABASE_URL', ' ')
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

db = SQLAlchemy(app)

############################################################################

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'log_in'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##########################################################################
# MODELS - Include all your existing model definitions here
##########################################################################

class Registration(db.Model):
    __tablename__ = 'registration'
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.userID'), primary_key=True)
    course_id = db.Column('course_id', db.Integer, db.ForeignKey('course.courseID'), primary_key=True)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    userID = db.Column('userID', db.Integer, primary_key=True)
    first_name = db.Column('first_name', db.String(50), nullable=False)
    last_name = db.Column('last_name', db.String(50), nullable=False)
    email = db.Column('email', db.String(100), unique=True, nullable=False)
    age = db.Column('age', db.Integer, nullable=False)
    gender = db.Column('gender', db.String(10), nullable=False)
    role = db.Column('role', db.String(20), nullable=False, default='student')

    enrolled_courses = db.relationship(
        'Course',
        secondary='registration',
        backref=db.backref('students', lazy='dynamic')
    )

    def get_id(self):
        return str(self.userID)

class Course(db.Model):
    __tablename__ = 'course'
    courseID = db.Column('courseID', db.Integer, primary_key=True)
    courseName = db.Column('courseName', db.String(255), nullable=False)
    description = db.Column('description', db.String(255), nullable=False)
    section = db.Column('section', db.String(10), nullable=False)
    totalSeats = db.Column('totalSeats', db.Integer, nullable=False)
    seatsTaken = db.Column('seatsTaken', db.Integer, nullable=False)
    dates = db.Column('dates', db.String(255), nullable=False)
    days = db.Column('days', db.String(255), nullable=False)
    timings = db.Column('timings', db.String(255), nullable=False)
    active = db.Column('active', db.String(255), nullable=False)
    teacherID = db.Column('teacherID', db.Integer, db.ForeignKey('teacher.teacherID'))

    teacher = db.relationship('Teacher', backref='courses')
    announcements = db.relationship('Announcement', backref='course', lazy='dynamic')

class Teacher(db.Model):
    __tablename__ = 'teacher'
    teacherID = db.Column('teacherID', db.Integer, primary_key=True)
    qualifications = db.Column('qualifications', db.String(400), nullable=False)
    experience = db.Column('experience', db.String(400), nullable=False)
    department = db.Column('department', db.String(255), nullable=False)
    status = db.Column('status', db.String(255), nullable=False)
    userID = db.Column('userID', db.Integer, db.ForeignKey('user.userID'), nullable=False)

    user = db.relationship('User', backref=db.backref('teacher_profile', uselist=False))

class Parent(db.Model):
    __tablename__ = 'parent'
    parentID = db.Column('parentID', db.Integer, primary_key=True)
    student1ID = db.Column('student1ID', db.Integer, db.ForeignKey('user.userID'))
    student2ID = db.Column('student2ID', db.Integer, db.ForeignKey('user.userID'), nullable=True)
    student3ID = db.Column('student3ID', db.Integer, db.ForeignKey('user.userID'), nullable=True)
    student4ID = db.Column('student4ID', db.Integer, db.ForeignKey('user.userID'), nullable=True)

class FAQ(db.Model):
    __tablename__ = 'FAQ'
    faqID = db.Column('faqID', db.Integer, primary_key=True)
    question = db.Column('question', db.String(255), nullable=False)
    answer = db.Column('answer', db.String(255), nullable=False)

class Question(db.Model):
    __tablename__ = 'question'
    questionID = db.Column('questionID', db.Integer, primary_key=True)
    query = db.Column('query', db.String(255), nullable=False)
    answer = db.Column('answer', db.String(255))
    userID = db.Column('userID', db.Integer, db.ForeignKey('user.userID'))

class Announcement(db.Model):
    __tablename__ = 'announcement'
    announcementID = db.Column('announcementID', db.Integer, primary_key=True)
    text = db.Column('text', db.String(500), nullable=False)
    courseID = db.Column('courseID', db.Integer, db.ForeignKey('course.courseID'))
    active = db.Column('active', db.String(10), nullable=False)
    expiration_date = db.Column('expiration_date', db.Date)

##########################################################################
# ROUTES - Include all your existing routes here
##########################################################################

# ... [ALL YOUR EXISTING ROUTES GO HERE] ...

##########################################################################
# ERROR HANDLERS
##########################################################################

@app.errorhandler(500)
def internal_server_error(e):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    app.logger.error("An internal server error occurred: %s", exc_value)
    return "Internal Server Error", 500

@app.errorhandler(404)
def not_found_error(error):
    return "Page not found", 404

@app.errorhandler(403)
def forbidden_error(error):
    return "Forbidden", 403

##########################################################################
# APPLICATION STARTUP
##########################################################################

if __name__ == '__main__':
    # Determine environment
    flask_env = os.getenv('FLASK_ENV', 'development')
    database_url = app.config['SQLALCHEMY_DATABASE_URI']

    # Print connection info (remove in production or use proper logging)
    print(f"Environment: {flask_env}")
    print(f"Database: {database_url.split('@')[1] if '@' in database_url else 'SQLite'}")

    # Create tables if using SQLite and database doesn't exist
    if 'sqlite' in database_url and not os.path.exists('data.db'):
        with app.app_context():
            db.create_all()
            print("✅ Database tables created")

    # Configure based on environment
    debug_mode = flask_env == 'development'
    port = int(os.getenv('PORT', 8080))

    # Production: Use Gunicorn instead of Flask dev server
    # This is only for local testing
    if debug_mode:
        app.run(debug=True, port=port, host='0.0.0.0')
    else:
        # In production, use: gunicorn app:app
        print("⚠️  For production, use: gunicorn app:app")
        app.run(debug=False, port=port, host='0.0.0.0')


##########################################################################
# EXAMPLE .env FILE CONFIGURATIONS
##########################################################################

"""
# ===== LOCAL DEVELOPMENT (SQLite) =====
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production

# Firebase credentials (same for all environments)
FIREBASE_API_KEY=your-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=1:123456789:web:abc123
FIREBASE_MEASUREMENT_ID=G-ABC123XYZ
FIREBASE_DATABASE_URL=


# ===== CLOUD SQL VIA PUBLIC IP =====
FLASK_ENV=production
SECRET_KEY=your-production-secret-key-32-chars-minimum
DATABASE_URL=mysql+pymysql://classify_app:PASSWORD@35.192.123.45:3306/school?charset=utf8mb4

# Firebase credentials...


# ===== CLOUD SQL VIA PROXY (Local Dev) =====
FLASK_ENV=development
SECRET_KEY=dev-secret-key
DATABASE_URL=mysql+pymysql://classify_app:PASSWORD@127.0.0.1:3306/school?charset=utf8mb4

# Firebase credentials...


# ===== CLOUD SQL VIA UNIX SOCKET (Cloud Run) =====
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
CLOUD_SQL_CONNECTION_NAME=project-id:region:instance-name
DB_USER=classify_app
DB_PASSWORD=your-db-password
DB_NAME=school

# Firebase credentials...


# ===== CLOUD SQL WITH SSL =====
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
DATABASE_URL=mysql+pymysql://classify_app:PASSWORD@35.192.123.45:3306/school?charset=utf8mb4&ssl_mode=REQUIRED
DB_SSL_CA=/path/to/server-ca.pem
# Optional mutual TLS:
# DB_SSL_CERT=/path/to/client-cert.pem
# DB_SSL_KEY=/path/to/client-key.pem

# Firebase credentials...
"""
