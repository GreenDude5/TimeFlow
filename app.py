from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Konfiguracja bazy danych
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'tajny-klucz-123'

db = SQLAlchemy(app)

# Model Zadania
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    priority = db.Column(db.Integer, default=3)
    due_date = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed': self.completed,
            'created_at': self.created_at.isoformat()
        }

# Strona główna
@app.route('/')
def index():
    tasks = Task.query.order_by(Task.priority, Task.due_date).all()
    return render_template('index.html', tasks=tasks)

# Dodawanie nowego zadania
@app.route('/add_task', methods=['POST'])
def add_task():
    title = request.form.get('title')
    
    if title:
        new_task = Task(title=title)
        db.session.add(new_task)
        db.session.commit()
    
    return redirect(url_for('index'))

# Usuwanie zadania - NOWA FUNKCJA!
@app.route('/delete_task/<int:task_id>', methods=['DELETE', 'POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return '', 204  # Pusta odpowiedź - sukces

# Oznaczanie jako zrobione/niezrobione - NOWA FUNKCJA!
@app.route('/toggle_task/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed  # Zmiana stanu
    db.session.commit()
    return redirect(url_for('index'))

# API do pobierania zadań
@app.route('/api/tasks')
def api_tasks():
    tasks = Task.query.order_by(Task.priority, Task.due_date).all()
    return jsonify([task.to_dict() for task in tasks])

# Uruchamiamy aplikację
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)