from typing import Tuple, Optional

from Crypto import Util
from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256

__fixed_iv = b'*\xfe\xce\xa09\xdep+\x14\xd7SvY6\xcd\xa3'


def encrypt(message: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    return cipher.encrypt(Util.Padding.pad(message, 16))


def decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    return Util.Padding.unpad(cipher.decrypt(ciphertext), 16)


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
