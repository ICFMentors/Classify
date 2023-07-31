from flask import Flask, render_template, request, redirect, session
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import sys
import os
from flask_login import LoginManager, UserMixin


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.secret_key = 'your_secret_key'  # Set a secret key for session security
db = SQLAlchemy(app)

############################################################################3

# Initialize Flask-Login
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ensure the User class inherits from UserMixin


    ##########################################################################

class Registration(db.Model):
    __tablename__ = 'registration'
    user_id = db.Column(db.Integer, db.ForeignKey('user.userID'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.courseID'), primary_key=True)
    # Add any additional fields related to the registration if needed

    # Add relationships to User and Course models
    user = db.relationship('User', backref=db.backref('registrations', lazy=True))
    course = db.relationship('Course', backref=db.backref('registrations', lazy=True))

    def __repr__(self):
        return f'<Registration user_id={self.user_id} course_id={self.course_id}>'

class User(db.Model, UserMixin):
    userID = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')

    # Add the enrolled_courses relationship to represent the courses a user is enrolled in
    enrolled_courses = db.relationship('Course', secondary='registration', backref=db.backref('students', lazy='dynamic'))

    def __repr__(self):
        return f'<User {self.username}>'

class Course(db.Model):
    __tablename__ = 'course'
    courseID = db.Column(db.Integer, primary_key=True)
    courseName = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    totalSeats = db.Column(db.Integer, nullable=False)
    seatsTaken = db.Column(db.Integer, nullable=False)
    teacherID = db.Column(db.Integer, db.ForeignKey('teacher.teacherID'), nullable=False)
    dates = db.Column(db.String(255), nullable=False)
    timings = db.Column(db.String(255), nullable=False)

    teacher = db.relationship('Teacher', backref=db.backref('courses', lazy=True))

    def __repr__(self):
        return '<Course %r>' % self.courseID


class Teacher(db.Model):
    teacherID = db.Column(db.Integer, primary_key=True)
    qualifications = db.Column(db.String(400), nullable=False)
    experience = db.Column(db.String(400), nullable=False)
    department = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey('user.userID'), nullable=False)

    user = db.relationship('User', backref=db.backref('teacher', uselist=False))

    def __repr__(self):
        return '<Teacher %r>' % self.teacherID

class Parent(db.Model):
    parentID = db.Column(db.Integer, primary_key=True)
    student1ID = db.Column(db.Integer, db.ForeignKey('user.userID'), nullable=False)
    student2ID = db.Column(db.Integer, db.ForeignKey('user.userID'), nullable=False)
    student3ID = db.Column(db.Integer, db.ForeignKey('user.userID'), nullable=False)
    student4ID = db.Column(db.Integer, db.ForeignKey('user.userID'), nullable=False)

    # Define the relationships and specify the join conditions
    student1 = db.relationship('User', foreign_keys=[student1ID], backref=db.backref('Parent1', lazy=True))
    student2 = db.relationship('User', foreign_keys=[student2ID], backref=db.backref('Parent2', lazy=True))
    student3 = db.relationship('User', foreign_keys=[student3ID], backref=db.backref('Parent3', lazy=True))
    student4 = db.relationship('User', foreign_keys=[student4ID], backref=db.backref('Parent4', lazy=True))

    def __repr__(self):
        return '<Parent %r>' % self.parentID


class FAQ(db.Model):
    faqID = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<FAQ %r>' % self.id



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/student-home')
def studentHome():
    user_id = session.get('user_id')
    student = User.query.get(user_id)
    courses = student.enrolled_courses  # Change this to student.enrolled_courses
    return render_template('student-home.html', student=student, courses=courses)


@app.route('/student-settings')
def studentSettings():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('student-settings.html', user=user)

@app.route('/update-student', methods=['POST'])
def updateStudent():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    pass
    
    if user:
        # Update user information from the form data
        user.first_name = request.form['first']
        user.last_name = request.form['last']
        user.email = request.form['email']
        user.username = request.form['username']
        user.age = int(request.form['selectbasic'])
        user.gender = request.form['radios']
        user.password = request.form['new_password']
        
        try:
            db.session.commit()
            return redirect('/student-home')
        except Exception as e:
            error_message = 'There was an issue updating the user information. Please try again later.'
            return render_template('student-settings.html', user=user, error_message=error_message)
    else:
        error_message = 'User not found.'
        return render_template('student-settings.html', user=user, error_message=error_message)



@app.route('/teacher-home')
def teacherHome():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    courses = Course.query.join(Teacher).join(User).filter(User.userID == user_id).all()
    return render_template('teacher-home.html', user=user, courses=courses)


@app.route('/teacher-settings')
def teacherSettings():
    teacher_id = session.get('user_id')
    teacher = Teacher.query.get(teacher_id)
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('teacher-settings.html', teacher=teacher, user=user)

@app.route('/update-teacher', methods=['POST'])
def updateTeacher():
    teacher_id = session.get('user_id')
    teacher = Teacher.query.get(teacher_id)
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    pass
    
    if teacher:
        # Update teacher information from the form data
        teacher.qualifications = request.form['qualifications']
        teacher.experience = request.form['experience']
        teacher.department = request.form['department']
        teacher.status = request.form['status']
        
        try:
            db.session.commit()
            return redirect('/teacher-home')
        except Exception as e:
            error_message = 'There was an issue updating the teacher information. Please try again later.'
            return render_template('teacher-settings.html', teacher=teacher, error_message=error_message)
    else:
        error_message = 'Teacher not found.'
        return render_template('teacher-settings.html', teacher=teacher, error_message=error_message)


@app.route('/parent-home')
def parentHome():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('parent-home.html', user=user)

@app.route('/parent-settings')
def parentSettings():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('parent-settings.html', user=user)


@app.route('/sign-up', methods=['GET', 'POST'])
def signUp():
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

            # Store the user ID in the session
            session['user_id'] = new_user.userID

            return redirect('/student-home')
        except Exception as e:
            error_message = 'There was an issue signing you up. Please try again later.'
            return render_template('sign-up.html', error_message=error_message)
    else:
        return render_template('sign-up.html')


@app.route('/log-in', methods=['GET', 'POST'])
def log_in():                  #WE CHANGED logIn to log_in ##########################3
    if request.method == 'POST':
        # Retrieve form data
        username = request.form['username']
        password = request.form['password']
        login_role = request.form['login_role']

        # Check if the user exists in the database
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            # Store the user ID in the session
            session['user_id'] = user.userID

            if login_role == 'student':
                return redirect('/student-home')
            elif login_role == 'teacher':
                return redirect('/teacher-home')
            elif login_role == 'parent':
                return redirect('/parent-home')
            else:
                error_message = 'Invalid login role. Please try again.'
        else:
            error_message = 'Invalid username or password. Please try again.'

        return render_template('log-in.html', error_message=error_message)
    else:
        return render_template('log-in.html')


@app.route('/course-catalog')
def courseCatalog():
    courses = Course.query.all()
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    registered_course_ids = [course.courseID for course in user.enrolled_courses]

    return render_template('course-catalog.html', courses=courses, registered_course_ids=registered_course_ids)


@app.route('/create-class', methods=['GET', 'POST'])
def createClass():
    if request.method == 'POST':
        # Retrieve form data
        courseName = request.form['courseName']
        description = request.form['description']
        section = request.form['section']
        totalSeats = int(request.form['totalSeats'])
        seatsTaken = int(request.form['seatsTaken'])
        teacher_username = request.form['teacher']  # Assuming the teacher's username is provided in the form
        dates = request.form['dates']
        timings = request.form['timings']

        # Find the teacher by username
        teacher = Teacher.query.join(User).filter(User.username == teacher_username).first()

        if not teacher:
            # If the teacher doesn't exist, you can choose to create a new teacher or show an error message.
            # For simplicity, let's assume the teacher must exist in the database.
            error_message = 'Teacher not found. Please enter a valid teacher username.'
            return render_template('create-class.html', error_message=error_message)

        # Create a new course and add it to the database
        new_course = Course(
            courseName=courseName,
            description=description,
            section=section,
            totalSeats=totalSeats,
            seatsTaken=seatsTaken,
            teacher=teacher,  # Set the teacher object in the new course
            dates=dates,
            timings=timings
        )

        try:
            db.session.add(new_course)
            db.session.commit()
            return redirect('/course-catalog')  # Redirect to the course catalog page after adding the class
        except Exception as e:
            error_message = 'There was an issue adding the class. Please try again later.'
            return render_template('create-class.html', error_message=error_message)
    else:
        return render_template('create-class.html')



@app.route('/faq-teacher')
def faqTeacher():
    faq_entries = FAQ.query.all()
    return render_template('faq-teacher.html', faq_entries=faq_entries)


@app.route('/faq-student')
def faqStudent():
    faq_entries = FAQ.query.all()
    return render_template('faq-student.html', faq_entries=faq_entries)

@app.route('/faq-parent')
def faqParent():
    faq_entries = FAQ.query.all()
    return render_template('faq-parent.html', faq_entries=faq_entries)

@app.route('/teacher-profile')
def teacherprofile():
    teacher_id = session.get('user_id')
    teacher = Teacher.query.get(teacher_id)
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('teacher-profile.html', teacher=teacher, user=user)


@app.route('/about-us-student')
def aboutUsStudent():
    return render_template('about-us-student.html')

@app.route('/about-us-teacher')
def aboutUsTeacher():
    return render_template('about-us-teacher.html')

@app.route('/about-us-parent')
def aboutUsParent():
    return render_template('about-us-parent.html')


@app.errorhandler(500)
def internal_server_error(e):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    app.logger.error("An internal server error occurred: %s", exc_value)
    return "Internal Server Error", 500



@app.route('/register-course/<int:course_id>', methods=['POST'])
def register_course(course_id):
    # Check if the user is logged in
    if not current_user.is_authenticated:
        return redirect('/log-in')  # Redirect to login page if not logged in

    # Get the course with the given course_id from the database
    course = Course.query.get(course_id)

    # Check if the course exists
    if not course:
        # Handle the case where the course doesn't exist (e.g., display an error message)
        pass

    # Check if the user is already registered for the course
    if current_user in course.students:
        # Handle the case where the user is already registered for the course
        pass

    # Register the current user for the course (add the user to the course's students relationship)
    course.students.append(current_user)
    db.session.commit()

    # Optionally, you can add a success message here and redirect to the course catalog
    return redirect('/course_catalog')

if __name__ == '__main__':
    # Create all tables if they don't exist
    if not os.path.exists('data.db'):
        db.create_all()

    app.run(debug=True)