import json
import time
from threading import Thread

from flask import Blueprint, request, current_app, jsonify, abort

from app import socketio
from app.utils import error_respond
from app.utils.decorators import session_verify
from app.utils.ethereum_storage import EthereumStorage
from app.utils.ethereum_utils import initialize_ethereum_account
from app.utils.local_storage import LocalStorage
from app.utils.master_password import MasterPassword
from app.utils.settings import Settings

bp = Blueprint('api.master_password', __name__, url_prefix='/api/master_password')

MASTER_KEY = '__master_password_hash'
MASTER_SALT_KEY = '__master_password_hash_salt'


@bp.route('/new/', methods=['POST'])
@session_verify
def new():
    if current_app.config['INIT_STATE'] == 2:
        error_respond.master_password_already_set()

    master_password_in_memory = request.decrypted_data.decode()

    current_app.config['MASTER_PASSWORD'] = MasterPassword.new_password(master_password_in_memory)
    ethereum_pass = current_app.config['MASTER_PASSWORD'].ethereum_pass

    del request.decrypted_data
    del master_password_in_memory

    def initializing_worker(app):
        with app.app_context():
            settings = Settings()
            current_app.config['INIT_STATE'] = 1
            socketio.emit('state change', 1)
            if current_app.config['USE_ETHEREUM']:
                ethereum_account = initialize_ethereum_account(ethereum_pass)
                current_app.config['STORAGE'] = EthereumStorage(ethereum_account, ethereum_pass)
                settings.ethereum_address = ethereum_account
                settings.write()
            else:
                current_app.config['STORAGE'] = LocalStorage('chain')
            storage = current_app.config['STORAGE']
            storage.add(MASTER_KEY, settings.master_password_hash)
            storage.add(MASTER_SALT_KEY, settings.master_password_hash_salt)
            while True:
                if storage.get(MASTER_KEY, True)[1] and storage.get(MASTER_SALT_KEY, True)[1]:
                    break
                time.sleep(0.1)
            current_app.config['INIT_STATE'] = 2
            socketio.emit('state change', 2)

    Thread(target=initializing_worker, daemon=True, args=(current_app._get_current_object(),)).start()
    return jsonify(message='Success')


@bp.route('/verify/', methods=['POST'])
@session_verify
def verify():
    master_password_in_memory = request.decrypted_data.decode()

    master_pass = MasterPassword.verify(master_password_in_memory)
    ethereum_pass = master_pass.ethereum_pass

    del request.decrypted_data
    del master_password_in_memory

    if master_pass:
        current_app.config['MASTER_PASSWORD'] = master_pass
        if current_app.config['USE_ETHEREUM']:
            settings = Settings()
            current_app.config['STORAGE'] = EthereumStorage(settings.ethereum_address, ethereum_pass)
        else:
            current_app.config['STORAGE'] = LocalStorage('chain')
        return jsonify(message='Success')
    error_respond.master_password_wrong()


@bp.route('/verify_with_account/', methods=['POST'])
@session_verify
def verify_with_account():
    if not current_app.config['USE_ETHEREUM']:
        abort(404)
    data = json.loads(request.decrypted_data.decode())
    master_password_in_memory = data['password']
    account = data['account']
    del request.decrypted_data
    del data

    ethereum_pass = MasterPassword.generate_ethereum_password(master_password_in_memory)

    storage = None
    try:
        storage = EthereumStorage(account, ethereum_pass)
    except TypeError:
        error_respond.blockchain_account_wrong()

    while not storage.loaded:
        time.sleep(0.1)

    master_pass_hash = storage.get(MASTER_KEY)
    master_salt = storage.get(MASTER_SALT_KEY)
    if master_pass_hash and master_salt:
        settings = Settings()
        settings.master_password_hash = master_pass_hash
        settings.master_password_hash_salt = master_salt
        master_pass = MasterPassword.verify(master_password_in_memory)
        del master_password_in_memory
        if master_pass:
            current_app.config['MASTER_PASSWORD'] = master_pass
            current_app.config['STORAGE'] = storage
            settings.ethereum_address = account
            settings.write()
            current_app.config['INIT_STATE'] = 2
            socketio.emit('state change', 2)
            return jsonify(message='Success')
        else:
            settings.master_password_hash = ''
            settings.master_password_hash_salt = ''
            settings.write()
            storage.terminate()
            error_respond.master_password_wrong()

    storage.terminate()
    error_respond.blockchain_account_wrong()
