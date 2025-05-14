# Fittrack/routes/share_routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from Fittrack.forms import ShareForm
from Fittrack.models import SharedReport, db, DailyRecord, User

from Fittrack.routes.visualise_routes import get_accepted_friends


share_bp = Blueprint("share_routes", __name__)


@share_bp.route('/shared_reports')
@login_required
def shared_reports():
    
    shared_reports = SharedReport.query.filter_by(receiver_id=current_user.user_id).all()
    return render_template('shared_reports.html', shared_reports=shared_reports)

@share_bp.route("/share_report", methods=["POST"])
@login_required
def share_report():
    form = ShareForm()
    friends = get_accepted_friends(current_user.user_id)
    form.receiver_id.choices = [(f.user_id, f.username) for f in friends]

    print("====== DEBUG: Share Report ======")
    print("Form data:", form.data)
    print("Request.form:", request.form)
    print("Receiver ID:", form.receiver_id.data)
    print("Report Type:", form.report_type.data)
    print("validate_on_submit():", form.validate_on_submit())

    if form.validate_on_submit():
        shared = SharedReport(
            sender_id=current_user.user_id,
            receiver_id=form.receiver_id.data,
            report_type=form.report_type.data
        )
        db.session.add(shared)
        db.session.commit()
        
        saved_report = SharedReport.query.filter_by(
            sender_id=current_user.user_id,
            receiver_id=form.receiver_id.data,
            report_type=form.report_type.data
        ).first()
        print("Saved Report:", saved_report)
        flash("Report shared successfully!", "success")
    else:
        flash("Failed to share report.", "danger")
    
    return redirect(url_for('visualise_bp.visualise'))