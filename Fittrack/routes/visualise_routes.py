from flask import Blueprint, render_template, jsonify
from datetime import date, timedelta
from Fittrack.models import User, DailyRecord, DailyExercise
from flask_login import current_user, login_required

visualise_bp = Blueprint('visualise_bp', __name__)

@visualise_bp.route('/visualise')
@login_required
def visualise():
    return render_template('visualise.html')

@visualise_bp.route('/report/weight')
@login_required
def weight_report():
    return render_template('weight.html')

@visualise_bp.route('/weight_data')
@login_required
def weight_data():
    user = current_user

    records = DailyRecord.query.filter_by(user_id=user.user_id).order_by(DailyRecord.date.asc()).all()
    return jsonify({
        'status': 'success',
        'data': [
            {'date': r.date.strftime("%Y-%m-%d"), 'weight': r.weight} for r in records
        ]
    })

@visualise_bp.route("/report/exercise")
@login_required
def exercise_report():
    return render_template("exercise.html")

@visualise_bp.route("/api/exercise_data")
@login_required
def exercise_data():
    user = current_user

    records = DailyRecord.query.filter_by(user_id=user.user_id).order_by(DailyRecord.date.asc()).all()
    labels = []
    minutes = []

    for record in records:
        date_str = record.date.strftime("%Y-%m-%d")
        exercises = DailyExercise.query.filter_by(record_id=record.record_id).all()
        total_minutes = sum(e.exercise_duration_minutes for e in exercises)

        labels.append(date_str)
        minutes.append(total_minutes)

    return jsonify({
        "labels": labels,
        "minutes": minutes
    })

@visualise_bp.route("/api/exercise_type_breakdown")
@login_required
def exercise_type_breakdown():
    user = current_user

    records = DailyRecord.query.filter_by(user_id=user.user_id).all()
    type_totals = {}

    for record in records:
        exercises = DailyExercise.query.filter_by(record_id=record.record_id).all()
        for e in exercises:
            normalized_type = e.exercise_type.strip().lower()
            type_totals[normalized_type] = type_totals.get(normalized_type, 0) + e.exercise_duration_minutes

    return jsonify({
        "labels": [k.capitalize() for k in type_totals.keys()],
        "minutes": list(type_totals.values())
    })

@visualise_bp.route("/api/exercise_intensity_breakdown")
@login_required
def exercise_intensity_breakdown():
    user = current_user

    records = DailyRecord.query.filter_by(user_id=user.user_id).all()
    intensity_totals = {}

    for record in records:
        exercises = DailyExercise.query.filter_by(record_id=record.record_id).all()
        for e in exercises:
            intensity = e.exercise_intensity.lower().capitalize()
            intensity_totals[intensity] = intensity_totals.get(intensity, 0) + e.exercise_duration_minutes

    return jsonify({
        "labels": list(intensity_totals.keys()),
        "minutes": list(intensity_totals.values())
    })

@visualise_bp.route("/api/exercise_goal_progress")
@login_required
def exercise_goal_progress():
    user = current_user

    if not user or not user.target_exercise_time_per_week:
        return jsonify({
            "status": "error",
            "message": "User or goal not found"
        }), 404

    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)          # Sunday

    total_minutes = 0
    records = DailyRecord.query.filter_by(user_id=user.user_id).filter(
        DailyRecord.date >= start_of_week,
        DailyRecord.date <= end_of_week
    ).all()

    for record in records:
        for e in record.exercises:
            total_minutes += e.exercise_duration_minutes

    goal = user.target_exercise_time_per_week
    remaining = max(goal - total_minutes, 0)

    return jsonify({
        "status": "success",
        "goal": goal,
        "completed": total_minutes,
        "remaining": remaining
    })
