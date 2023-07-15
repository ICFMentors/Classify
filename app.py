from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import sys
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class FAQ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<FAQ %r>' % self.id

class User(db.Model):
    userID = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        age = int(request.form['selectbasic'])
        gender = request.form['radios']

        # Check if a user with the same username or email already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            error_message = 'Username or email already exists. Please choose a different one.'
            return render_template('sign-up.html', error_message=error_message)

        # Create a new user and add it to the database
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=password,
            age=age,
            gender=gender
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/student-home')
        except Exception as e:
            error_message = 'There was an issue signing you up. Please try again later.'
            return render_template('sign-up.html', error_message=error_message)
    else:
        return render_template('sign-up.html')


@app.route('/log-in', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists in the database
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            # Redirect the user to the appropriate home page based on their role
            if user.role == 'teacher':
                return redirect('/teacher-home')
            else:
                return redirect('/student-home')
        else:
            error_message = 'Invalid username or password. Please try again.'
            return render_template('log-in.html', error_message=error_message)
    else:
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

@app.route('/faq')
def display_faq():
    faq_entries = FAQ.query.all()
    return render_template('faq.html', faq_entries=faq_entries)

@app.route('/faq-student')
def faqStudent():
    faq_entries = FAQ.query.all()
    return render_template('faq-student.html', faq_entries=faq_entries)

@app.route('/submit-question', methods=['POST'])
def submit_question():
    question = request.form['question']
    send_email(question)
    return redirect('/faq')


@app.route('/about-us')
def aboutUs():
    return render_template('about-us.html')    

@app.errorhandler(500)
def internal_server_error(e):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    app.logger.error("An internal server error occurred: %s", exc_value)
    return "Internal Server Error", 500


if not os.path.exists('data.db'):  # Check if the database file doesn't exist
    db.create_all()

if __name__ == '__main__':
    app.run()

