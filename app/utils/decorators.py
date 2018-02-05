import base64
import binascii
import time
from functools import wraps

from flask import request, jsonify

from app import SessionKey
from app.utils.cipher import decrypt_and_verify
from app.utils.exceptions import StateError


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


def check_state(state_name):
    def __decorator(func):
        @wraps(func)
        def __wrapper(self, *args, **kwargs):
            if not getattr(self, state_name):
                raise StateError('Need ' + state_name + ' to be True.')
            if hasattr(self, state_name + '_until') and getattr(self, state_name + '_until') < time.time():
                setattr(self, state_name, False)
                raise StateError(state_name + ' has expired.')
            return func(self, *args, **kwargs)

        return __wrapper

    return __decorator


def check_and_unset_state(state_name):
    def __decorator(func):
        @wraps(func)
        @check_state(state_name)
        def __wrapper(self, *args, **kwargs):
            rtn = func(self, *args, **kwargs)
            setattr(self, state_name, False)
            return rtn

        return __wrapper

    return __decorator


def set_state(state_name, duration_name=None, duration_default=None):
    def __decorator(func):
        @wraps(func)
        def __wrapper(self, *args, **kwargs):
            rtn = func(self, *args, **kwargs)
            setattr(self, state_name, True)
            if duration_name is not None:
                duration = kwargs.get(duration_name)
                if duration is not None:
                    setattr(self, state_name + '_until', time.time() + duration)
                else:
                    setattr(self, state_name + '_until', time.time() + duration_default)

            return rtn

        return __wrapper

    return __decorator


def unset_state(state_name):
    def __decorator(func):
        @wraps(func)
        def __wrapper(self, *args, **kwargs):
            rtn = func(self, *args, **kwargs)
            setattr(self, state_name, False)
            return rtn

        return __wrapper

    return __decorator
