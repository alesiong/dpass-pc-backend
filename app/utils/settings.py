import json
import os
from pathlib import Path
from unqlite import UnQLite

from flask import current_app

from app.utils.misc import Singleton


class Settings(metaclass=Singleton):
    def __init__(self, filename=None):
        assert filename is not None
        if not os.path.exists(filename):
            directory = Path(filename[:filename.rfind('/')])
            directory.mkdir(parents=True, exist_ok=True)

        self.__db = UnQLite(filename)

        if self.__db_get('master_password_hash'):
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

    @property
    def ethereum_address(self) -> str:
        return self.__db_get('ethereum_address')

    @ethereum_address.setter
    def ethereum_address(self, v: str):
        self.__db['ethereum_address'] = v

    @property
    def blockchain_length(self) -> int:
        return int(self.__db_get('blockchain_length', 0))

    @blockchain_length.setter
    def blockchain_length(self, v: int):
        self.__db['blockchain_length'] = str(v)

    @property
    def blockchain(self) -> list:
        return json.loads(self.__db_get('blockchain', '[]'))

    @blockchain.setter
    def blockchain(self, v: list):
        self.__db['blockchain'] = json.dumps(v)

    @property
    def chain_private_key(self) -> str:
        return self.__db_get('chain_private_key')

    @chain_private_key.setter
    def chain_private_key(self, v: str):
        self.__db['chain_private_key'] = v

    def __del__(self):
        self.__db.close()

    def __db_get(self, key, default=None):
        if key in self.__db:
            return self.__db[key]
        return default
