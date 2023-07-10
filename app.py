from flask import Flask, render_template

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run()
