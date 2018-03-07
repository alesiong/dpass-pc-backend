from flask import Blueprint, current_app, jsonify, request

from app.utils import error_respond

bp = Blueprint('api.settings', __name__, url_prefix='/api/settings')


@bp.route('/')
def get_settings():
    type_ = request.args.get('type')
    if type_ == 'init_state':
        return jsonify(state=current_app.config['INIT_STATE'])
    else:
        error_respond.invalid_arguments()
