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
