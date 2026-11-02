import streamlit as st
import sqlite3

DATABASE = "students.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL,
            department TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

st.title("Student Management System")
menu = ["Add Student", "View Students", "Delete Student"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Student":
    st.subheader("Add New Student")
    name = st.text_input("Name")
    roll_no = st.text_input("Roll No")
    dept = st.text_input("Department")
    if st.button("Add"):
        if name and roll_no and dept:
            conn = get_db_connection()
            conn.execute("INSERT INTO students (name, roll_no, department) VALUES (?,?,?)", (name, roll_no, dept))
            conn.commit()
            conn.close()
            st.success(f"Student {name} Added!")
        else:
            st.error("Fill all fields")

elif choice == "View Students":
    st.subheader("All Students")
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    if students:
        for s in students:
            st.write(f"ID: {s['id']} | Name: {s['name']} | Roll: {s['roll_no']} | Dept: {s['department']}")
    else:
        st.info("No students yet")

elif choice == "Delete Student":
    st.subheader("Delete Student")
    id_to_del = st.number_input("Enter Student ID to delete", min_value=1, step=1)
    if st.button("Delete"):
        conn = get_db_connection()
        conn.execute("DELETE FROM students WHERE id=?", (id_to_del,))
        conn.commit()
        conn.close()
        st.warning(f"Student ID {id_to_del} Deleted if existed")