import base64
import binascii
from flask import Blueprint, current_app, jsonify, request, json

from app import SessionKey
from app.models import KeyLookupTable
from app.utils import error_respond
from app.utils.cipher import encrypt_and_authenticate
from app.utils.decorators import session_verify
from app.utils.master_password import MasterPassword

bp = Blueprint('api.password', __name__, url_prefix='/api/password')


@bp.route('/')
@session_verify
def get_table():
    key = SessionKey().session_key
    master_password: MasterPassword = current_app.config['MASTER_PASSWORD']
    expired = master_password.check_expire()
    if expired:
        error_respond.authentication_failure()
    hidden = request.args.get('hidden')
    if hidden:
        entries = KeyLookupTable.query.filter_by(hidden=False).all()
    else:
        entries = KeyLookupTable.query.all()

    entries = [
        {
            'key': entry.key,
            'metadata': json.loads(
                master_password.simple_decrypt(
                    base64.decodebytes(entry.meta_data.encode())).decode())
        } for entry in entries
    ]

    data, hmac = encrypt_and_authenticate(json.dumps(entries).encode(),
                                          binascii.unhexlify(key))
    return jsonify(data=base64.encodebytes(data).decode().strip(),
                   hmac=base64.encodebytes(hmac).decode().strip())
