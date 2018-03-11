import json
import os
from pathlib import Path

from flask import current_app
from unqlite import UnQLite

from app import LocalStorage
from app.utils.misc import Singleton


class Settings(metaclass=Singleton):
    def __init__(self, filename=None):
        assert filename is not None
        if not os.path.exists(filename):
            directory = Path(filename[:filename.rfind('/')])
            directory.mkdir(parents=True, exist_ok=True)

        self.__db = UnQLite(filename)

        if self.__db_get('master_password_hash'):
            current_app.config['INIT_STATE'] = 1
            current_app.config['STORAGE'] = LocalStorage('chain')
            current_app.config['INIT_STATE'] = 2

    def write(self):
        self.__db.commit()

    @property
    def master_password_hash(self) -> str:
        return self.__db_get('master_password_hash')

    @master_password_hash.setter
    def master_password_hash(self, v: str):
        self.__db['master_password_hash'] = v

    @property
    def master_password_hash_salt(self) -> str:
        return self.__db_get('master_password_hash_salt')

    @master_password_hash_salt.setter
    def master_password_hash_salt(self, v: str):
        self.__db['master_password_hash_salt'] = v

    def __del__(self):
        self.__db.close()

    def __db_get(self, key, default=None):
        if key in self.__db:
            return self.__db[key]
        return default
