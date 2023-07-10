from flask import Flask, render_template
import sqlite3
import sys

app = Flask(__name__)

# Connect to the database
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

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

@app.route('/faq')
def faq():
    # Fetch data from the faq table
    cursor.execute('SELECT question, answer FROM faq')
    faq_data = cursor.fetchall()

    # Close the database connection
    cursor.close()
    conn.close()

    return render_template('faq.html', faq_data=faq_data)


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
