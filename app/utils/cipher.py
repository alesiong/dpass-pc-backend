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
