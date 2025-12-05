from flask import Blueprint, request
from extensions import db
from models.user import User
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.exceptions import HTTPException

bp = Blueprint('api', __name__)


def error_handler(status_code = 500, message = None):
    db.session.rollback()
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    return payload, status_code

@bp.errorhandler(HTTPException)
def handle_exceptions(e):
    return error_handler(e.code)

@bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    return db.get_or_404(User, id).to_dict()

@bp.route('/users/<int:id>/followers', methods=['GET'])
def get_user_followers(id):
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)

    return db.get_or_404(User, id).to_collection_dict(page, per_page)
