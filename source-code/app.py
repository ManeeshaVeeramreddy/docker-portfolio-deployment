import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='static', static_url_path='')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')


def get_db():
    """Open a new SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the todos table if it doesn't exist."""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    """Serve the static frontend index.html."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/todos', methods=['GET'])
def get_todos():
    """Return all todos ordered by creation date (newest first)."""
    conn = get_db()
    rows = conn.execute(
        'SELECT id, title, created_at FROM todos ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    todos = [dict(row) for row in rows]
    return jsonify(todos)


@app.route('/api/todos', methods=['POST'])
def add_todo():
    """Add a new todo."""
    data = request.get_json()
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    conn = get_db()
    cursor = conn.execute(
        'INSERT INTO todos (title) VALUES (?)', (title,)
    )
    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()

    return jsonify({'id': todo_id, 'title': title}), 201


@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo by ID."""
    conn = get_db()
    cursor = conn.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify({'message': 'Deleted'}), 200


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
