from flask import Blueprint, current_app, jsonify, request, json

from app import EthereumUtils
from app.utils import error_respond
from app.utils.decorators import session_verify

bp = Blueprint('api.settings', __name__, url_prefix='/api/settings')


@bp.route('/')
def get_settings():
    type_ = request.args.get('type')
    if type_ == 'init_state':
        return jsonify(state=current_app.config['INIT_STATE'])
    elif type_ == 'mining':
        ethereum_utils = EthereumUtils()
        return jsonify(mining=ethereum_utils.is_mining)
    else:
        error_respond.invalid_arguments()


@bp.route('', methods=['POST'])
@session_verify
def change_settings():
    ethereum_utils = EthereumUtils()
    data = json.loads(request.decrypted_data.decode())
    setting_type = data['type']
    setting_args = data['args']
    if setting_type is None or setting_args is None:
        error_respond.invalid_post_data()
    if setting_type == 'mining' and setting_args is False:
        if ethereum_utils.is_mining:
            ethereum_utils.stop_mining()
            ethereum_utils.is_mining = False
    if setting_type == 'mining' and setting_args is True:
        if not ethereum_utils.is_mining:
            ethereum_utils.start_mining()
            ethereum_utils.is_mining = True
    return jsonify(message='Success')
