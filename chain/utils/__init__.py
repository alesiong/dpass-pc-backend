import os
import time
from typing import Callable, Generator

import gevent
from Crypto.Hash import SHA3_512
from rlp.utils import big_endian_to_int

DifficultyUnit = 1 << 512


def get_target(difficulty: int) -> int:
    return DifficultyUnit // difficulty


def chain_hash(data: bytes) -> bytes:
    return SHA3_512.new(data=SHA3_512.new(data=data).digest()).digest()


def chain_hash_object(data: bytes):
    return SHA3_512.new(data=SHA3_512.new(data=data).digest())


def mine(target: int, get_data: Callable[[bytes], bytes]) -> Generator[bytes, None, None]:
    i = 0
    byte_num = 8
    while True:
        if i > (1 << (byte_num >> 1)):  # i > 2^(byte_num/2)
            byte_num *= 2
        try_ = os.urandom(byte_num)
        data = get_data(try_)
        result = big_endian_to_int(chain_hash(data))
        if result < target:
            yield try_
        i += 1
        yield


def timestamp():
    return int(time.time() * 1000)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
