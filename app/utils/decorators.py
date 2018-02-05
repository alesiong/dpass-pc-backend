import base64
from functools import wraps

import binascii
from flask import request, jsonify

from app import SessionKey
from app.utils.cipher import decrypt_and_verify


def session_verify(func):
    @wraps(func)
    def __wrapper(*args, **kwargs):

        try:
            data: str = request.get_json()['data']
            hmac: str = request.get_json()['hmac']
            key = SessionKey().session_key
            decrypted = decrypt_and_verify(base64.decodebytes(data.encode()),
                                           base64.decodebytes(hmac.encode()),
                                           binascii.unhexlify(key))
            if decrypted:
                request.decrypted_data = decrypted
            else:
                return jsonify(error=''), 401

        except (KeyError, AttributeError):
            return jsonify(error=''), 400
        except ValueError:
            return jsonify(error=''), 401

        return func(*args, **kwargs)

    return __wrapper
