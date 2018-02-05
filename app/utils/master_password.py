import datetime
from typing import Optional

from Crypto.Hash import SHA512, SHA256

from app.utils.cipher import salted_hash, encrypt_fixed_iv, decrypt_fixed_iv
from app.utils.decorators import check_and_unset_state


class MasterPassword:
    """
    Basic ideas:

    1. master password can only be stored in the memory for long time in the form which cannot be converted back to the
       plaintext of the master password, i.e. master password can be stored in the form of:

       a. hash digest
       b. salted hash digest

       cannot be stored in the form of:

       a. plaintext (except temporary storage, like user input)
       b. invertible encryption (either symmetric or asymmetric encryption)

    """

    def __init__(self, password_hash: bytes, salt: bytes, encryption_key: bytes):
        self.__password_hash = password_hash
        self.__salt = salt
        self.__encryption_key = encryption_key
        self.__expire_time = int((datetime.datetime.now() + datetime.timedelta(minutes=10)).timestamp())

        self._checked_expire = False

    @classmethod
    def new_password(cls, master_password_in_memory: str) -> 'MasterPassword':
        password_hash, salt = salted_hash(master_password_in_memory)
        encryption_key = cls.generate_encryption_key(master_password_in_memory)
        del master_password_in_memory
        # TODO: stores the 2 in the settings

        return cls(password_hash, salt, encryption_key)

    @classmethod
    def verify(cls, master_password_in_memory: str) -> Optional['MasterPassword']:
        salt = b''  # TODO: load the salt from the settings
        password_hash = b''  # TODO: load the hash from the settings
        password_hash_new, _ = salted_hash(master_password_in_memory, salt)
        if password_hash != password_hash_new:
            return None  # not verified
        encryption_key = cls.generate_encryption_key(master_password_in_memory)
        del master_password_in_memory

        return cls(password_hash, salt, encryption_key)

    @staticmethod
    def generate_encryption_key(master_password_in_memory: str, num_iter: int = 10000) -> bytes:
        sha512 = SHA512.new(data=master_password_in_memory.encode())
        del master_password_in_memory
        for _ in range(num_iter - 1):
            sha512 = SHA512.new(sha512.digest())
        return SHA256.new(sha512.digest()).digest()

    @check_and_unset_state('_checked_expire')
    def simple_encrypt(self, message: str) -> bytes:
        """
        Use master password (actually its hash) to encrypt a message
        """
        return encrypt_fixed_iv(message.encode(), self.__encryption_key)

    @check_and_unset_state('_checked_expire')
    def simple_decrypt(self, ciphertext: bytes) -> bytes:
        return decrypt_fixed_iv(ciphertext, self.__encryption_key)

    @check_and_unset_state('_checked_expire')
    def encrypt(self, message: str, key: str):
        encrypt_key = SHA256.new(data=key.encode() + self.__encryption_key).digest()
        return encrypt_fixed_iv(message.encode(), encrypt_key)

    @check_and_unset_state('_checked_expire')
    def decrypt(self, ciphertext: bytes, key: str):
        decrypt_key = SHA256.new(data=key.encode() + self.__encryption_key).digest()
        return decrypt_fixed_iv(ciphertext, decrypt_key)

    def check_expire(self) -> bool:
        """
        Return True if the master password has expired, should generate a new MasterPassword object
        """
        expired = datetime.datetime.now().timestamp() > self.__expire_time
        if expired:
            del self.__encryption_key
        else:
            self._checked_expire = True

        return expired
