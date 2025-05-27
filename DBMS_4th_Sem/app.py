from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL config
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Aiml@2026',
    'database': 'college'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'teacher' not in session:
        return redirect('/login')

    selected_sem = request.form.get('semester')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if selected_sem:
        cursor.execute("""SELECT * FROM student WHERE sem = %s ORDER BY CAST(RIGHT(usn, 3) AS UNSIGNED) ASC""", (selected_sem,))
    else:
        cursor.execute("SELECT * FROM student ORDER BY CAST(RIGHT(usn, 3) AS UNSIGNED) ASC")
    
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('dashboard.html', students=students, selected_sem=selected_sem, semesters=list(range(1, 9)))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM teacher WHERE username = %s", (username,))
        teacher = cursor.fetchone()
        cursor.close()
        conn.close()
        if teacher and teacher['password'] == password:
            session['teacher'] = username
            return redirect('/')
        return 'Invalid username or password'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('teacher', None)
    return redirect('/login')

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if 'teacher' not in session:
        return redirect('/login')
    if request.method == 'POST':
        data = (
            request.form['name'],
            request.form['usn'],
            int(request.form['sem']),
            request.form['subject'],
            int(request.form['marks_test1']),
            int(request.form['marks_test2']),
            int(request.form['marks_test3'])
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO student (name, usn, sem, subject, marks_test1, marks_test2, marks_test3) VALUES (%s, %s, %s, %s, %s, %s, %s)", data)
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/')
    return render_template('form.html', action='Add', student=None)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if 'teacher' not in session:
        return redirect('/login')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM student WHERE id = %s", (id,))
    student = cursor.fetchone()
    if request.method == 'POST':
        data = (
            request.form['name'],
            request.form['usn'],
            int(request.form['sem']),
            request.form['subject'],
            int(request.form['marks_test1']),
            int(request.form['marks_test2']),
            int(request.form['marks_test3']),
            id
        )
        cursor.execute("UPDATE student SET name=%s, usn=%s, sem=%s, subject=%s, marks_test1=%s, marks_test2=%s, marks_test3=%s WHERE id=%s", data)
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/')
    cursor.close()
    conn.close()
    return render_template('form.html', action='Edit', student=student)

@app.route('/delete/<int:id>')
def delete_student(id):
    if 'teacher' not in session:
        return redirect('/login')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
