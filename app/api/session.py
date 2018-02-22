import base64
import binascii
from multiprocessing import Queue

from flask import Blueprint, current_app, request, jsonify

from app import SessionKey
from app.utils.cipher import encrypt_and_authenticate
from app.utils.decorators import session_verify
from app.utils.error_respond import authentication_failure

bp = Blueprint('api.session', __name__, url_prefix='/api/session')


@bp.route('/refresh/', methods=['POST'])
@session_verify
def refresh_session():
    """
    API end point: /api/session/refresh/
    Method: POST
    POST body (payload):
        type: json
        {
        "data": "xxx",
        "hmac": "xxx"
        }
        `data` is the encryption of string 'refresh' by the session key and Base64 encoded. `hmac` is its authentication
        token, also Base64 encoded.

    Response:
        type: json
        {
        "data": "xxx",
        "hmac": "xxx"
        }
        `data` is the encrpytion of the new session key. `hmac` is similar to above. Both fields are Base64 encoded.
        The session key itself is Hex encoded.
    """
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

    authentication_failure()
