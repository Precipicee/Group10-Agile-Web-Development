from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from Fittrack.models import db, User, FriendRequest
from flask_login import current_user, login_required

friends_bp = Blueprint('friends_bp', __name__)

@friends_bp.route("/friends")
@login_required
def friends():
    user = current_user
    user_id = user.user_id

    sent_requests = FriendRequest.query.filter_by(from_user_id=user_id).all()
    received_requests = FriendRequest.query.filter_by(to_user_id=user_id).all()

    accepted_requests = FriendRequest.query.filter(
        ((FriendRequest.from_user_id == user_id) | (FriendRequest.to_user_id == user_id)) &
        (FriendRequest.status == "accepted")
    ).all()

    def get_user(user_id):
        return User.query.filter_by(user_id=user_id).first()

    friends = []
    for req in accepted_requests:
        friend_id = req.to_user_id if req.from_user_id == user_id else req.from_user_id
        friend = get_user(friend_id)
        if friend:
            friends.append(friend)

    return render_template("friends.html",
                           sent_requests=sent_requests,
                           received_requests=received_requests,
                           friends=friends)

@friends_bp.route("/get_friend_data")
@login_required
def get_friend_data():
    user = current_user

    received = FriendRequest.query.filter_by(to_user_id=user.user_id, status="pending").all()
    sent = FriendRequest.query.filter_by(from_user_id=user.user_id).all()

    accepted = FriendRequest.query.filter(
        ((FriendRequest.from_user_id == user.user_id) | (FriendRequest.to_user_id == user.user_id)) &
        (FriendRequest.status == "accepted")
    ).all()

    friend_ids = set()
    for r in accepted:
        if r.from_user_id != user.user_id:
            friend_ids.add(r.from_user_id)
        elif r.to_user_id != user.user_id:
            friend_ids.add(r.to_user_id)

    friends = User.query.filter(User.user_id.in_(friend_ids)).all()

    return jsonify({
        "received_requests": [            {"id": r.id, "from_user": r.from_user.username if r.from_user else "(unknown)"} for r in received        ],
        "sent_requests": [            {"id": r.id, "to_user": r.to_user.username if r.to_user else "(unknown)", "status": r.status} for r in sent        ],
        "friends": [{"username": f.username, "user_id": f.user_id} for f in friends]
    })

@friends_bp.route("/add_friend", methods=["POST"])
@login_required
def add_friend():
    from_user = current_user
    data = request.get_json()
    to_username = data.get("to_username")
    if not to_username:
        return jsonify({"status": "error", "message": "No username provided"})

    to_user = User.query.filter_by(username=to_username).first()
    if not to_user:
        return jsonify({"status": "error", "message": "User not found"})

    if to_user.user_id == from_user.user_id:
        return jsonify({"status": "error", "message": "You cannot add yourself"})

    existing = FriendRequest.query.filter_by(
        from_user_id=from_user.user_id,
        to_user_id=to_user.user_id
    ).first()

    if existing:
        return jsonify({"status": "error", "message": "Friend request already sent"})

    new_request = FriendRequest(
        from_user_id=from_user.user_id,
        to_user_id=to_user.user_id,
        status="pending"
    )
    db.session.add(new_request)
    db.session.commit()

    return jsonify({"status": "success", "message": "Friend request sent!"})

@friends_bp.route("/respond_request", methods=["POST"])
@login_required
def respond_request():
    user = current_user

    data = request.get_json()
    request_id = data.get("request_id")
    action = data.get("action")  # 'accept' or 'reject'

    friend_request = FriendRequest.query.filter_by(id=request_id, to_user_id=user.user_id).first()
    if not friend_request:
        return jsonify({"status": "error", "message": "Request not found"}), 404

    if action == "accept":
        friend_request.status = "accepted"
    elif action == "reject":
        friend_request.status = "rejected"
    else:
        return jsonify({"status": "error", "message": "Invalid action"}), 400

    db.session.commit()
    return jsonify({"status": "success", "message": f"Request {action}ed"})

@friends_bp.route("/respond_friend_request", methods=["POST"])
@login_required
def respond_friend_request():
    user = current_user

    request_id = request.form.get("request_id")
    action = request.form.get("action")  # 'accept' or 'reject'

    friend_request = FriendRequest.query.filter_by(id=request_id, to_user_id=user.user_id).first()
    if not friend_request:
        return "Request not found", 404

    if action == "accept":
        friend_request.status = "accepted"
    elif action == "reject":
        friend_request.status = "rejected"
    else:
        return "Invalid action", 400

    db.session.commit()
    return redirect(url_for("friends_bp.friends"))