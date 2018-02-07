from flask import Blueprint, request, current_app, jsonify

from app.utils import error_respond
from app.utils.decorators import session_verify
from app.utils.master_password import MasterPassword

bp = Blueprint('api.master_password', __name__, url_prefix='/api/master_password')


@bp.route('/new/', methods=['POST'])
@session_verify
def new():
    current_app.config['MASTER_PASSWORD'] = MasterPassword.new_password(request.decrypted_data.decode())
    del request.decrypted_data
    # TODO: initialize Storage Layer
    return jsonify(message='Success')


@bp.route('/verify/', methods=['POST'])
@session_verify
def verify():
    master_pass = MasterPassword.verify(request.decrypted_data.decode())
    del request.decrypted_data
    if master_pass:
        current_app.config['MASTER_PASSWORD'] = master_pass
        return jsonify(message='Success')
    error_respond.authentication_failure()
