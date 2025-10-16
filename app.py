from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os


app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['SQLALCHEMY_SECRET_KEY'] = 'klucz_tymaczoswy'


db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    priority = db.Column(db.Integer, default=5)
    due_date = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now())

    def to_dict(self):
        return {
            'id' : self.id,
            'title' : self.title,
            'description' : self.description,
            'priority' : self.priority,
            'due_date' : self.due_date,
            'completed' : self.completed,
            'created_at' : self.created_at
        }


@app.route('/')
def index():
    tasks = Task.query.order_by(Task.priority, Task.due_date).all()
    return render_template('index.html', tasks=tasks)


@app.route('/add_task', methods=['POST'])
def add_task():
    title = request.form.get('title')

    if(title):
        new_task = Task(title=title)
        db.session.add(new_task)
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/api/tasks')
def api_tasks():
    tasks = Task.query.order_by(Task.priority, Task.due_date).all()
    return jsonify([task.to_dict() for task in tasks])


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)