"""
Production-ready version of app.py with environment variables.
This file shows the changes needed for production deployment.

INSTRUCTIONS:
1. Copy this file over app.py OR
2. Apply the changes from this file to your existing app.py
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

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# ===== PRODUCTION CONFIGURATION =====
# Use environment variables instead of hardcoded values
app.secret_key = os.getenv('SECRET_KEY', 'fallback-dev-key-change-in-production')

# Database configuration from environment
database_url = os.getenv('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Firebase configuration from environment variables
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
login_manager.login_view = 'log_in'  # Redirect to login page if not authenticated

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##########################################################################
# NOTE: Include all your existing model definitions here
# (User, Teacher, Course, Registration, Parent, FAQ, Question, Announcement)
##########################################################################

# ... [ALL YOUR EXISTING MODELS GO HERE] ...

##########################################################################
# NOTE: Include all your existing routes here
##########################################################################

# ... [ALL YOUR EXISTING ROUTES GO HERE] ...

##########################################################################

if __name__ == '__main__':
    # Check environment
    flask_env = os.getenv('FLASK_ENV', 'development')

    # Create tables if needed (only for SQLite in development)
    if 'sqlite' in database_url and not os.path.exists('data.db'):
        with app.app_context():
            db.create_all()

    # Configure based on environment
    debug_mode = flask_env == 'development'
    port = int(os.getenv('PORT', 8080))

    # Run the application
    app.run(debug=debug_mode, port=port, host='0.0.0.0')
