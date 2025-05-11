from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date
from flask_login import UserMixin


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

    def get_id(self):
        return str(self.user_id) if self.user_id else None


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

    # One-to-many relationship: one record → many exercises
    exercises = db.relationship('DailyExercise', backref='record', lazy=True)


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
