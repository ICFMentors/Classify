from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import sys
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


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


class Teacher(db.Model):
    teacherID = db.Column(db.Integer, primary_key=True)
    qualifications = db.Column(db.String(400), nullable=False)
    experience = db.Column(db.String(400), nullable=False)
    department = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey('user.userID'), nullable=False)

    user = db.relationship('User', backref=db.backref('Teacher', lazy=True))

    def __repr__(self):
        return '<Teacher %r>' % self.teacherID


class Course(db.Model):
    courseID = db.Column(db.Integer, primary_key=True)
    courseName = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    totalSeats = db.Column(db.Integer, nullable=False)
    seatsTaken = db.Column(db.Integer, nullable=False)
    teacherID = db.Column(db.Integer, db.ForeignKey('teacher.teacherID'), nullable=False)
    dates = db.Column(db.String(255), nullable=False)
    timings = db.Column(db.String(255), nullable=False)

    teacher = db.relationship('Teacher', backref=db.backref('Courses', lazy=True))

    def __repr__(self):
        return '<Course %r>' % self.courseID


class FAQ(db.Model):
    faqID = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<FAQ %r>' % self.id


if not os.path.exists('data.db'):  # Check if the database file doesn't exist
    db.create_all()


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
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM course')
    courses = cursor.fetchall()
    conn.close()
    return render_template('course-catalog.html', courses=courses)

@app.route('/create-class', methods=['GET', 'POST'])
def createClass():
    if request.method == 'POST':
        # Retrieve form data
        courseName = request.form['courseName']
        description = request.form['description']
        section = request.form['section']
        totalSeats = int(request.form['totalSeats'])
        seatsTaken = int(request.form['seatsTaken'])
        teacher_id = int(request.form['teacher'])  # Assuming the teacher ID is an integer
        dates = request.form['dates']
        timings = request.form['timings']

        # Retrieve the corresponding Teacher object based on the provided teacher ID
        teacher = Teacher.query.get(teacher_id)

        if teacher is None:
            error_message = 'Invalid teacher ID. Please enter a valid teacher ID.'
            return render_template('create-class.html', error_message=error_message)

        # Create a new course and add it to the database
        new_course = Course(
            courseName=courseName,
            description=description,
            section=section,
            totalSeats=totalSeats,
            seatsTaken=seatsTaken,
            teacher=teacher,
            dates=dates,
            timings=timings
        )

        try:
            db.session.add(new_course)
            db.session.commit()
            return redirect('/course-catalog')
        except Exception as e:
            error_message = 'There was an issue adding the class. Please try again later.'
            return render_template('create-class.html', error_message=error_message)
    else:
        return render_template('create-class.html')



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


if __name__ == '__main__':
    app.run()

