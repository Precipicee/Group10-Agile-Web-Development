from flask import Blueprint, render_template, jsonify, request
from datetime import date, timedelta
from Fittrack.models import User, DailyRecord, DailyExercise
from flask_login import current_user, login_required
from ..forms import ShareReportForm
from ..models import FriendRequest

visualise_bp = Blueprint('visualise_bp', __name__)

@visualise_bp.route('/visualise')
@login_required
def visualise():
    return render_template('visualise.html')

@visualise_bp.route('/report/weight')
@login_required
def weight_report():
    form = ShareReportForm()

    sent = FriendRequest.query.filter_by(from_user_id=current_user.user_id, status='accepted').all()
    received = FriendRequest.query.filter_by(to_user_id=current_user.user_id, status='accepted').all()
    friend_ids = [f.to_user_id for f in sent] + [f.from_user_id for f in received]
    friends = User.query.filter(User.user_id.in_(friend_ids)).all()

    form.receiver_id.choices = [(f.user_id, f.username) for f in friends]

    return render_template("weight.html", form=form)

@visualise_bp.route('/weight_data')
@login_required
def weight_data():
    user_id = request.args.get("user_id")
    if user_id:
        user = User.query.get_or_404(user_id)
    else:
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
    form = ShareReportForm()

    
    sent = FriendRequest.query.filter_by(from_user_id=current_user.user_id, status='accepted').all()
    received = FriendRequest.query.filter_by(to_user_id=current_user.user_id, status='accepted').all()
    friend_ids = [f.to_user_id for f in sent] + [f.from_user_id for f in received]
    friends = User.query.filter(User.user_id.in_(friend_ids)).all()

    
    form.receiver_id.choices = [(f.user_id, f.username) for f in friends]

    
    return render_template("exercise.html", form=form)

@visualise_bp.route("/api/exercise_data")
@login_required
def exercise_data():
    user_id = request.args.get("user_id")
    if user_id:
        user = User.query.get_or_404(user_id)
    else:
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
    user_id = request.args.get("user_id")
    if user_id:
        user = User.query.get_or_404(user_id)
    else:
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

@visualise_bp.route("/shared_reports")
@login_required
def shared_reports():
    from ..models import SharedReport
    report_type = request.args.get("type", "").lower()
    
    query = SharedReport.query.filter_by(receiver_id=current_user.user_id)
    if report_type in ['weight', 'exercise', 'diet']:
        query = query.filter_by(report_type=report_type)

    reports = query.order_by(SharedReport.timestamp.desc()).all()
    return render_template("shared_reports.html", reports=reports, selected_type=report_type)

@visualise_bp.route("/shared_view/<int:user_id>/<type>")
@login_required
def view_shared_report(user_id, type):
    user = User.query.get_or_404(user_id)

    
    from ..forms import ShareReportForm
    from ..models import FriendRequest

    is_friend = FriendRequest.query.filter(
        ((FriendRequest.from_user_id == current_user.user_id) & 
         (FriendRequest.to_user_id == user_id) & 
         (FriendRequest.status == 'accepted')) |
        ((FriendRequest.from_user_id == user_id) & 
         (FriendRequest.to_user_id == current_user.user_id) & 
         (FriendRequest.status == 'accepted'))
    ).first()

    form = ShareReportForm() if is_friend else None

    
    if form:
        sent = FriendRequest.query.filter_by(from_user_id=current_user.user_id, status='accepted').all()
        received = FriendRequest.query.filter_by(to_user_id=current_user.user_id, status='accepted').all()
        friend_ids = [f.to_user_id for f in sent] + [f.from_user_id for f in received]
        friends = User.query.filter(User.user_id.in_(friend_ids)).all()
        form.receiver_id.choices = [(f.user_id, f.username) for f in friends]

    if type == "weight":
        
        user = User.query.get_or_404(user_id)
        
        return render_template("weight.html", shared_user=user, form=form)

    elif type == "exercise":
        user = User.query.get_or_404(user_id)
        
        return render_template("exercise.html", shared_user=user, form=form)

    else:
        return "Invalid report type", 400

@visualise_bp.route("/diet")
@login_required
def diet_report():
    return render_template("diet.html")
