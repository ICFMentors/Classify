from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    completion_time = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime)
    category = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    grade = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Student %r>' % self.id


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/students', methods=['POST', 'GET'])
def students():
    if request.method == 'POST':
        student_name = request.form['name']
        student_grade = request.form['grade']
        new_student = Student(name=student_name, grade=student_grade)

        try:
            db.session.add(new_student)
            db.session.commit()
            return redirect('/students')
        except:
            return 'There was an issue adding the student'
    else:
        students = Student.query.all()
        return render_template('students.html', students=students)



@app.route('/tasks', methods=['POST', 'GET'])
def tasks():
    if request.method == 'POST':
        task_content = request.form['content']
        due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%dT%H:%M')
        task_category = request.form['category']
        new_task = Todo(content=task_content, due_date=due_date, category=task_category)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/tasks')
        except:
            return 'There was an issue adding your task'
    else:
        tasks = Todo.query.filter_by(completed=False).order_by(Todo.due_date).all()
        completed_tasks = Todo.query.filter_by(completed=True).order_by(Todo.completion_time).all()
        return render_template('tasks.html', tasks=tasks, completed_tasks=completed_tasks)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/tasks')
    except:
        return 'There was a problem deleting that task'


@app.route('/clear_completed')
def clear_completed():
    try:
        completed_tasks = Todo.query.filter_by(completed=True).all()
        for task in completed_tasks:
            db.session.delete(task)
        db.session.commit()
        return redirect('/tasks')
    except:
        return 'There was a problem clearing completed tasks'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']
        task.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%dT%H:%M')
        task_category = request.form['category']
        task.completed = 'completed' in request.form
        task.completion_time = datetime.utcnow() if task.completed else None

        try:
            db.session.commit()
            return redirect('/tasks')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)



@app.route('/complete/<int:id>', methods=['POST'])
def complete(id):
    task = Todo.query.get_or_404(id)
    task.completed = True
    task.completion_time = datetime.utcnow()

    try:
        db.session.commit()
        return redirect('/tasks')
    except:
        return 'There was an issue completing the task'

import os
if not os.path.exists('test.db'):  # Check if the database file doesn't exist
    db.create_all()

if __name__ == '__main__':
    # os.remove('test.db')  # Delete the existing database file
    app.run(debug=True)
