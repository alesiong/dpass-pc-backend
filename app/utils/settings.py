import json
import os
from pathlib import Path

from flask import current_app

from app.utils.misc import Singleton


class Settings(metaclass=Singleton):
    def __init__(self, filename=None):
        assert filename is not None
        if not os.path.exists(filename):
            directory = Path(filename[:filename.rfind('/')])
            directory.mkdir(parents=True, exist_ok=True)
            with open(filename, 'w') as f:
                json.dump({}, f)
            current_app.config['INIT_STATE'] = 1
        else:
            current_app.config['INIT_STATE'] = 2

        self.__filename = filename
        self.__master_password_hash: str = None
        self.__master_password_hash_salt: str = None
        self.read()

    def read(self):
        with open(self.__filename) as f:
            settings = json.load(f)
        master_password = settings.get('master_password')
        if master_password:
            self.__master_password_hash = master_password.get('hash')
            self.__master_password_hash_salt = master_password.get('salt')

    def write(self):
        with open(self.__filename, 'w') as f:
            json.dump({
                'master_password': {
                    'hash': self.__master_password_hash,
                    'salt': self.__master_password_hash_salt
                }
            }, f)

    @property
    def master_password_hash(self) -> str:
        return self.__master_password_hash

    @master_password_hash.setter
    def master_password_hash(self, v: str):
        self.__master_password_hash = v

    @property
    def master_password_hash_salt(self) -> str:
        return self.__master_password_hash_salt

    @master_password_hash_salt.setter
    def master_password_hash_salt(self, v: str):
        self.__master_password_hash_salt = v
