from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from Fittrack.models import User
from Fittrack.forms import SignupForm, SigninForm

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.hashed_password, password):
            session['user'] = user.username
            flash("Signed in successfully!", "success")
            return redirect(url_for('main_bp.index'))
        else:
            flash("Invalid username or password!", "danger")

    return render_template('signin.html', form=form)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already exists!", "danger")
            return render_template('signup.html', form=form)

        hashed_password = generate_password_hash(password)
        session['temp_user'] = {
            'username': username,
            'email': email,
            'password': hashed_password
        }

        flash("Account created. Proceed to basic info setup.", "success")
        return redirect(url_for('profile_bp.basicinfo'))

    return render_template('signup.html', form=form)

@auth_bp.route('/check_login')
def check_login():
    return jsonify({'logged_in': 'user' in session})

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('main_bp.index'))
