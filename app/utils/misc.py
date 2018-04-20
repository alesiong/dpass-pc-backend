import base64
import hashlib
import json
import os
import platform
from typing import NewType, Union


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


def get_os() -> str:
    os = platform.system()
    if os == 'Darwin':
        return 'macos'
    elif os == 'Windows':
        if platform.architecture()[0] == '64bit':
            return 'win64'
        else:
            return 'win32'
    elif os == 'Linux':
        return 'linux'


def get_executable(path: str, name: str) -> str:
    os = get_os()
    result = '/'.join((path, os, name))
    if os.startswith('win'):
        result += '.exe'
        result = result.replace('/', '\\')
    return result


def get_env() -> dict:
    result = {}
    if os.path.exists('.env'):
        for line in open('.env'):
            var = line.strip().split('=', 1)
            if len(var) == 2:
                result[var[0]] = var[1]
    return result


def get_ipc(path: str, name: str) -> str:
    if get_os().startswith('win'):
        return '\\\\.\\pipe\\' + name
    return '/'.join((path, name))


def base64_encode(data: Union[bytes, str]) -> str:
    if isinstance(data, str):
        data = data.encode()
    return base64.encodebytes(data).decode().replace('\n', '')


def base64_decode(data: Union[bytes, str]) -> bytes:
    if isinstance(data, str):
        data = data.encode()
    return base64.decodebytes(data)
