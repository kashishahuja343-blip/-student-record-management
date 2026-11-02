
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = "students.db"


# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create students table
def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)

    conn.commit()
    conn.close()


# GET: Retrieve all students
@app.route("/students", methods=["GET"])
def get_students():
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM students ORDER BY id"
    ).fetchall()
    conn.close()

    students = [dict(row) for row in rows]
    return jsonify(students), 200


# GET: Retrieve one student by ID
@app.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    conn = get_db_connection()

    row = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    conn.close()

    if row is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(row)), 200


# POST: Add a new student
@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON object required"}), 400

    name = data.get("name")
    department = data.get("department")
    email = data.get("email")

    if not all(
        isinstance(value, str) and value.strip()
        for value in (name, department, email)
    ):
        return jsonify({
            "error": "Name, department, and email are required"
        }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """INSERT INTO students (name, department, email)
               VALUES (?, ?, ?)""",
            (name.strip(), department.strip(), email.strip())
        )
        conn.commit()

        student_id = cursor.lastrowid

        row = conn.execute(
            "SELECT * FROM students WHERE id = ?",
            (student_id,)
        ).fetchone()

        return jsonify(dict(row)), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Email already exists"
        }), 409

    finally:
        conn.close()


# PUT: Update an existing student
@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON object required"}), 400

    name = data.get("name")
    department = data.get("department")
    email = data.get("email")

    if not all(
        isinstance(value, str) and value.strip()
        for value in (name, department, email)
    ):
        return jsonify({
            "error": "Name, department, and email are required"
        }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """UPDATE students
               SET name = ?, department = ?, email = ?
               WHERE id = ?""",
            (
                name.strip(),
                department.strip(),
                email.strip(),
                student_id
            )
        )

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Student not found"
            }), 404

        conn.commit()

        row = conn.execute(
            "SELECT * FROM students WHERE id = ?",
            (student_id,)
        ).fetchone()

        return jsonify(dict(row)), 200

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Email already exists"
        }), 409

    finally:
        conn.close()


# DELETE: Delete a student
@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    conn = get_db_connection()

    try:
        cursor = conn.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Student not found"
            }), 404

        conn.commit()

        return jsonify({
            "message": "Student deleted successfully"
        }), 200

    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
