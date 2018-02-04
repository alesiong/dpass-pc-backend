from typing import Tuple, Optional

from Crypto import Util
from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256
from Crypto.Util import Padding

__fixed_iv = b'*\xfe\xce\xa09\xdep+\x14\xd7SvY6\xcd\xa3'


def encrypt(message: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    return cipher.encrypt(Padding.pad(message, 16))


def decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    return Padding.unpad(cipher.decrypt(ciphertext), 16)


def encrypt_fixed_iv(message: bytes, key: bytes) -> bytes:
    return encrypt(message, key, __fixed_iv)


def decrypt_fixed_iv(ciphertext: bytes, key: bytes) -> bytes:
    return decrypt(ciphertext, key, __fixed_iv)


def encrypt_and_authenticate(message: bytes, key: bytes) -> Tuple[bytes, bytes]:
    cipher = encrypt_fixed_iv(message, key)
    hmac = HMAC.new(key, digestmod=SHA256)
    hmac.update(cipher)
    return cipher, hmac.digest()


def decrypt_and_verify(ciphertext: bytes, mac: bytes, key: bytes) -> Optional[bytes]:
    message = decrypt_fixed_iv(ciphertext, key)
    hmac = HMAC.new(key, digestmod=SHA256)
    hmac.update(ciphertext)
    try:
        hmac.verify(mac)
        return message
    except ValueError:
        return None
from Crypto import Random
from Crypto.Hash import SHA3_512


def salt_hash(password: str, salt: bytes = None, iteration: int = 1000):
    if not salt:
        salt = Random.get_random_bytes(64)
    password = password.encode()
    for i in range(iteration):
        h_obj = SHA3_512.new()
        h_obj.update(password)
        password = h_obj.digest()
        if i == iteration // 2:
            password = password + salt
    return password, salt
