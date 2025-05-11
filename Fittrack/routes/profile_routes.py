from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
from Fittrack.models import db, User, DailyRecord
from Fittrack.forms import BasicInfoForm
from Fittrack import csrf
from flask_login import current_user, login_required

profile_bp = Blueprint('profile_bp', __name__)

@profile_bp.route('/basicinfo', methods=['GET', 'POST'])
@login_required
def basicinfo():
    form = BasicInfoForm()

    if request.method == 'GET':
        return render_template('basicinfo.html', form=form)

    if not form.validate_on_submit():
        flash("All required fields must be filled out correctly.", "danger")
        return render_template('basicinfo.html', form=form)

    try:
        # 提取表单数据
        birthday = form.birthday.data
        gender = form.gender.data
        height = form.height.data
        weight_reg = form.current_weight.data
        target_weight = form.target_weight.data
        avatar = form.avatar.data

        today = datetime.today().date()
        age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
        height_m = height / 100
        bmi = round(weight_reg / (height_m ** 2), 2)

        # 更新 current_user
        user = current_user
        user.is_profile_complete = True 
        user.birthday = birthday
        user.age = age
        user.gender = gender
        user.height = height
        user.current_weight = weight_reg
        user.target_weight = target_weight
        user.avatar = avatar
        user.weight_reg = weight_reg
        user.bmi_reg = bmi
        user.bmi_now = bmi
        user.register_date = today
        user.target_weight_time_days = form.target_weight_time_days.data
        user.target_exercise_time_per_week = form.target_exercise_time_per_week.data
        user.target_exercise_timeframe_days = form.target_exercise_timeframe_days.data

        db.session.commit()

        # 同步创建初始 DailyRecord
        record = DailyRecord(user_id=user.user_id, date=today, weight=weight_reg)
        db.session.add(record)
        db.session.commit()

        flash("Profile created successfully!", "success")
        return redirect(url_for('profile_bp.services'))

    except Exception as e:
        db.session.rollback()
        flash(f"Error saving to database: {str(e)}", "danger")
        return render_template('basicinfo.html', form=form)

@profile_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@profile_bp.route('/services')
@login_required
def services():
    return render_template('services.html')

@profile_bp.route('/profile_data')
@login_required
def profile_data():
    user = current_user
    latest_record = DailyRecord.query.filter_by(user_id=user.user_id).order_by(DailyRecord.date.desc()).first()
    current_weight = latest_record.weight if latest_record else ""

    return jsonify({
        'status': 'success',
        'data': {
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
    })

@csrf.exempt
@profile_bp.route('/update_profile_fields', methods=['POST'])
@login_required
def update_profile_fields():
    if not request.is_json:
        return jsonify({
            'status': 'error',
            'message': 'Invalid content type, expected application/json',
            'headers': dict(request.headers),
            'raw_data': request.data.decode('utf-8', errors='ignore')
        }), 400

    data = request.get_json(force=True)

    try:
        birthday_str = data.get('birthday', '').strip()
        birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
        height = float(data.get('height'))
        weight = float(data.get('weight_reg'))
        target_weight = float(data.get('target_weight'))
        height_m = height / 100
        bmi = round(weight / (height_m ** 2), 2)
        today = datetime.today().date()
        age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

        user = current_user
        user.birthday = birthday
        user.gender = data.get('gender')
        user.height = height
        user.weight_reg = weight
        user.target_weight = target_weight
        user.age = age
        user.bmi_reg = bmi
        user.bmi_now = bmi

        if data.get('target_weight_time_days'):
            user.target_weight_time_days = int(data.get('target_weight_time_days'))
        if data.get('target_exercise_time_per_week'):
            user.target_exercise_time_per_week = int(data.get('target_exercise_time_per_week'))
        if data.get('target_exercise_timeframe_days'):
            user.target_exercise_timeframe_days = int(data.get('target_exercise_timeframe_days'))

        reg_date = user.register_date if isinstance(user.register_date, date) else datetime.strptime(user.register_date, "%Y-%m-%d").date()
        reg_record = DailyRecord.query.filter_by(user_id=user.user_id, date=reg_date).first()
        if reg_record:
            reg_record.weight = weight

        db.session.commit()
        return jsonify({'status': 'success', 'age': age, 'bmi': bmi})

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})
