from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime, timedelta, date
from Fittrack.models import db, User, DailyRecord, DailyExercise
from flask_login import current_user, login_required
from Fittrack.utils.gpt_utils import estimate_calories_from_meal, estimate_calories_from_exercise

upload_bp = Blueprint('upload_bp', __name__)

@upload_bp.route('/upload')
@login_required
def upload():
    form_data = session.get('pending_record', {})
    return render_template('upload.html', form_data=form_data)

@upload_bp.route('/add_record', methods=['POST'])
@login_required
def add_record():
    user = current_user

    date_str = request.form.get('date')
    form_data = request.form.to_dict(flat=True)
    session['pending_record'] = form_data

    # 获取原始输入
    exercises = request.form.getlist('exercise[]')
    durations = request.form.getlist('duration[]')
    intensities = request.form.getlist('intensity[]')

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

    # overwrite old record if exists
    existing = DailyRecord.query.filter_by(user_id=user.user_id, date=record_date).first()
    if existing:
        DailyExercise.query.filter_by(record_id=existing.record_id).delete()
        db.session.delete(existing)
        db.session.commit()

    try:
        weight = float(form_data.get('weight'))
        breakfast = form_data.get('breakfast')
        lunch = form_data.get('lunch')
        dinner = form_data.get('dinner')

        # 估算摄入热量
        meal_description = f"""
        User Info:
        - Gender: {user.gender or 'unspecified'}
        - Weight: {user.current_weight or weight} kg
        - Height: {user.height or 'N/A'} cm
        Meals:
        Breakfast: {breakfast or 'N/A'}
        Lunch: {lunch or 'N/A'}
        Dinner: {dinner or 'N/A'}
        """.strip()
        estimated_calories = estimate_calories_from_meal(meal_description)

        # 计算日常需求
        daily_need = DailyRecord.calculate_daily_calorie_need(
            weight=weight,
            height=user.height,
            birthday=user.birthday,
            gender=user.gender
        )

        # 处理运动信息（只保留完整的）
        exercise_list = []
        incomplete_count = 0
        for i in range(len(exercises)):
            name = exercises[i].strip()
            dur = durations[i].strip()
            intensity = intensities[i].strip()

            if name and dur and intensity:
                try:
                    exercise_list.append({
                        'type': name,
                        'duration': int(dur),
                        'intensity': intensity
                    })
                except Exception:
                    incomplete_count += 1
            elif name or dur or intensity:
                incomplete_count += 1  # 部分填写也视为不完整

        # 计算消耗热量（仅在所有字段齐全时才估算）
        if exercise_list:
            estimated_burned = estimate_calories_from_exercise(exercise_list)
            print(f"[INFO] Estimated exercise calories burned: {estimated_burned}")
        else:
            estimated_burned = 0.0
            print("[INFO] No valid exercises. Calories burned set to 0.")

        # 计算能量差值
        energy_gap = estimated_calories - daily_need - estimated_burned if estimated_calories and daily_need is not None else None

        # 保存主记录
        record = DailyRecord(
            user_id=user.user_id,
            date=record_date,
            weight=weight,
            breakfast=breakfast,
            lunch=lunch,
            dinner=dinner,
            total_calories=estimated_calories,
            calories_burned=estimated_burned,
            daily_calorie_needs=daily_need,
            energy_gap=energy_gap
        )
        db.session.add(record)
        db.session.commit()

        # 保存运动数据
        for ex in exercise_list:
            db.session.add(DailyExercise(
                record_id=record.record_id,
                exercise_type=ex['type'],
                exercise_duration_minutes=ex['duration'],
                exercise_intensity=ex['intensity']
            ))
        db.session.commit()

        # 用户提示
        if incomplete_count > 0:
            flash("Record saved successfully, but some incomplete exercise entries were ignored.", "warning")
        else:
            flash("Record saved successfully!", "success")

        # 更新 session
        session['pending_record'] = {
            'breakfast': breakfast,
            'lunch': lunch,
            'dinner': dinner,
            'total_calories': estimated_calories,
            'calories_burned': estimated_burned,
            'daily_calorie_needs': daily_need,
            'energy_gap': energy_gap
        }
        return redirect(url_for('upload_bp.upload'))

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")
        return redirect(url_for('upload_bp.upload'))


@upload_bp.route('/records')
@login_required
def records():
    user = current_user

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
@login_required
def view_history():
    return render_template("history.html")

@upload_bp.route('/get_today_record')
@login_required
def get_today_record():
    user = current_user
    today = date.today()
    record = DailyRecord.query.filter_by(user_id=user.user_id, date=today).first()
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
@login_required
def get_record_details(date):
    try:
        user = current_user
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
@login_required
def get_record_dates():
    user = current_user
    records = DailyRecord.query.filter_by(user_id=user.user_id).all()
    return jsonify({'status': 'success', 'dates': [r.date.strftime("%Y-%m-%d") for r in records]})

@upload_bp.route("/check_existing_record")
@login_required
def check_existing_record():
    """
    For AJAX call: check whether the given date has been recorded and return JSON
    """
    date_str = request.args.get("date")
    if not date_str:
        return jsonify({"error": "Missing date parameter."}), 400

    try:
        record_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format."}), 400

    existing = DailyRecord.query.filter_by(user_id=current_user.user_id, date=record_date).first()
    return jsonify({"exists": bool(existing)})


@upload_bp.route('/calorie_summary/<date>')
@login_required
def calorie_summary(date):
    record = DailyRecord.query.filter_by(user_id=current_user.user_id, date=date).first()
    if record:
        return jsonify({
            'total_calories': record.total_calories or 0,
            'calories_burned': record.calories_burned or 0,
            'daily_calorie_needs': record.daily_calorie_needs or 0, 
            'energy_gap': record.energy_gap or 0 
        })
    else:
        return jsonify({
            'total_calories': 0,
            'calories_burned': 0,
            'daily_calorie_needs': 0,
            'energy_gap': 0
        })
