from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from Fittrack.models import db, User
from Fittrack.forms import SignupForm, SigninForm
from flask_login import login_user, logout_user, login_required, current_user


auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=form.remember.data)
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

        new_user = User(
            username=username,
            email=email,
            is_profile_complete=False  
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash("Account created and signed in.", "success")
        return redirect(url_for('profile_bp.basicinfo'))

    return render_template('signup.html', form=form)



@auth_bp.route('/check_login')
def check_login():
    return jsonify({'logged_in': current_user.is_authenticated})


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('main_bp.index'))

