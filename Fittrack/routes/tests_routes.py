from flask import Blueprint
from Fittrack import db

tests_bp = Blueprint('tests_bp', __name__)

@tests_bp.route('/_test/clear_db', methods=['POST'])
def clear_db():
    db.drop_all()
    db.create_all()
    return '', 204