from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField,
    DateField, RadioField, IntegerField, FloatField, HiddenField
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class SigninForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign In')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')

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
