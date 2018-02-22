from flask import Blueprint, current_app, jsonify

from app.models import KeyLookupTable

bp = Blueprint('api.password', __name__, url_prefix='/api/password')


@bp.route('/get_table/')
def get_table():
    hidden = current_app.config['HIDDEN']
    if hidden:
        return jsonify(password_list=KeyLookupTable.query.filter_by(hidden=False).first())
    else:
        return jsonify(password_list=KeyLookupTable.query.all())
