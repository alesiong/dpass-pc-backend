import binascii
from flask import Blueprint, current_app, request, jsonify
from multiprocessing import Queue

from app import SessionKey
from app.utils.cipher import decrypt_and_verify, encrypt_and_authenticate
import base64

from app.utils.decorators import session_verify

bp = Blueprint('api.session', __name__, url_prefix='/api/session')


@bp.route('/refresh/', methods=['POST'])
@session_verify
def refresh_session():
    session_key = SessionKey()
    key = session_key.session_key
    if request.decrypted_data == b'refresh':
        queue: Queue = current_app.config['QUEUE']
        new_key = session_key.refresh()
        while not queue.empty():
            queue.get()
        queue.put(new_key)
        data, hmac = encrypt_and_authenticate(new_key.encode(), binascii.unhexlify(key))
        return jsonify(data=base64.encodebytes(data).decode().strip(),
                       hmac=base64.encodebytes(hmac).decode().strip())

    return jsonify(error=''), 401
