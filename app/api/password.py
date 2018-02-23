import base64
import binascii
from flask import Blueprint, current_app, jsonify, request, json

from app import SessionKey
from app.models import KeyLookupTable
from app.utils.cipher import encrypt_and_authenticate
from app.utils.decorators import session_verify

bp = Blueprint('api.password', __name__, url_prefix='/api/password')


@bp.route('/')
@session_verify
def get_table():
    session_key = SessionKey()
    key = session_key.session_key
    check_expire = current_app.config['MASTER_PASSWORD'].check_expire()
    if not check_expire:
        hidden = request.args['hidden']
        if hidden:
            data, hmac = encrypt_and_authenticate(json.dumps(KeyLookupTable.query.filter_by(hidden=False)).encode(),
                                                  binascii.unhexlify(key))
            return jsonify(data=base64.encodebytes(data).decode().strip(),
                           hmac=base64.encodebytes(hmac).decode().strip())
        else:
            data, hmac = encrypt_and_authenticate(json.dumps(KeyLookupTable.query.all()).encode(),
                                                  binascii.unhexlify(key))
            return jsonify(data=base64.encodebytes(data).decode().strip(),
                           hmac=base64.encodebytes(hmac).decode().strip())
