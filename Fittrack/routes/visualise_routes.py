from flask import Blueprint, render_template, jsonify, request
from datetime import date, timedelta
from Fittrack.models import User, DailyRecord, DailyExercise
from flask_login import current_user, login_required
from Fittrack.forms import ShareForm
from Fittrack.models import SharedReport, FriendRequest
from sqlalchemy import and_


visualise_bp = Blueprint('visualise_bp', __name__)

@visualise_bp.route('/visualise')
@login_required
def visualise():
    return render_template('visualise.html')

@visualise_bp.route('/report/weight')
@login_required
def weight_report():
    share_form = ShareForm()
    friends = get_accepted_friends(current_user.user_id)
    share_form.receiver_id.choices = [(f.user_id, f.username) for f in friends]

    # 调试：检查 report_type 和 receiver_id.choices
    print("===== DEBUG: Weight Report =====")
    print("Report Type:", share_form.report_type.data)  # 检查 report_type 是否正确
    print("Friends (receiver_id.choices):", [(f.user_id, f.username) for f in friends])  # 检查好友列表
    
    latest_record = DailyRecord.query.filter_by(user_id=current_user.user_id)\
                                     .order_by(DailyRecord.date.desc()).first()

    return render_template('weight.html', share_form=share_form, shared_user=current_user,
                           latest_weight_record=latest_record,report_type='weight')


@visualise_bp.route('/weight_data')
@login_required
def weight_data():
    user = current_user

    records = DailyRecord.query.filter_by(user_id=user.user_id).order_by(DailyRecord.date.asc()).all()
    return jsonify({
        'status': 'success',
        'height': user.height,
        'target_weight': user.target_weight,
        'data': [
            {'date': r.date.strftime("%Y-%m-%d"), 'weight': r.weight} for r in records
        ]
    })

@visualise_bp.route("/report/exercise")
@login_required
def exercise_report():
    share_form = ShareForm()
    friends = get_accepted_friends(current_user.user_id)
    share_form.receiver_id.choices = [(f.user_id, f.username) for f in friends]

    # 调试：检查 report_type 和 receiver_id.choices
    print("===== DEBUG: Exercise Report =====")
    print("Report Type:", share_form.report_type.data)  # 检查 report_type 是否正确
    print("Friends (receiver_id.choices):", [(f.user_id, f.username) for f in friends])  # 检查好友列表
    latest_exercise_record = DailyRecord.query \
        .filter_by(user_id=current_user.user_id) \
        .order_by(DailyRecord.date.desc()) \
        .first()

    return render_template(
        "exercise.html",
        share_form=share_form,
        shared_user=current_user,
        latest_exercise_record=latest_exercise_record,
        report_type='exercise'
    )


@visualise_bp.route("/api/exercise_data")
@login_required
def exercise_data():
    user = current_user
    range_option = request.args.get("range", "week")

    today = date.today()
    if range_option == "month":
        start = today - timedelta(days=30)
    elif range_option == "year":
        start = today - timedelta(days=365)
    else:  # default is week
        start = today - timedelta(days=7)

    records = DailyRecord.query.filter_by(user_id=user.user_id).filter(
        DailyRecord.date >= start
    ).order_by(DailyRecord.date.asc()).all()
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


def get_accepted_friends(user_id):
    received = FriendRequest.query.filter_by(to_user_id=user_id, status='accepted').all()
    sent = FriendRequest.query.filter_by(from_user_id=user_id, status='accepted').all()

    friends = []

    for req in received:
        friend = User.query.get(req.from_user_id)
        if friend:
            friends.append(friend)

    for req in sent:
        friend = User.query.get(req.to_user_id)
        if friend and friend not in friends:
            friends.append(friend)

    return friends

from flask import flash, redirect, url_for


@visualise_bp.route("/shared_report/<report_type>/<int:user_id>")
@login_required
def view_shared_report(report_type, user_id):
    shared = SharedReport.query.filter(
        and_(
            SharedReport.sender_id == user_id,
            SharedReport.receiver_id == current_user.user_id,
            SharedReport.report_type == report_type
        )
    ).first()

    if not shared:
        flash("You are not authorized to view this shared report.", "danger")
        return redirect(url_for("visualise_bp.visualise"))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("visualise_bp.visualise"))

    share_form = ShareForm()
    
    if report_type == "weight":
        records = DailyRecord.query.filter_by(user_id=user_id).order_by(DailyRecord.date.asc()).all()
        return render_template("weight.html",
                               share_form=share_form,
                               shared_user=user,   
                               records=records,
                               report_type='weight')

    elif report_type == "exercise":
        records = DailyRecord.query.filter_by(user_id=user_id).order_by(DailyRecord.date.asc()).all()
        return render_template("exercise.html",
                               share_form=share_form,
                               shared_user=user,   
                               records=records,
                               report_type='exercise')

    else:
        flash("Invalid report type.", "danger")
        return redirect(url_for("visualise_bp.visualise"))
    

@visualise_bp.route("/shared_reports")
@login_required
def shared_reports():
    reports = SharedReport.query.filter_by(receiver_id=current_user.user_id).all()
    return render_template("shared_reports.html", reports=reports)
