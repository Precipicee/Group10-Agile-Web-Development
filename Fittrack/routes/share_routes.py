from flask import Blueprint, request, redirect, flash, url_for
from flask_login import current_user, login_required
from .. import db
from ..models import SharedReport, FriendRequest, User
from ..forms import ShareReportForm

import logging

share_bp = Blueprint("share_bp", __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
@share_bp.route("/share_report", methods=["POST"])
@login_required
def share_report():
    form = ShareReportForm()
    report_type = request.args.get('report_type')

    sent = FriendRequest.query.filter_by(from_user_id=current_user.user_id, status='accepted').all()
    received = FriendRequest.query.filter_by(to_user_id=current_user.user_id, status='accepted').all()
    friend_ids = [f.to_user_id for f in sent] + [f.from_user_id for f in received]
    friends = User.query.filter(User.user_id.in_(friend_ids)).all()
    form.receiver_id.choices = [(f.user_id, f.username) for f in friends]  

    logger.debug(f"Form data: {form.data}, Report type: {report_type}")
    if form.validate_on_submit():
        receiver_id = form.receiver_id.data
        

        

        
        is_friend = FriendRequest.query.filter(
            ((FriendRequest.from_user_id == current_user.user_id) & 
             (FriendRequest.to_user_id == receiver_id) & 
             (FriendRequest.status == 'accepted')) |
            ((FriendRequest.from_user_id == receiver_id) & 
             (FriendRequest.to_user_id == current_user.user_id) & 
             (FriendRequest.status == 'accepted'))
        ).first()

        if not is_friend:
            flash("You can only share reports with your friends.", "danger")
            return redirect(request.referrer or url_for("main_bp.index"))


        new_share = SharedReport(
            sender_id=current_user.user_id,
            receiver_id=receiver_id,
            report_type=report_type,
            record_user_id=current_user.user_id
        )
        db.session.add(new_share)
        db.session.commit()
        flash(f"{report_type.capitalize()} report shared successfully!", "success")
    else:
        flash("Invalid form submission.", "danger")

    return redirect(request.referrer or url_for("main_bp.index"))


@share_bp.route("/delete_shared_report/<int:report_id>", methods=["POST"])
@login_required
def delete_shared_report(report_id):
    report = SharedReport.query.get_or_404(report_id)

    if report.receiver_id != current_user.user_id:
        flash("You are not authorized to delete this report.", "danger")
        return redirect(url_for("visualise_bp.shared_reports"))

    db.session.delete(report)
    db.session.commit()
    flash("Shared report deleted successfully.", "success")
    return redirect(url_for("visualise_bp.shared_reports"))
