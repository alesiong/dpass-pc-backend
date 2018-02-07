from typing import Tuple, Optional

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256, SHA3_512
from Crypto.Util import Padding

__fixed_iv = b'*\xfe\xce\xa09\xdep+\x14\xd7SvY6\xcd\xa3'


def salted_hash(password: str, salt: bytes = None, num_iter: int = 10000) -> Tuple[bytes, bytes]:
    """
    Generates the salted hash of a plaintext `password`. If parameter `salt` is not set, a random salt will be used.
    `num_iter` is the number of iterations to apply the hash algorithm.

    The hash algorithm used here is the SHA3-512, so the resulted hash is 64 bytes long and the salt is of the same
    size.

    :return: Salted hash of the `password` and the salt used.
    """
    if not salt:
        salt = Random.get_random_bytes(64)
    password_hash = password.encode()
    for i in range(num_iter):
        password_hash = SHA3_512.new(data=password_hash).digest()
        if i > num_iter // 2:
            password_hash = password_hash + salt
    return password_hash, salt


def encrypt(message: bytes, key: bytes, iv: bytes) -> bytes:
    """
    Encrypt the `message` with AES-CBC algorithm. **Note that the type of parameter `message` is `bytes`.**
    `key` is the key used in AES algorithm, it should be of length 16, 24, or 32 bytes. `iv` should be of length
    16 bytes.
    """
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    return cipher.encrypt(Padding.pad(message, 16))


def decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    """
    Decrypt the `ciphertext` with AES-CBC algorithm. `key` and `iv` are exactly the same as `encrypt`.
    **Note that the return type is `bytes`.**
    """
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    return Padding.unpad(cipher.decrypt(ciphertext), 16)


def encrypt_fixed_iv(message: bytes, key: bytes) -> bytes:
    """
    Similar to `encrypt` but with fixed(constant) iv.
    """
    return encrypt(message, key, __fixed_iv)


def decrypt_fixed_iv(ciphertext: bytes, key: bytes) -> bytes:
    """
    Similar to `decrypt` but with fixed(constant) iv.
    """
    return decrypt(ciphertext, key, __fixed_iv)


def encrypt_and_authenticate(message: bytes, key: bytes) -> Tuple[bytes, bytes]:
    """
    Encrypt `message` in the same way as `encrypt_fixed_iv` with `key`, and then use HMAC to generate an authentication
    token. The HMAC key and AES key are the same: `key`.

    The digest(hash) algorithm for HMAC is SHA256, and authentication token is generated from the ciphertext, not
    `message`.

    :return: Encrypted `message` and its HMAC token.
    """
    cipher = encrypt_fixed_iv(message, key)
    hmac = HMAC.new(key, digestmod=SHA256)
    hmac.update(cipher)
    return cipher, hmac.digest()


def decrypt_and_verify(ciphertext: bytes, mac: bytes, key: bytes) -> Optional[bytes]:
    """
    Decrypt `ciphertext` in the same way as `decrypt_fixed_iv` with `key`. And then verifies if `mac` is the correct
    HMAC token.

    :return: Decrypted `ciphertext` if the HMAC token `mac` is correct. `None` if the verification fails.
    """
    try:
        message = decrypt_fixed_iv(ciphertext, key)
        hmac = HMAC.new(key, digestmod=SHA256)
        hmac.update(ciphertext)
        hmac.verify(mac)
        return message
    except ValueError:
        return None
