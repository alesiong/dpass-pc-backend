from flask import Blueprint, current_app, jsonify

bp = Blueprint('api.settings', __name__, url_prefix='/api/settings')


@bp.route('/get_settings/')
def get_settings():
    state = current_app.config['INIT_STATE']
    return jsonify(state='%d' % state)
