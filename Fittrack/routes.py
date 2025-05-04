from flask import Flask, request, jsonify, session, render_template, redirect, url_for, send_from_directory
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, DailyRecord, DailyExercise
from .models import FriendRequest
from sqlalchemy import or_


DATABASE = 'users.db'

def register_routes(app):

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


    @app.route('/signin', methods=['POST'])
    def signin():
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.hashed_password, password):
            session['user'] = user.username
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid username or password!'})


    @app.route('/signup', methods=['POST'])
    def signup():
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # check
        if User.query.filter((User.username == username) | (User.email == email)).first():
            return "Username or email already exists!", 400

        # Temporarily store account information
        session['temp_user'] = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password)
        }

        return "success"



    @app.route('/basicinfo', methods=['POST'])
    def basicinfo():
        temp_user = session.get('temp_user')
        if not temp_user:
            return jsonify({'status': 'error', 'message': 'Registration expired or incomplete'})

        # basic info
        username = temp_user['username']
        email = temp_user['email']
        hashed_password = temp_user['password']

        birthday_str = request.form.get('birthday')
        gender = request.form.get('gender')
        height = request.form.get('height')
        current_weight = request.form.get('current_weight')
        target_weight = request.form.get('target_weight')
        avatar = request.form.get('avatar')

        target_days = request.form.get('target_weight_time_days')  # optional
        exercise_weekly = request.form.get('target_exercise_time_per_week')  # optional
        exercise_total_days = request.form.get('target_exercise_timeframe_days')  # optional

        if not all([birthday_str, gender, height, current_weight, target_weight, avatar]):
            return jsonify({'status': 'error', 'message': 'All fields required'})

        # calculate age
        try:
            birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
            today = datetime.today().date()
            age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
        except:
            return jsonify({'status': 'error', 'message': 'Invalid birthday format'})

        # BMI
        try:
            height_m = float(height) / 100
            weight_reg = float(current_weight)
            bmi = round(weight_reg / (height_m ** 2), 2)
        except:
            return jsonify({'status': 'error', 'message': 'Invalid height or weight format'})

        # Create users and submit to database
        try:
            register_date = datetime.now().strftime("%Y-%m-%d")

            user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                birthday=birthday_str,
                age=age,
                gender=gender,
                height=float(height),
                current_weight=float(weight_reg),
                target_weight=float(target_weight),
                avatar=avatar,
                weight_reg=weight_reg,
                bmi_reg=bmi,
                bmi_now=bmi,
                register_date=register_date,

                # Target field assignment (can be None) If none, it will affect the analysis, but not the registration.
                target_weight_time_days=int(target_days) if target_days else None,
                target_exercise_time_per_week=int(exercise_weekly) if exercise_weekly else None,
                target_exercise_timeframe_days=int(exercise_total_days) if exercise_total_days else None
            )

            db.session.add(user)
            db.session.commit()

            # Create a new record
            record = DailyRecord(
                user_id=user.user_id,
                date=datetime.today().date(),
                weight=weight_reg
            )
            db.session.add(record)
            db.session.commit()

            session.pop('temp_user', None)
            session['user'] = username
            return 'success'

        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)})




    @app.route('/profile_data')
    def profile_data():
        username = session.get('user')
        if not username:
            return jsonify({'status': 'error', 'message': 'Not logged in'})

        # SQLAlchemy
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'})

        # Get the latest weight record
        latest_record = (
            DailyRecord.query
            .filter_by(user_id=user.user_id)
            .order_by(DailyRecord.date.desc())
            .first()
        )
        current_weight = latest_record.weight if latest_record else ""

        data = {
            'username': user.username,
            'avatar': user.avatar or '',
            'birthday': user.birthday or '',
            'age': user.age or '',
            'gender': user.gender or '',
            'height': user.height or '',
            'weight_reg': user.weight_reg or '',
            'current_weight': current_weight,
            'target_weight': user.target_weight or '',
            'bmi_reg': user.bmi_reg or '',
            'bmi_now': user.bmi_now or '',
            'register_date': user.register_date or '',
            'target_weight_time_days': user.target_weight_time_days or '',
            'target_exercise_time_per_week': user.target_exercise_time_per_week or '',
            'target_exercise_timeframe_days': user.target_exercise_timeframe_days or ''
        }

        print("[DEBUG] user.weight_reg =", user.weight_reg)


        return jsonify({'status': 'success', 'data': data})

    @app.route('/add_record', methods=['POST'])
    def add_record():
        username = session.get('user')
        if not username:
            return jsonify({'status': 'error', 'message': 'Not logged in'})

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'})

        
        date_str = request.form.get('date')
        weight = request.form.get('weight')
        breakfast = request.form.get('breakfast')
        lunch = request.form.get('lunch')
        dinner = request.form.get('dinner')
        exercise_combined = request.form.get('exercise')  # e.g. "run (moderate); swim (light)"

        try:
            record_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            # Check whether it already exists
            existing = DailyRecord.query.filter_by(user_id=user.user_id, date=record_date).first()
            if existing:
                return jsonify({'status': 'exists', 'message': 'Record already exists'})

            # Save daily_record main table
            record = DailyRecord(
                user_id=user.user_id,
                date=record_date,
                weight=float(weight),
                breakfast=breakfast,
                lunch=lunch,
                dinner=dinner
            )
            db.session.add(record)
            db.session.commit()  # get record.record_id

            #  DailyExercise
            if exercise_combined:
                entries = exercise_combined.split(";")
                for entry in entries:
                    entry = entry.strip()
                    if not entry:
                        continue
                    print("[DEBUG] Raw entry received:", entry) 
                    try:
                        name_part, rest = entry.split("(", 1)
                        name = name_part.strip()
                        rest = rest.replace(")", "").strip()

                        duration_str, intensity = [r.strip() for r in rest.split(",")]
                        duration = int(duration_str.replace("min", "").strip())

                        print(f"[DEBUG] Saving Exercise - Name: {name}, Duration: {duration}, Intensity: {intensity}")  

                        exercise = DailyExercise(
                            record_id=record.record_id,
                            exercise_type=name,
                            exercise_duration_minutes=duration,
                            exercise_intensity=intensity
                        )
                        db.session.add(exercise)
                    except Exception as e:
                        print(f"[WARN] Failed to parse exercise entry: {entry}", e)





            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Record saved'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)})

    @app.route('/update_record', methods=['POST'])
    def update_record():
        username = session.get('user')
        if not username:
            return jsonify({'status': 'error', 'message': 'Not logged in'})

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'})

        date_str = request.form.get('date')
        weight = request.form.get('weight')
        breakfast = request.form.get('breakfast')
        lunch = request.form.get('lunch')
        dinner = request.form.get('dinner')
        exercise = request.form.get('exercise')

        try:
            record_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            # get record
            record = DailyRecord.query.filter_by(user_id=user.user_id, date=record_date).first()
            if not record:
                return jsonify({'status': 'error', 'message': 'Record not found'})

            # update
            record.weight = float(weight)
            record.breakfast = breakfast
            record.lunch = lunch
            record.dinner = dinner

            # Use record_id to delete all exercise records of the day
            old_exercises = DailyExercise.query.filter_by(record_id=record.record_id).all()
            for old in old_exercises:
                db.session.delete(old)

            # Insert a new exercise record
            if exercise:
                entries = exercise.split(";")
                for entry in entries:
                    entry = entry.strip()
                    if not entry:
                        continue
                    try:
                        name_part, rest = entry.split("(", 1)
                        name = name_part.strip()
                        rest = rest.replace(")", "").strip()
                        duration_str, intensity = [r.strip() for r in rest.split(",")]
                        duration = int(duration_str.replace("min", "").strip())

                        new_exercise = DailyExercise(
                            record_id=record.record_id,
                            exercise_type=name,
                            exercise_duration_minutes=duration,
                            exercise_intensity=intensity
                        )
                        db.session.add(new_exercise)
                    except Exception as e:
                        print(f"[WARN] Failed to parse exercise entry: {entry}", e)

            # Synchronous registration of the same-day weight
            try:
                reg_date_obj = datetime.strptime(user.register_date, "%Y-%m-%d").date()
                if record_date == reg_date_obj:
                    height_m = user.height / 100
                    bmi = round(float(weight) / (height_m ** 2), 2)
                    user.weight_reg = float(weight)
                    user.bmi_reg = bmi
                    user.bmi_now = bmi
            except Exception as e:
                print("[WARN] BMI sync failed:", e)

            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Record updated'})

        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)})



    @app.route('/records')
    def records():
        username = session.get('user')
        if not username:
            return jsonify({'status': 'error', 'message': 'Not logged in'})

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'})

        record_list = DailyRecord.query.filter_by(user_id=user.user_id)\
            .order_by(DailyRecord.date.desc()).all()

        return jsonify({
            'status': 'success',
            'data': [
                {
                    'date': r.date.strftime("%Y-%m-%d"),
                    'weight': r.weight,
                    'breakfast': r.breakfast,
                    'lunch': r.lunch,
                    'dinner': r.dinner,
                    'exercise': "; ".join(
                        f"{e.exercise_type} ({e.exercise_duration_minutes}min, {e.exercise_intensity})"
                        for e in DailyExercise.query.filter_by(record_id=r.record_id).all()
                    )
                } for r in record_list
            ]
        })


    @app.route('/weight_data')
    def weight_data():
        username = session.get('user')
        if not username:
            return jsonify({'status': 'error', 'message': 'Not logged in'})

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'})

        records = (
            DailyRecord.query
            .filter_by(user_id=user.user_id)
            .order_by(DailyRecord.date.asc())
            .all()
        )

        data = [
            {
                'date': r.date.strftime("%Y-%m-%d"),
                'weight': r.weight
            } for r in records
        ]

        return jsonify({'status': 'success', 'data': data})



    @app.route('/update_profile_fields', methods=['POST'])
    def update_profile_fields():
        username = session.get('user')
        if not username:
            return jsonify({'status': 'error', 'message': 'Not logged in'})

        data = request.get_json(force=True)

        birthday_str = data.get('birthday', '').strip()
        gender = data.get('gender', '').strip()
        height = data.get('height')
        weight_reg = data.get('weight_reg')
        target_weight = data.get('target_weight')
        target_weight_time_days = data.get('target_weight_time_days')
        target_exercise_time_per_week = data.get('target_exercise_time_per_week')
        target_exercise_timeframe_days = data.get('target_exercise_timeframe_days')

        # debug 
        debug_info = {
            'raw_data': data,
            'birthday': birthday_str,
            'gender': gender,
            'height': height,
            'weight_reg': weight_reg,
            'target_weight': target_weight,
            'target_weight_time_days': target_weight_time_days,
            'target_exercise_time_per_week': target_exercise_time_per_week,
            'target_exercise_timeframe_days': target_exercise_timeframe_days
        }

        # check
        if not birthday_str:
            return jsonify({'status': 'error', 'message': 'Birthday cannot be empty.', 'debug': debug_info})
        if height in [None, ''] or weight_reg in [None, ''] or target_weight in [None, '']:
            return jsonify({'status': 'error', 'message': 'Missing numeric fields', 'debug': debug_info})

        try:
            birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
            today = datetime.today().date()
            age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

            height_val = float(height)
            weight_val = float(weight_reg)
            target_weight_val = float(target_weight)

            height_m = height_val / 100
            bmi = round(weight_val / (height_m ** 2), 2)

            user = User.query.filter_by(username=username).first()
            if not user:
                return jsonify({'status': 'error', 'message': 'User not found', 'debug': debug_info})

            # input
            user.birthday = birthday_str
            user.gender = gender
            user.height = float(height_val)
            user.weight_reg = float(weight_val)
            user.target_weight = target_weight_val
            user.age = age
            user.bmi_reg = bmi
            user.bmi_now = bmi

            if target_weight_time_days not in [None, ""]:
                user.target_weight_time_days = int(target_weight_time_days)
            if target_exercise_time_per_week not in [None, ""]:
                user.target_exercise_time_per_week = int(target_exercise_time_per_week)
            if target_exercise_timeframe_days not in [None, ""]:
                user.target_exercise_timeframe_days = int(target_exercise_timeframe_days)

            # Synchronized registration day weight
            try:
                reg_date_obj = datetime.strptime(user.register_date, "%Y-%m-%d").date()
                reg_record = DailyRecord.query.filter_by(user_id=user.user_id, date=reg_date_obj).first()
                if reg_record:
                    reg_record.weight = user.weight_reg
                    db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("Failed to sync reg weight to daily_record:", e)

            db.session.commit()

            return jsonify({'status': 'success', 'age': age, 'bmi': bmi})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e), 'debug': debug_info})


    @app.route("/history")
    def view_history():
        return send_from_directory("static/html", "history.html")

    @app.route('/get_today_record')
    def get_today_record():
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'Not logged in'}), 401

        today = date.today()

        record = DailyRecord.query.filter_by(user_id=user_id, date=today).first()
        if not record:
            return jsonify({'status': 'empty'})  # No record today

        exercises = DailyExercise.query.filter_by(record_id=record.record_id).all()
        exercise_data = [
            {
                'type': ex.exercise_type,
                'duration': ex.exercise_duration_minutes,
                'intensity': ex.exercise_intensity
            }
            for ex in exercises
        ]

        return jsonify({
            'status': 'success',
            'data': {
                'weight': record.weight,
                'breakfast': record.breakfast,
                'lunch': record.lunch,
                'dinner': record.dinner,
                'exercises': exercise_data
            }
        })


    @app.route('/record_details/<date>')
    def get_record_details(date):
        if 'user' not in session:
            return jsonify({"status": "error", "message": "User not logged in"}), 401

        try:
            user = User.query.filter_by(username=session['user']).first()
            if not user:
                return jsonify({"status": "error", "message": "User not found"}), 404

            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
            record = DailyRecord.query.filter_by(user_id=user.user_id, date=parsed_date).first()
            if not record:
                return jsonify({"status": "empty", "message": "No record for selected date"})

            # Extract all records of the day
            exercises = DailyExercise.query.filter_by(record_id=record.record_id).all()

            # Debug 
            print(f"[DEBUG] user_id={user.user_id}, date={parsed_date}, record_id={record.record_id}")
            for ex in exercises:
                print(f"[DEBUG] Exercise - type: {ex.exercise_type}, duration: {ex.exercise_duration_minutes}, intensity: {ex.exercise_intensity}")

            # Format and return
            exercise_data = [{
                "type": ex.exercise_type,
                "duration": ex.exercise_duration_minutes,
                "intensity": ex.exercise_intensity
            } for ex in exercises]

            return jsonify({
                "status": "success",
                "data": {
                    "weight": record.weight,
                    "breakfast": record.breakfast or "N/A",
                    "lunch": record.lunch or "N/A",
                    "dinner": record.dinner or "N/A",
                    "exercises": exercise_data
                }
            })

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    # Return all dates for calendar annotation
    @app.route('/record_dates')
    def get_record_dates():
        if 'user' not in session:
            return jsonify({'status': 'error', 'message': 'Not logged in'}), 401

        user = User.query.filter_by(username=session['user']).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        records = DailyRecord.query.filter_by(user_id=user.user_id).all()
        date_list = [r.date.strftime("%Y-%m-%d") for r in records]

        return jsonify({'status': 'success', 'dates': date_list})

    @app.route("/get_friend_data")
    def get_friend_data():
        username = session.get("user")
        if not username:
            return jsonify({"error": "Not logged in"}), 401

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # get request
        received = FriendRequest.query.filter_by(to_user_id=user.user_id, status="pending").all()
        received_data = [
            {"id": r.id, "from_user": r.from_user.username if r.from_user else "(unknown)"}
            for r in received
        ]

        # send request
        sent = FriendRequest.query.filter_by(from_user_id=user.user_id).all()
        sent_data = [
            {"id": r.id, "to_user": r.to_user.username if r.to_user else "(unknown)", "status": r.status}
            for r in sent
        ]

        # friend list
        accepted = FriendRequest.query.filter(
            ((FriendRequest.from_user_id == user.user_id) | (FriendRequest.to_user_id == user.user_id)) &
            (FriendRequest.status == "accepted")
        ).all()

        friend_ids = set()
        for r in accepted:
            if r.from_user_id != user.user_id:
                friend_ids.add(r.from_user_id)
            elif r.to_user_id != user.user_id:
                friend_ids.add(r.to_user_id)

        friends = User.query.filter(User.user_id.in_(friend_ids)).all()
        friends_data = [{"username": f.username} for f in friends]

        return jsonify({
            "received_requests": received_data,
            "sent_requests": sent_data,
            "friends": friends_data
        })


    @app.route("/respond_request", methods=["POST"])
    def respond_request():
        username = session.get("user")
        if not username:
            return jsonify({"status": "error", "message": "Not logged in"}), 401

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        data = request.get_json()
        request_id = data.get("request_id")
        action = data.get("action")  # 'accept' or 'reject'

        friend_request = FriendRequest.query.filter_by(id=request_id, to_user_id=user.user_id).first()
        if not friend_request:
            return jsonify({"status": "error", "message": "Request not found"}), 404

        if action == "accept":
            friend_request.status = "accepted"
        elif action == "reject":
            friend_request.status = "rejected"
        else:
            return jsonify({"status": "error", "message": "Invalid action"}), 400

        db.session.commit()
        return jsonify({"status": "success", "message": f"Request {action}ed"})


    @app.route("/friends")
    def friends():
        username = session.get("user")
        if not username:
            return redirect(url_for("signin"))

        user = User.query.filter_by(username=username).first()
        if not user:
            return redirect(url_for("signin"))

        user_id = user.user_id

        # Sent and received requests
        sent_requests = FriendRequest.query.filter_by(from_user_id=user_id).all()
        received_requests = FriendRequest.query.filter_by(to_user_id=user_id).all()

        # Accepted friends
        accepted_requests = FriendRequest.query.filter(
            ((FriendRequest.from_user_id == user_id) | (FriendRequest.to_user_id == user_id)) &
            (FriendRequest.status == "accepted")
        ).all()

        # Resolve friend names
        def get_user(user_id):
            return User.query.filter_by(user_id=user_id).first()

        friends = []
        for req in accepted_requests:
            friend_id = req.to_user_id if req.from_user_id == user_id else req.from_user_id
            friend = get_user(friend_id)
            if friend:
                friends.append(friend)

        return render_template("friends.html",
                            sent_requests=sent_requests,
                            received_requests=received_requests,
                            friends=friends)
    


    @app.route("/add_friend", methods=["POST"])
    def add_friend():
        username = session.get("user")
        if not username:
            return jsonify({"status": "error", "message": "Not logged in"}), 401

        from_user = User.query.filter_by(username=username).first()
        data = request.get_json()
        print("[DEBUG] received data:", data)
        to_username = data.get("to_username")
        if not to_username:
            return jsonify({"status": "error", "message": "No username provided"})

        to_user = User.query.filter_by(username=to_username).first()
        if not to_user:
            return jsonify({"status": "error", "message": "User not found"})

        if to_user.user_id == from_user.user_id:
            return jsonify({"status": "error", "message": "You cannot add yourself"})

        existing = FriendRequest.query.filter_by(
            from_user_id=from_user.user_id,
            to_user_id=to_user.user_id
        ).first()

        if existing:
            return jsonify({"status": "error", "message": "Friend request already sent"})

        new_request = FriendRequest(
            from_user_id=from_user.user_id,
            to_user_id=to_user.user_id,
            status="pending"
        )
        db.session.add(new_request)
        db.session.commit()

        return jsonify({"status": "success", "message": "Friend request sent!"})


    

    @app.route("/respond_friend_request", methods=["POST"])
    def respond_friend_request():
        username = session.get("user")
        if not username:
            return redirect(url_for("signin"))

        user = User.query.filter_by(username=username).first()
        if not user:
            return redirect(url_for("signin"))

        request_id = request.form.get("request_id")
        action = request.form.get("action")  # 'accept' or 'reject'

        friend_request = FriendRequest.query.filter_by(id=request_id, to_user_id=user.user_id).first()
        if not friend_request:
            return "Request not found", 404

        if action == "accept":
            friend_request.status = "accepted"
        elif action == "reject":
            friend_request.status = "rejected"
        else:
            return "Invalid action", 400

        db.session.commit()
        return redirect(url_for("friends"))



    @app.route('/logout')
    def logout():
        session.pop('user', None)
        return redirect(url_for('index'))
