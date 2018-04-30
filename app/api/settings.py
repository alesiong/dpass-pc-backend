from flask import Blueprint, current_app, jsonify, request, json

from app import ChainUtils
from app.utils.ethereum_utils import EthereumUtils
from app.utils import error_respond
from app.utils.decorators import session_verify

bp = Blueprint('api.settings', __name__, url_prefix='/api/settings')


@bp.route('/')
def get_settings():
    type_ = request.args.get('type')
    if type_ == 'init_state':
        return jsonify(state=current_app.config['INIT_STATE'])
    elif type_ == 'mining':
        if current_app.config['USE_ETHEREUM']:
            ethereum_utils = EthereumUtils()
        else:
            ethereum_utils = ChainUtils()
        return jsonify(mining=ethereum_utils.is_mining)
    else:
        error_respond.invalid_arguments()


@bp.route('/', methods=['POST'])
@session_verify
def change_settings():
    if current_app.config['USE_ETHEREUM']:
        ethereum_utils = EthereumUtils()
    else:
        ethereum_utils = ChainUtils()
    data = json.loads(request.decrypted_data.decode())
    setting_type = data.get('type')
    setting_args = data.get('args')
    if setting_type is None:
        error_respond.invalid_post_data()
    if setting_type == 'mining':
        if setting_args is None:
            error_respond.invalid_post_data()
        if setting_args:
            ethereum_utils.start_mining(current_app.config['STORAGE'].get_constructor_arguments())
        else:
            ethereum_utils.stop_mining()
    elif setting_type == 'lock':
        current_app.config['MASTER_PASSWORD'].lock()
    return jsonify(message='Success')
