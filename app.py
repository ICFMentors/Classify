from flask import Flask, render_template, request, redirect, session, flash, abort, url_for
from flask_login import current_user, login_user, logout_user, login_required, LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import sys
import os
from datetime import datetime
from sqlalchemy.orm import aliased
import pyrebase


app = Flask(__name__)
app.secret_key = 'summer2023project'  # Set a secret key for session security
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://classifydbuser:WeakPass@23@34.106.105.100/school'
#app.config['SQLALCHEMY_TRACK_NOTIFICATIONS'] = False

# For Firebase JS SDK v7.20.0 and later, measurementId is optional
config = {
    'apiKey': "AIzaSyBWQXbSBC6oKNZk96jMP53qvHJqekG0T1Q",
    'authDomain': "summer-2023-396400.firebaseapp.com",
    'projectId': "summer-2023-396400",
    'storageBucket': "summer-2023-396400.appspot.com",
    'messagingSenderId': "900862315561",
    'appId': "1:900862315561:web:fa9f9ccf3f5f2b4f6b6038",
    'measurementId': "G-XYTJ9FBMVG",
    'databaseURL': " "
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

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
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')

    # Add the enrolled_courses relationship to represent the courses a user is enrolled in
    enrolled_courses = db.relationship('Course', secondary='registration', backref=db.backref('students', lazy='dynamic'))

    def get_id(self):
        return str(self.userID)

class Course(db.Model):
    __tablename__ = 'course'
    courseID = db.Column(db.Integer, primary_key=True)
    courseName = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    totalSeats = db.Column(db.Integer, nullable=False)
    seatsTaken = db.Column(db.Integer, nullable=False)
    dates = db.Column(db.String(255), nullable=False)
    days = db.Column(db.String(255), nullable=False)
    timings = db.Column(db.String(255), nullable=False)
    active = db.Column(db.String(255), nullable=False)
    teacherID = db.Column(db.Integer, db.ForeignKey('teacher.teacherID'), nullable=False)

    teacher = db.relationship('Teacher', backref=db.backref('courses', lazy=True))

    def __repr__(self):
        return '<Course %r>' % self.courseID


class Teacher(db.Model):
    __tablename__ = 'teacher'
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
    __tablename__ = 'parent'
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
    __tablename__ = 'FAQ'
    faqID = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<FAQ %r>' % self.id
    
class Question(db.Model):
    __tablename__ = 'question'
    questionID = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(255), nullable=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.userID'), nullable=False)

    user = db.relationship('User', backref=db.backref('question', uselist=False))

    def __repr__(self):
        return '<FAQ %r>' % self.id

class Announcement(db.Model):
    __tablename__ = 'announcement'
    announcementID = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    courseID = db.Column(db.Integer, db.ForeignKey('course.courseID'), nullable=False)
    active = db.Column(db.String(255), nullable=True)
    expiration_date = db.Column(db.DateTime, nullable=True)  # New column for expiration datetime
    
    course = db.relationship('Course', backref=db.backref('announcement', lazy=True))

    def __repr__(self):
        return f'<Announcement {self.announcementID}>'
    
    @property
    def activated(self):
        if self.expiration_date is None:
            return True
        return datetime.utcnow() <= self.expiration_date


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/student-home')
def studentHome():
    # Check if the user is authenticated
    if 'user' in session:
        # Fetch user data from your database based on the Firebase UID
        user_email = session.get('user')
        student = User.query.filter_by(email=user_email).first()
        courses = student.enrolled_courses
        # Create an alias for the Announcement model to handle the join condition
        announcement_alias = aliased(Announcement)

        # Fetch announcements for the courses the student is enrolled in
        announcements = db.session.query(Announcement).join(
            announcement_alias,
            Announcement.courseID == announcement_alias.courseID
        ).filter(
            Announcement.courseID.in_(course.courseID for course in courses),
            Announcement.active == 1
        ).all()

        return render_template('student-home.html', student=student, courses=courses, announcements=announcements)
    
    else:
        return redirect('/')



@app.route('/student-settings')
def studentSettings():
    user_email = session.get('user')
    user = User.query.filter_by(email=user_email).first()
    return render_template('student-settings.html', user=user)

@app.route('/update-student', methods=['POST'])
def updateStudent():
    user_email = session.get('user')
    user = User.query.filter_by(email=user_email).first()
    pass
    
    if user:
        # Update user information from the form data
        user.first_name = request.form['first']
        user.last_name = request.form['last']
        user.email = request.form['email']
        user.age = int(request.form['selectbasic'])
        user.gender = request.form['radios']
        
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
    user_email = session.get('user')
    user = User.query.filter_by(email=user_email).first()
    teacher = Teacher.query.filter_by(teacherID=user.userID).first()
    courses = Course.query.join(Teacher).join(User).filter(Teacher.userID == user.userID).all()
    course_ids = [course.courseID for course in courses]
    announcements = Announcement.query.filter(Announcement.courseID.in_(course_ids),Announcement.active == 1).all()

    return render_template('teacher-home.html', teacher=teacher, courses=courses, announcements=announcements)



@app.route('/teacher-settings')
def teacherSettings():
    user_email = session.get('user')
    user = User.query.filter_by(email=user_email).first()
    teacher = Teacher.query.filter_by(teacherID=user.userID).first()
    return render_template('teacher-settings.html', teacher=teacher, user=user)

@app.route('/update-teacher', methods=['POST'])
def updateTeacher():
    user_email = session.get('user')
    user = User.query.filter_by(email=user_email).first()
    teacher = Teacher.query.filter_by(teacherID=user.userID).first()
    
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
        error_message = 'Incorrect password! Please try again!'
        return render_template('teacher-settings.html', teacher=teacher, error_message=error_message)
    
@app.route('/teacher-profile/<int:teacher_id>')
def teacher_profile(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    user_email = session.get('user')
    user = User.query.filter_by(email=user_email).first()
    return render_template('teacher-profile.html', teacher=teacher, user=user)

@app.route('/parent-home')
def parentHome():
    user_email = session.get('user')
    user = User.query.filter_by(email=user_email).first()
    return render_template('parent-home.html', user=user)

@app.route('/parent-settings')
def parentSettings():
    user_email = session.get('user')
    user = User.query.filter_by(email=user_email).first()
    return render_template('parent-settings.html', user=user)

@app.route('/sign-up', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        age = int(request.form['selectbasic'])
        gender = int(request.form['radios'])

        # Check if a user with the same username or email already exists
        existing_user = User.query.filter(
            (User.email == email)
        ).first()

        if existing_user:
            error_message = 'Username or email already exists. Please choose a different one.'
            return render_template('sign-up.html', error_message=error_message)

        # Create a new user and add it to the database
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            age=age,
            gender=gender
        )

        try:
            db.session.add(new_user)
            db.session.commit()

            # Create a new Firebase user
            auth.create_user_with_email_and_password(email, password)
            auth.sign_in_with_email_and_password(email, password)
            session['user'] = email
            user = User.query.filter_by(email=email).first()

            # Store the user ID in the session
            #session['user_id'] = new_user.userID
            login_user(user)

            new_teacher = Teacher(
                teacherID=new_user.userID,
                userID=new_user.userID,
                qualifications=" ",
                experience=" ",
                department=" ",
                status=" ",
            )

            db.session.add(new_teacher)
            db.session.commit()

            return redirect('/student-home')
        except Exception as e:
            print('There was an issue signing you up. Please try again later.')
            error_message = 'There was an issue signing you up. Please try again later.' + str(e)
            return render_template('sign-up.html', error_message=error_message)
    else:
        return render_template('sign-up.html')

@app.route('/log-in', methods=['GET', 'POST'])
def log_in():                  #WE CHANGED logIn to log_in ##########################3
    if request.method == 'POST':
        # Retrieve form data
        email = request.form['email']
        password = request.form['password']
        login_role = request.form['login_role']

        try:
            auth.sign_in_with_email_and_password(email, password)
            session['user'] = email
            user = User.query.filter_by(email=email).first()
            login_user(user)

            if login_role == 'student':
                return redirect('/student-home')
            elif login_role == 'teacher':
                return redirect('/teacher-home')
            elif login_role == 'parent':
                return redirect('/parent-home')
            else:
                error_message = 'Invalid login role. Please try again.'    

        except Exception as e:
            error_message = 'Invalid username or password. Please try again.' + str(e)
            print(error_message)
            return render_template('log-in.html', error_message=error_message)
    else:
        return render_template('log-in.html')


@app.route('/logout')
def logout():
    #logout_user()
    return redirect('/')  # Redirect to the main page after logging out


@app.route('/course-catalog')
def courseCatalog():
    courses = Course.query.all()
    user_email = session.get('user')
    user = User.query.filter_by(email=user_email).first()
    registered_course_ids = [course.courseID for course in user.enrolled_courses]
    return render_template('course-catalog.html', user=user, courses=courses, registered_course_ids=registered_course_ids)


@app.route('/create-class', methods=['GET', 'POST'])
def createClass():
    user_email = session.get('user')
    user = User.query.filter_by(email=user_email).first()
    teacher = Teacher.query.filter_by(teacherID=user.userID).first()
    if request.method == 'POST':
        # Retrieve form data
        courseName = request.form['courseName']
        description = request.form['description']
        section = request.form['section']
        totalSeats = int(request.form['totalSeats'])
        dates = request.form['dates']
        days = request.form['days']
        timings = request.form['timings']

        # Find the teacher by username
        #teacher = Teacher.query.join(User).filter(User.username == teacher_username).first()

        if not teacher:
            # If the teacher doesn't exist, you can choose to create a new teacher or show an error message.
            # For simplicity, let's assume the teacher must exist in the database.
            error_message = 'You do not have access to the teacher role. Please contact admin at bagdadihadi@gmail.com.'
            return render_template('create-class.html', error_message=error_message)

        # Create a new course and add it to the database
        new_course = Course(
            courseName=courseName,
            description=description,
            section=section,
            totalSeats=totalSeats,
            seatsTaken=0,
            dates=dates,
            days=days,
            timings=timings,
            teacher=teacher,  # Set the teacher object in the new course
            active=1
        )

        try:
            db.session.add(new_course)
            db.session.commit()
            return redirect('/teacher-home')  # Redirect the course catalog page after adding the class
        except Exception as e:
            error_message = 'There was an issue adding the class. Please try again later.'
            return render_template('create-class.html', error_message=error_message)
    else:
        return render_template('create-class.html')

@app.route('/faq-teacher', methods=['GET', 'POST'])
def faqTeacher():
    faq_entries = FAQ.query.all()
    user_email = session.get('user')
    user = User.query.filter_by(email=user_email).first()
    if request.method == 'POST':
        # Retrieve form data
        question = request.form['textarea']

        new_question = Question(
            query = question,
            userID = user.userID,
            answer = ""
        )

        try:
            db.session.add(new_question)
            db.session.commit()
            return redirect('/teacher-home')  # Redirect to home page
        except Exception as e:
            error_message = 'There was an issue sending the question. Please try again later.'
            return render_template('faq-teacher.html', faq_entries=faq_entries, error_message=error_message)
    else:
        return render_template('faq-teacher.html', faq_entries=faq_entries)
    

@app.route('/faq-student', methods=['GET', 'POST'])
def faqStudent():
    faq_entries = FAQ.query.all()
    user_email = session.get('user')
    user = User.query.filter_by(email=user_email).first()
    if request.method == 'POST':
        # Retrieve form data
        question = request.form['textarea']

        new_question = Question(
            query = question,
            userID = user.userID,
            answer = ""
        )

        try:
            db.session.add(new_question)
            db.session.commit()
            return redirect('/student-home')  # Redirect to home page
        except Exception as e:
            error_message = 'There was an issue sending the question. Please try again later.'
            return render_template('faq-student.html', faq_entries=faq_entries, error_message=error_message)
    else:
        return render_template('faq-student.html', faq_entries=faq_entries)

@app.route('/faq-parent', methods=['GET', 'POST'])
def faqParent():
    faq_entries = FAQ.query.all()
    return render_template('faq-parent.html', faq_entries=faq_entries)

@app.route('/about-us-student')
def aboutUsStudent():
    return render_template('about-us-student.html')

@app.route('/create-announcement', methods=['GET', 'POST'])
def create_announcement():
    # Fetch courses taught by the teacher
    user_email = session.get('user')
    user = User.query.filter_by(email=user_email).first()
    teacher = Teacher.query.filter_by(teacherID=user.userID).first()
    courses = Course.query.join(Teacher).join(User).filter(Teacher.userID == user.userID).all()

    if request.method == 'POST':
        course_id = int(request.form['course_id'])
        announcement_text = request.form['announcement_text']

        # Check if the teacher is the instructor of the selected course
        course = Course.query.get(course_id)
        if course.teacherID != teacher.teacherID:
            error_message = 'You are not authorized to create announcements for this course.'
            return render_template('create-announcement.html', user=user, courses=courses, error_message=error_message)

        # Create a new announcement and add it to the database
        new_announcement = Announcement(courseID=course_id, text=announcement_text, active=1)

        try:
            db.session.add(new_announcement)
            db.session.commit()
            return redirect('/teacher-home')  # Redirect to teacher's home page
        except Exception as e:
            error_message = 'There was an issue creating the announcement. Please try again later.'
            return render_template('create-announcement.html', user=user, courses=courses, error_message=error_message)

    else:
        return render_template('create-announcement.html', user=user, courses=courses)
    

@app.route('/edit-announcement/<int:announcement_id>', methods=['GET', 'POST'])
def edit_announcement(announcement_id):
    # Fetch the announcement to be updated
    announcement = Announcement.query.get(announcement_id)

    if not announcement:
        return "Announcement not found", 404

    # Get the teacher's ID
    user_email = session.get('user')
    user = User.query.filter_by(email=user_email).first()
    teacher = Teacher.query.filter_by(teacherID=user.userID).first()
    courses = Course.query.join(Teacher).join(User).filter(Teacher.userID == user.userID).all()

    # Check if the teacher is the instructor of the announcement's course
    if announcement.course.teacherID != teacher.teacherID:
        return "You are not authorized to update this announcement", 403

    if request.method == 'POST':
        # Update announcement details from the form data
        announcement.courseID = int(request.form['course_id'])
        announcement.text = request.form['announcement_text']

        # Check if the "disable_announcement" checkbox was selected
        if request.form.get('disable_announcement'):
            announcement.active = 0
        else:
            announcement.active = 1

        try:
            db.session.commit()
            return redirect('/teacher-home')  # Redirect to teacher's home page
        except Exception as e:
            error_message = 'There was an issue updating the announcement. Please try again later.'
            return render_template('edit-announcement.html', user=user, courses=courses, announcement=announcement, error_message=error_message)
        
    else:
        return render_template('edit-announcement.html', user=user, courses=courses, announcement=announcement)


@app.route('/deactivate-announcement/<int:announcement_id>', methods=['POST'])
def deactivate_announcement(announcement_id):
    announcement = Announcement.query.get(announcement_id)

    if not announcement:
        return "Announcement not found", 404

    # Check if the teacher is the instructor of the announcement's course
    user_email = session.get('user')
    user = User.query.filter_by(email=user_email).first()
    teacher = Teacher.query.filter_by(teacherID=user.userID).first()
    if announcement.course.teacherID != teacher.teacherID:
        return "You are not authorized to deactivate this announcement", 403

    announcement.active = 0  # Deactivate the announcement
    db.session.commit()

    return redirect('/teacher-home')  # Redirect to teacher's home page



@app.route('/about-us-teacher')
def aboutUsTeacher():
    return render_template('about-us-teacher.html')

@app.route('/about-us-parent')
def aboutUsParent():
    return render_template('about-us-parent.html')


@app.route('/register-course/<int:course_id>', methods=['POST'])  # Ensure the user is logged in before registering
def register_course(course_id):
    course = Course.query.get(course_id)

    if not course:
        return "Course not found", 404  # Handle the case where the course doesn't exist

    if current_user in course.students:
        return "Already registered for this course", 400  # Handle the case where the user is already registered

    course.students.append(current_user)
    course.seatsTaken += 1  # Increment seatsTaken by one
    db.session.commit()

    return redirect('/student-home')  # Redirect to the student's home page

@app.route('/delete_course/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    course = Course.query.get(course_id)

    if not course:
        return "Course not found", 404

    if current_user != course.teacher.user:
        return "You don't have permission to delete this course", 403

    course.active=0
    db.session.commit()

    return redirect('/teacher-home')  # Redirect to the teacher's home page




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

if __name__ == '__main__':
    # Create all tables if they don't exist
    if not os.path.exists('data.db'):
        db.create_all()

    app.run(debug=True, port=8080)

