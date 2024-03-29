import binascii
import time
from functools import wraps

from flask import request, current_app

from app.utils.cipher import decrypt_and_verify
from app.utils.error_respond import invalid_post_data, authentication_failure, master_password_expired
from app.utils.exceptions import StateError
from app.utils.misc import base64_decode
from app.utils.session_key import SessionKey


def session_verify(func):
    """
    Decrypt and verify the POST data with session key encrypted. Respond with 401 if verification failed.
    Decrypted data is put in request.decrypted_data
    """

    @wraps(func)
    def __wrapper(*args, **kwargs):

        try:
            data: str = request.get_json()['data']
            hmac: str = request.get_json()['hmac']
            key = SessionKey().session_key
            decrypted = decrypt_and_verify(base64_decode(data),
                                           base64_decode(hmac),
                                           binascii.unhexlify(key))
            if decrypted:
                request.decrypted_data = decrypted
            else:
                authentication_failure()

        except (KeyError, TypeError):
            invalid_post_data()
        except ValueError:
            authentication_failure()

        return func(*args, **kwargs)

    return __wrapper


def master_password_verify(func):
    from app.utils.master_password import MasterPassword

    exempt_times = func if isinstance(func, int) else 1

    def __inner_wrapper(f, *args, **kwargs):
        try:
            master_password: MasterPassword = current_app.config['MASTER_PASSWORD']
        except KeyError:
            master_password_expired()
            return
        expired = master_password.check_expire(exempt_times)
        if expired:
            master_password_expired()

        return f(*args, **kwargs)

    if callable(func):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            return __inner_wrapper(func, *args, **kwargs)

        return __wrapper
    else:
        def __decorator(f):
            @wraps(f)
            def __wrapper(*args, **kwargs):
                return __inner_wrapper(f, *args, **kwargs)

            return __wrapper

        return __decorator


def check_state(state_name):
    """
    Simple decorator to ensure states inside a class before some methods are called.

    This decorator should only be used on a method in class. The class should has an attribute named `state_name`.
    The check passes if the attribute is `True`. If an attribute named `state_name` + '_util' also exists in the class,
    the check passes if the attribute `state_name` is `True` and `state_name` + '_util' is less then current time.

    :raise: `StateError` if the check failed
    """

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
    """
    Similar to the `@check_state`, but unset the state to `False` afterwards.
    """

    def __decorator(func):
        @wraps(func)
        @check_state(state_name)
        def __wrapper(self, *args, **kwargs):
            rtn = func(self, *args, **kwargs)
            state = getattr(self, state_name)
            if isinstance(state, int):
                setattr(self, state_name, max(state - 1, 0))
            else:
                setattr(self, state_name, False)
            return rtn

        return __wrapper

    return __decorator


def set_state(state_name, duration_name=None, duration_default=None):
    """
    Set the state to `True` after the function exit. If `duration_name` is set, the state will become a time limited
    state. The expire time is set in the keyword arguments called `duration_name` of the function. If the keyword
    arguments is not set, the expire time defaults to `duration_default`
    `duration_name` and `duration_default` should always be provided together.
    """

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
    """
    Unset the state to `False` after the function exit.
    """

    def __decorator(func):
        @wraps(func)
        def __wrapper(self, *args, **kwargs):
            rtn = func(self, *args, **kwargs)
            setattr(self, state_name, False)
            return rtn

        return __wrapper

    return __decorator
