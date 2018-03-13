import base64
import json
from typing import Union

from flask import jsonify

from app.utils.cipher import encrypt_and_authenticate
from app.utils.misc import Singleton
from Crypto import Random
import binascii


class SessionKey(metaclass=Singleton):
    """
    Manage the session key between frontend and backend. The session key is of random 16 bytes and is encoded by Hex
    (binascii.hexlify), so the str representation is of 32 characters long.
    """

    def __init__(self, init_key=None):
        assert init_key is not None
        self.__session_key = init_key

    def refresh(self) -> str:
        self.__session_key = self.generate_key()
        return self.__session_key

    @property
    def session_key(self) -> str:
        return self.__session_key

    @staticmethod
    def generate_key() -> str:
        return binascii.hexlify(Random.get_random_bytes(16)).decode()

    def encrypt_response(self, response_data: Union[bytes, dict, list]):
        if not isinstance(response_data, bytes):
            response_data = json.dumps(response_data).encode()
        data, hmac = encrypt_and_authenticate(response_data, binascii.unhexlify(self.session_key))
        return jsonify(data=base64.encodebytes(data).decode().replace('\n', ''),
                       hmac=base64.encodebytes(hmac).decode().replace('\n', ''))
