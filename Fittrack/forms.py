from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField,
    DateField, RadioField, IntegerField, FloatField, HiddenField, ValidationError
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
import re

def validate_strong_password(form, field):
    password = field.data
    if len(password) < 6:
        raise ValidationError("Password must be at least 6 characters long.")
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r'[0-9]', password):
        raise ValidationError("Password must contain at least one number.")


class SigninForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign In')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        validate_strong_password
    ])
    confirm = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Sign Up')


class BasicInfoForm(FlaskForm):
    avatar = HiddenField('Avatar', validators=[DataRequired()])
    birthday = DateField('Birthday', validators=[DataRequired()], format='%Y-%m-%d')
    gender = RadioField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    height = IntegerField('Height (cm)', validators=[DataRequired()])
    current_weight = FloatField('Current Weight (kg)', validators=[DataRequired()])
    target_weight = FloatField('Target Weight (kg)', validators=[DataRequired()])
    target_weight_time_days = IntegerField('Target Time (days)', validators=[Optional()])
    target_exercise_time_per_week = IntegerField('Exercise per Week (min)', validators=[Optional()])
    target_exercise_timeframe_days = IntegerField('Exercise Plan Duration (days)', validators=[Optional()])
    submit = SubmitField('Submit Profile')

class EditProfileForm(FlaskForm):
    birthday = DateField('Birthday', validators=[DataRequired()], format='%Y-%m-%d')
    gender = RadioField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    height = IntegerField('Height', validators=[DataRequired()])
    current_weight = FloatField('Current Weight', validators=[DataRequired()])
    target_weight = FloatField('Target Weight', validators=[DataRequired()])
    target_weight_time_days = IntegerField('Target Days', validators=[Optional()])
    target_exercise_time_per_week = IntegerField('Exercise per Week', validators=[Optional()])
    target_exercise_timeframe_days = IntegerField('Exercise Plan Duration', validators=[Optional()])
    submit = SubmitField('Save Changes')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        validate_strong_password
    ])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')

