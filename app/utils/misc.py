import hashlib
import json
from typing import NewType


def sha2(s: str) -> str:
    return hashlib.sha256(hashlib.sha256(s.encode()).digest()).hexdigest()


def hash_dict(d: dict) -> str:
    return sha2(json.dumps(d, sort_keys=True))


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# string like '0x12345...'
HashType = NewType('Hash', str)
Address = HashType
