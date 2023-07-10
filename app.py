from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sign-up')
def signup():
    return render_template('sign-up.html')

@app.route('/log-in')
def login():
    return render_template('log-in.html')

@app.route('/student-home')
def studentHome():
    return render_template('student-home.html')

@app.route('/student-profile')
def studentProfile():
    return render_template('student-profile.html')

@app.route('/teacher-home')
def teacherHome():
    return render_template('teacher-home.html')
 
@app.route('/teacher-settings')
def teacherSettings():
    return render_template('teacher-settings.html')

@app.route('/course-catalog')
def courseCatalog():
    return render_template('course-catalog.html')

@app.route('/faq', methods=['POST', 'GET'])
def FAQ():
    faq = faqs.query.all()
    return render_template('faq.html', faq=faq)


@app.route('/about-us')
def aboutUs():
    return render_template('about-us.html')    

@app.errorhandler(500)
def internal_server_error(e):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    app.logger.error("An internal server error occurred: %s", exc_value)
    return "Internal Server Error", 500

if __name__ == '__main__':
    app.run()
