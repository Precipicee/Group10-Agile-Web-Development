from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta, date
from Fittrack.models import db, User, DailyRecord, DailyExercise

upload_bp = Blueprint('upload_bp', __name__)

@upload_bp.route('/upload')
def upload():
    form_data = session.get('pending_record', {})
    return render_template('upload.html', form_data=form_data)

@upload_bp.route('/add_record', methods=['POST'])
def add_record():
    username = session.get('user')
    if not username:
        flash("You must be logged in.", "danger")
        return redirect(url_for('auth_bp.signin'))

    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('upload_bp.upload'))

    date_str = request.form.get('date')
    form_data = request.form.to_dict(flat=True)
    session['pending_record'] = form_data

    try:
        record_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.today().date()

        if record_date > today:
            flash("Date cannot be in the future.", "danger")
            return redirect(url_for('upload_bp.upload'))

        if record_date < today - timedelta(days=180):
            flash("Date is too old. Please select a recent date.", "danger")
            return redirect(url_for('upload_bp.upload'))

    except Exception:
        flash("Invalid date format.", "danger")
        return redirect(url_for('upload_bp.upload'))

    existing = DailyRecord.query.filter_by(user_id=user.user_id, date=record_date).first()
    if existing and not session.get('overwrite'):
        flash("Record already exists. Click Submit again to overwrite.", "warning")
        session['overwrite'] = True
        return redirect(url_for('upload_bp.upload'))

    session.pop('overwrite', None)

    try:
        weight = float(form_data.get('weight'))
        breakfast = form_data.get('breakfast')
        lunch = form_data.get('lunch')
        dinner = form_data.get('dinner')

        if existing:
            DailyExercise.query.filter_by(record_id=existing.record_id).delete()
            db.session.delete(existing)
            db.session.commit()

        record = DailyRecord(
            user_id=user.user_id,
            date=record_date,
            weight=weight,
            breakfast=breakfast,
            lunch=lunch,
            dinner=dinner
        )
        db.session.add(record)
        db.session.commit()

        # Add exercises
        exercises = request.form.getlist('exercise[]')
        durations = request.form.getlist('duration[]')
        intensities = request.form.getlist('intensity[]')

        for i in range(len(exercises)):
            if exercises[i]:
                ex = DailyExercise(
                    record_id=record.record_id,
                    exercise_type=exercises[i],
                    exercise_duration_minutes=int(durations[i]),
                    exercise_intensity=intensities[i] or 'unknown'
                )
                db.session.add(ex)

        db.session.commit()
        flash("Record saved successfully!", "success")
        session.pop('pending_record', None)
        return redirect(url_for('profile_bp.services'))

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")
        return redirect(url_for('upload_bp.upload'))

@upload_bp.route('/update_record', methods=['POST'])
def update_record():
    username = session.get('user')
    if not username:
        flash("Please sign in first.", "danger")
        return redirect(url_for('auth_bp.signin'))

    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('auth_bp.signin'))

    try:
        form_data = request.form.to_dict(flat=False)
        date_str = request.form.get('date')
        weight = request.form.get('weight')
        breakfast = request.form.get('breakfast')
        lunch = request.form.get('lunch')
        dinner = request.form.get('dinner')
        exercise_combined = request.form.get('exercise')

        record_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        record = DailyRecord.query.filter_by(user_id=user.user_id, date=record_date).first()

        if not record:
            flash("Record not found for this date.", "warning")
            return redirect(url_for('upload_bp.upload'))

        record.weight = float(weight)
        record.breakfast = breakfast
        record.lunch = lunch
        record.dinner = dinner

        DailyExercise.query.filter_by(record_id=record.record_id).delete()

        if exercise_combined:
            for entry in exercise_combined.split(";"):
                if not entry.strip():
                    continue
                try:
                    name_part, rest = entry.split("(", 1)
                    name = name_part.strip()
                    rest = rest.replace(")", "").strip()
                    duration_str, intensity = [r.strip() for r in rest.split(",")]
                    duration = int(duration_str.replace("min", "").strip())
                    db.session.add(DailyExercise(
                        record_id=record.record_id,
                        exercise_type=name,
                        exercise_duration_minutes=duration,
                        exercise_intensity=intensity
                    ))
                except Exception as e:
                    print(f"[WARN] Failed to parse: {entry}", e)

        # Update BMI if same as register date
        try:
            reg_date = user.register_date if isinstance(user.register_date, date) else datetime.strptime(user.register_date, "%Y-%m-%d").date()
            if record_date == reg_date:
                height_m = user.height / 100
                bmi = round(float(weight) / (height_m ** 2), 2)
                user.weight_reg = float(weight)
                user.bmi_reg = bmi
                user.bmi_now = bmi
        except Exception as e:
            print("[WARN] BMI update failed", e)

        db.session.commit()
        flash("Record updated successfully!", "success")
        return redirect(url_for('profile_bp.services'))

    except Exception as e:
        db.session.rollback()
        flash(f"Error while updating record: {str(e)}", "danger")
        session['form_data'] = form_data
        return redirect(url_for('upload_bp.upload'))

@upload_bp.route('/records')
def records():
    username = session.get('user')
    if not username:
        return jsonify({'status': 'error', 'message': 'Not logged in'})

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'})

    record_list = DailyRecord.query.filter_by(user_id=user.user_id).order_by(DailyRecord.date.desc()).all()

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

@upload_bp.route("/history")
def view_history():
    return render_template("history.html")

@upload_bp.route('/get_today_record')
def get_today_record():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Not logged in'}), 401

    today = date.today()
    record = DailyRecord.query.filter_by(user_id=user_id, date=today).first()
    if not record:
        return jsonify({'status': 'empty'})

    exercises = DailyExercise.query.filter_by(record_id=record.record_id).all()
    return jsonify({
        'status': 'success',
        'data': {
            'weight': record.weight,
            'breakfast': record.breakfast,
            'lunch': record.lunch,
            'dinner': record.dinner,
            'exercises': [
                {
                    'type': e.exercise_type,
                    'duration': e.exercise_duration_minutes,
                    'intensity': e.exercise_intensity
                } for e in exercises
            ]
        }
    })

@upload_bp.route('/record_details/<date>')
def get_record_details(date):
    if 'user' not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 401

    try:
        user = User.query.filter_by(username=session['user']).first()
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        record = DailyRecord.query.filter_by(user_id=user.user_id, date=parsed_date).first()
        if not record:
            return jsonify({"status": "empty", "message": "No record for selected date"})

        exercises = DailyExercise.query.filter_by(record_id=record.record_id).all()
        return jsonify({
            "status": "success",
            "data": {
                "weight": record.weight,
                "breakfast": record.breakfast or "N/A",
                "lunch": record.lunch or "N/A",
                "dinner": record.dinner or "N/A",
                "exercises": [
                    {
                        "type": e.exercise_type,
                        "duration": e.exercise_duration_minutes,
                        "intensity": e.exercise_intensity
                    } for e in exercises
                ]
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@upload_bp.route('/record_dates')
def get_record_dates():
    if 'user' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'}), 401

    user = User.query.filter_by(username=session['user']).first()
    records = DailyRecord.query.filter_by(user_id=user.user_id).all()
    return jsonify({'status': 'success', 'dates': [r.date.strftime("%Y-%m-%d") for r in records]})
