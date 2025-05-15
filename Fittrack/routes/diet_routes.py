from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import current_user, login_required
from Fittrack.models import db, DailyRecord, SharedReport, User, FriendRequest
from ..forms import ShareReportForm
from datetime import datetime


diet_bp = Blueprint('diet_bp', __name__)

@diet_bp.route("/diet_data/<date_str>")
@login_required
def get_diet_data(date_str):
    """Get a certain day's diet record and recommended intake value, and support shared view"""
    try:
        user_id = request.args.get("user_id", type=int)
        user = User.query.get(user_id) if user_id else current_user

        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        record = DailyRecord.query.filter_by(user_id=user.user_id, date=date).first()

        if not record:
            return jsonify({'status': 'empty'})

        return jsonify({
            'status': 'success',
            'date': date_str,
            'breakfast': record.breakfast or '',
            'lunch': record.lunch or '',
            'dinner': record.dinner or '',
            'total_calories': record.total_calories or 0,
            'recommended': record.daily_calorie_needs or 0,
            'gap': record.energy_gap or 0
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@diet_bp.route("/diet_calorie_trend")
@login_required
def diet_calorie_trend():
    user_id = request.args.get("user_id", type=int)
    user = User.query.get(user_id) if user_id else current_user

    records = DailyRecord.query.filter_by(user_id=user.user_id).order_by(DailyRecord.date.asc()).all()
    data = [
        {
            "date": r.date.strftime("%Y-%m-%d"),
            "total_calories": r.total_calories or 0
        } for r in records
    ]
    return jsonify({"status": "success", "data": data})



@diet_bp.route("/diet_energy_gap_trend")
@login_required
def diet_energy_gap_trend():
    user_id = request.args.get("user_id", type=int)
    user = User.query.get(user_id) if user_id else current_user

    records = DailyRecord.query.filter_by(user_id=user.user_id).order_by(DailyRecord.date.asc()).all()
    data = [
        {
            "date": r.date.strftime("%Y-%m-%d"),
            "energy_gap": r.energy_gap or 0
        } for r in records
    ]
    return jsonify({"status": "success", "data": data})



@diet_bp.route("/api/recommended_calories")
@login_required
def api_recommended_calories():
    user_id = request.args.get("user_id", type=int)
    user = User.query.get(user_id) if user_id else current_user

    if not user:
        return jsonify({'error': 'User not found'}), 404

    required_fields = [user.height, user.gender, user.birthday, user.current_weight, user.target_weight]
    if any(field is None for field in required_fields):
        return jsonify({'error': 'Incomplete profile'}), 400

    today = datetime.today().date()
    age = today.year - user.birthday.year - ((today.month, today.day) < (user.birthday.month, user.birthday.day))

    gender = user.gender.strip().lower()
    if gender == 'male':
        bmr = 10 * user.current_weight + 6.25 * user.height - 5 * age + 5
    elif gender == 'female':
        bmr = 10 * user.current_weight + 6.25 * user.height - 5 * age - 161
    else:
        bmr = 10 * user.current_weight + 6.25 * user.height - 5 * age - 78  

    activity_param = request.args.get("activity", "moderate").lower()
    activity_map = {
        "low": 1.2,
        "moderate": 1.55,
        "high": 1.9
    }
    activity_factor = activity_map.get(activity_param, 1.55)

    recommended = round(bmr * activity_factor)

    # db
    user.recommended_calories = recommended
    user.activity_level = activity_param
    db.session.commit()

    return jsonify({
        'recommended': recommended,
        'age': age,
        'height': user.height,
        'current_weight': user.current_weight,
        'gender': user.gender,
        'goal': 'lose weight' if user.current_weight > user.target_weight else 'maintain',
        'activity_level': activity_param
    })



@diet_bp.route("/report/diet")
@login_required
def diet_report():
    form = ShareReportForm()

    # Calculate the recommended intake and write it into the database
    user = current_user
    required_fields = [user.height, user.gender, user.birthday, user.current_weight, user.target_weight]
    if all(required_fields):
        today = datetime.today().date()
        age = today.year - user.birthday.year - ((today.month, today.day) < (user.birthday.month, user.birthday.day))
        gender = user.gender.strip().lower()

        if gender == 'male':
            bmr = 10 * user.current_weight + 6.25 * user.height - 5 * age + 5
        elif gender == 'female':
            bmr = 10 * user.current_weight + 6.25 * user.height - 5 * age - 161
        else:
            bmr = 10 * user.current_weight + 6.25 * user.height - 5 * age - 78

        # defualt activity_level = moderate
        activity_param = user.activity_level or 'moderate'
        activity_map = {
            "low": 1.2,
            "moderate": 1.55,
            "high": 1.9
        }
        activity_factor = activity_map.get(activity_param, 1.55)

        user.recommended_calories = round(bmr * activity_factor)
        user.activity_level = activity_param
        db.session.commit()

    sent = FriendRequest.query.filter_by(from_user_id=user.user_id, status='accepted').all()
    received = FriendRequest.query.filter_by(to_user_id=user.user_id, status='accepted').all()
    friend_ids = [f.to_user_id for f in sent] + [f.from_user_id for f in received]
    friends = User.query.filter(User.user_id.in_(friend_ids)).all()
    form.receiver_id.choices = [(f.user_id, f.username) for f in friends]

    return render_template("diet.html", form=form)





@diet_bp.route("/share_diet_report", methods=["POST"])
@login_required
def share_diet_report():
    form = ShareReportForm()
    if form.validate_on_submit():
        shared = SharedReport(
            report_type='diet',
            sender_id=current_user.user_id,
            receiver_id=form.receiver_id.data
        )
        db.session.add(shared)
        db.session.commit()
        flash("Diet report shared successfully.", "success")
    else:
        flash("Failed to share diet report.", "danger")

    return redirect(url_for("diet_bp.diet_report"))
