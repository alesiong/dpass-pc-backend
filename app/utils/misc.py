import hashlib
import json


def sha2(s: str) -> str:
    return hashlib.sha256(hashlib.sha256(s.encode()).digest()).hexdigest()


def hash_dict(d: dict) -> str:
    return sha2(json.dumps(d, sort_keys=True))
