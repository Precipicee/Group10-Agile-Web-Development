from flask import Blueprint, request, redirect, flash, url_for
from flask_login import current_user, login_required
from .. import db
from ..models import SharedReport, FriendRequest, User
from ..forms import ShareReportForm

share_bp = Blueprint("share_bp", __name__)

@share_bp.route("/share_report", methods=["POST"])
@login_required
def share_report():
    form = ShareReportForm()

    sent = FriendRequest.query.filter_by(from_user_id=current_user.user_id, status='accepted').all()
    received = FriendRequest.query.filter_by(to_user_id=current_user.user_id, status='accepted').all()
    friend_ids = [f.to_user_id for f in sent] + [f.from_user_id for f in received]
    friends = User.query.filter(User.user_id.in_(friend_ids)).all()
    form.receiver_id.choices = [(f.user_id, f.username) for f in friends]  


    if form.validate_on_submit():
        receiver_id = form.receiver_id.data
        report_type = form.report_type.data

        print("✅ 最终提交进来的类型是：", report_type)

        
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
            return redirect(request.referrer or url_for("main_routes.index"))

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

    return redirect(request.referrer or url_for("main_routes.index"))
