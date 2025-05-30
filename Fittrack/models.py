from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(200), nullable=False)
    is_profile_complete = db.Column(db.Boolean, default=False)

    # Optional fields for profile
    birthday = db.Column(Date)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    height = db.Column(db.Integer)
    current_weight = db.Column(db.Float)
    target_weight = db.Column(db.Float)
    avatar = db.Column(db.String(100))

    # Optional targets
    target_weight_time_days = db.Column(db.Integer)
    target_exercise_time_per_week = db.Column(db.Integer)
    target_exercise_timeframe_days = db.Column(db.Integer)

    # BMI tracking
    weight_reg = db.Column(db.Float)
    bmi_reg = db.Column(db.Float)
    bmi_now = db.Column(db.Float)

    register_date = db.Column(Date)

    # One-to-many relationship
    records = db.relationship('DailyRecord', backref='user', lazy=True)
    recommended_calories = db.Column(db.Float)
    activity_level = db.Column(db.String(20))  # 'low', 'moderate', 'high'

    def get_id(self):
        return str(self.user_id) if self.user_id else None
    
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class DailyRecord(db.Model):
    __tablename__ = 'daily_record'

    record_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    weight = db.Column(db.Float, nullable=False)

    breakfast = db.Column(db.String(200))
    breakfast_calories = db.Column(db.Integer)

    lunch = db.Column(db.String(200))
    lunch_calories = db.Column(db.Integer)

    dinner = db.Column(db.String(200))
    dinner_calories = db.Column(db.Integer)

    # New field: total calories - Migration
    total_calories = db.Column(db.Integer)
    calories_burned = db.Column(db.Float, default=0.0)
    daily_calorie_needs = db.Column(db.Float)
    energy_gap = db.Column(db.Float)
    # One-to-many relationship: one record → many exercises
    exercises = db.relationship('DailyExercise', backref='record', lazy=True)
    @staticmethod
    def calculate_daily_calorie_need(weight, height, birthday, gender, activity_factor=1.55):
        """
        Use the Mifflin-St Jeor formula to calculate the daily heat demand
        """
        if not (weight and height and birthday and gender):
            return None 

        today = date.today()
        age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

        if gender.lower() == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        return round(bmr * activity_factor, 1)



class DailyExercise(db.Model):
    __tablename__ = 'daily_exercise'

    exercise_id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('daily_record.record_id'), nullable=False)
    exercise_type = db.Column(db.String(100), nullable=False)
    exercise_duration_minutes = db.Column(db.Integer, nullable=False)
    exercise_intensity = db.Column(
        db.String(20),
        nullable=False
    )

    __table_args__ = (
        db.CheckConstraint(
            "exercise_intensity IN ('light', 'moderate', 'intense')",
            name='valid_exercise_intensity'
        ),
    )

class FriendRequest(db.Model):
    __tablename__ = 'friend_request'

    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'accepted', 'rejected'

    from_user = db.relationship('User', foreign_keys=[from_user_id], backref='sent_friend_requests')
    to_user = db.relationship('User', foreign_keys=[to_user_id], backref='received_friend_requests')


class SharedAnalysis(db.Model):
    __tablename__ = 'shared_analysis'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    image_path = db.Column(db.String(200))  # Path to the analysis image
    description = db.Column(db.Text)        # Optional description
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    sender = db.relationship('User', foreign_keys=[sender_id], backref='shared_analyses_sent')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='shared_analyses_received')



class SharedReport(db.Model):
    __tablename__ = 'shared_report'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    report_type = db.Column(db.String(20), nullable=False)  # 'weight' or 'exercise'
    record_user_id = db.Column(db.Integer, nullable=True)  
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_reports')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_reports')
