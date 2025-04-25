from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os, csv, sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'group10'

DATABASE = 'users.db'

# --- Initialize Database ---
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Create a user table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Create a daily record table
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            weight REAL,
            breakfast TEXT,
            lunch TEXT,
            dinner TEXT,
            exercise TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

init_db()

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict(flat=False)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"record_{now}.csv"

    os.makedirs('uploads', exist_ok=True)
    with open(os.path.join('uploads', filename), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Key', 'Value'])
        for key, values in data.items():
            for value in values:
                writer.writerow([key, value])

    return redirect(url_for('index'))


@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']

    session['temp_user'] = {
        'username': username,
        'password': password
    }

    return 'Signup success!'


@app.route('/signin', methods=['POST'])
def signin():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        session['user'] = username
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid username or password!'})



@app.route('/basicinfo', methods=['POST'])
def basicinfo():
    temp_user = session.get('temp_user')
    if not temp_user:
        return jsonify({'status': 'error', 'message': 'Registration expired or incomplete'})

    username = temp_user['username']
    password = temp_user['password']
    age = request.form.get('age')
    gender = request.form.get('gender')
    height = request.form.get('height')
    current_weight = request.form.get('current_weight')
    target_weight = request.form.get('target_weight')
    avatar = request.form.get('avatar')

    if not all([age, gender, height, current_weight, target_weight, avatar]):
        return jsonify({'status': 'error', 'message': 'All fields required'})

    try:
        height_m = float(height) / 100
        weight_reg = float(current_weight)
        bmi = round(weight_reg / (height_m ** 2), 2)
    except:
        return jsonify({'status': 'error', 'message': 'Invalid height or weight format'})

    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        
        c.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in c.fetchall()]
        required_fields = [
            'age', 'gender', 'height', 'current_weight', 'target_weight',
            'avatar', 'weight_reg', 'bmi_reg', 'bmi_now', 'register_date'
        ]
        for field in required_fields:
            if field not in columns:
                c.execute(f"ALTER TABLE users ADD COLUMN {field} TEXT")

        # register data
        register_date = datetime.now().strftime("%Y/%m/%d")

        # info
        c.execute("""
            INSERT INTO users (
                username, password, age, gender, height, current_weight,
                target_weight, avatar, weight_reg, bmi_reg, bmi_now, register_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username, password, age, gender, height, current_weight,
            target_weight, avatar, weight_reg, bmi, bmi, register_date
        ))

        # get user_id
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = c.fetchone()[0]

        # input daily_records
        c.execute("""
            INSERT INTO daily_records (user_id, date, weight)
            VALUES (?, ?, ?)
        """, (user_id, register_date, weight_reg))

        conn.commit()
        conn.close()

        session.pop('temp_user', None)
        session['user'] = username
        return 'success'

    except sqlite3.IntegrityError:
        return jsonify({'status': 'error', 'message': 'Username already exists!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})



@app.route('/profile_data')
def profile_data():
    username = session.get('user')
    if not username:
        return jsonify({'status': 'error', 'message': 'Not logged in'})

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # get info
    c.execute("""
        SELECT id, username, avatar, age, gender, height, weight_reg, target_weight, bmi_reg, bmi_now, register_date
        FROM users WHERE username = ?
    """, (username,))
    user = c.fetchone()

    if not user:
        conn.close()
        return jsonify({'status': 'error', 'message': 'User not found'})

    user_id = user[0]

    # current weight
    c.execute("""
        SELECT weight FROM daily_records
        WHERE user_id = ?
        ORDER BY date DESC LIMIT 1
    """, (user_id,))
    latest_weight_row = c.fetchone()
    current_weight = latest_weight_row[0] if latest_weight_row else ''

    conn.close()

    data = {
        'username': user[1],
        'avatar': user[2] or '',
        'age': user[3] or '',
        'gender': user[4] or '',
        'height': user[5] or '',
        'weight_reg': user[6] or '',
        'current_weight': current_weight,
        'target_weight': user[7] or '',
        'bmi_reg': user[8] or '',
        'bmi_now': user[9] or '',
        'register_date': user[10] or ''
    }
    return jsonify({'status': 'success', 'data': data})

@app.route('/add_record', methods=['POST'])
def add_record():
    username = session.get('user')
    if not username:
        return jsonify({'status': 'error', 'message': 'Not logged in'})

    date = request.form.get('date')
    weight = request.form.get('weight')
    breakfast = request.form.get('breakfast')
    lunch = request.form.get('lunch')
    dinner = request.form.get('dinner')
    exercise = request.form.get('exercise')

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # get ID
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_row = c.fetchone()
    if not user_row:
        return jsonify({'status': 'error', 'message': 'User not found'})
    user_id = user_row[0]

    # check
    c.execute("SELECT id FROM daily_records WHERE user_id = ? AND date = ?", (user_id, date))
    existing = c.fetchone()

    if existing:
        return jsonify({'status': 'exists', 'message': 'Record for this date already exists.'})

    try:
        c.execute("""
            INSERT INTO daily_records (user_id, date, weight, breakfast, lunch, dinner, exercise)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, date, weight, breakfast, lunch, dinner, exercise))

        conn.commit()
        return jsonify({'status': 'success', 'message': 'Record saved'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        conn.close()

@app.route('/update_record', methods=['POST'])
def update_record():
    username = session.get('user')
    if not username:
        return jsonify({'status': 'error', 'message': 'Not logged in'})

    date = request.form.get('date')
    weight = request.form.get('weight')
    breakfast = request.form.get('breakfast')
    lunch = request.form.get('lunch')
    dinner = request.form.get('dinner')
    exercise = request.form.get('exercise')

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # get user_id
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_row = c.fetchone()
    if not user_row:
        return jsonify({'status': 'error', 'message': 'User not found'})
    user_id = user_row[0]

    try:
        c.execute("""
            UPDATE daily_records SET weight=?, breakfast=?, lunch=?, dinner=?, exercise=?
            WHERE user_id = ? AND date = ?
        """, (weight, breakfast, lunch, dinner, exercise, user_id, date))

        conn.commit()
        return jsonify({'status': 'success', 'message': 'Record updated'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        conn.close()


@app.route('/records')
def records():
    username = session.get('user')
    if not username:
        return jsonify({'status': 'error', 'message': 'Not logged in'})

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_row = c.fetchone()

    if not user_row:
        return jsonify({'status': 'error', 'message': 'User not found'})

    user_id = user_row[0]
    c.execute("""
        SELECT date, weight, breakfast, lunch, dinner, exercise
        FROM daily_records
        WHERE user_id = ?
        ORDER BY date DESC
    """, (user_id,))
    records = c.fetchall()
    conn.close()

    return jsonify({
        'status': 'success',
        'data': [
            {
                'date': row[0],
                'weight': row[1],
                'breakfast': row[2],
                'lunch': row[3],
                'dinner': row[4],
                'exercise': row[5],
            } for row in records
        ]
    })

@app.route('/weight_data')
def weight_data():
    username = session.get('user')
    if not username:
        return jsonify({'status': 'error', 'message': 'Not logged in'})

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_row = c.fetchone()
    if not user_row:
        return jsonify({'status': 'error', 'message': 'User not found'})

    user_id = user_row[0]
    c.execute("SELECT date, weight FROM daily_records WHERE user_id = ? ORDER BY date ASC", (user_id,))
    rows = c.fetchall()
    conn.close()

    data = [{'date': row[0], 'weight': row[1]} for row in rows]
    return jsonify({'status': 'success', 'data': data})


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
