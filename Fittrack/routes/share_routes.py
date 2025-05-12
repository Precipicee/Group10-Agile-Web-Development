from flask import flash, redirect, url_for
from Fittrack.models import db, DailyRecord, SharedAnalysis, User
from flask_login import current_user, login_required

@upload_bp.route('/share/<int:record_id>/<int:friend_id>', methods=['POST'])
@login_required
def share_record(record_id, friend_id):
    # Step 1: 获取记录并校验是否属于当前用户
    record = DailyRecord.query.get(record_id)
    if not record or record.user_id != current_user.user_id:
        flash("Unauthorized: You cannot share this record.", "danger")
        return redirect(url_for('upload_bp.upload'))

    # Step 2: 检查目标好友是否存在
    friend = User.query.get(friend_id)
    if not friend:
        flash("User not found.", "danger")
        return redirect(url_for('upload_bp.upload'))

    # Step 3: 检查是否已经分享过
    existing = SharedAnalysis.query.filter_by(
        record_id=record_id,
        sender_id=current_user.user_id,
        receiver_id=friend_id
    ).first()

    if existing:
        flash("You already shared this record with that friend.", "warning")
        return redirect(url_for('upload_bp.upload'))

    # Step 4: 插入共享记录
    new_shared = SharedAnalysis(
        record_id=record_id,
        sender_id=current_user.user_id,
        receiver_id=friend_id
    )
    db.session.add(new_shared)
    db.session.commit()

    flash(f"Record shared with {friend.username} successfully!", "success")
    return redirect(url_for('upload_bp.upload'))

@upload_bp.route('/shared_reports')
@login_required
def shared_reports():
    # 获取别人分享给当前用户的所有记录
    shared_entries = SharedAnalysis.query.filter_by(receiver_id=current_user.user_id).all()

    return render_template("shared_reports.html", records=shared_entries)
