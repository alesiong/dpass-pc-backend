# from threading import Thread, Lock, Event
from typing import Optional, Union, Tuple, Dict

import gevent
from coincurve import PrivateKey, PublicKey
from flask import current_app
from gevent.lock import BoundedSemaphore

from app import socketio
from app.models import KeyLookupTable
from app.utils.chain_utils import ChainUtils
from app.utils.settings import Settings


class ChainStorage:
    def __init__(self, account: PrivateKey):
        """
        **Assumptions**:

        1. Singleton class ChainUtils has been initialized before
        """
        self.__cache_dict: Dict[str, Tuple[str, bool]] = {}

        self.__chain_utils = ChainUtils()
        self.__account = account

        self.__lock = BoundedSemaphore()
        self.__terminating = False

        self.__load_interval = 5
        self.__blockchain_length = Settings().blockchain_length
        self.__blockchain = Settings().blockchain

        # load blockchain from disk
        for k, v in self.__blockchain:
            if v == '':
                del self.__cache_dict[k]
            else:
                self.__cache_dict[k] = (v, True)

        # make up for the missing entries (delete entries that have not sync'ed)
        for k in self.__cache_dict:
            if not k.startswith('__') and KeyLookupTable.query.get(k) is None:
                new_entry = KeyLookupTable(key=k, meta_data='', hidden=False)
                KeyLookupTable.query.session.add(new_entry)

        KeyLookupTable.query.session.commit()

        self.__load_thread = gevent.spawn(self.load_worker)
        self.__load_thread.start()

        self.__loaded = False

        self.__app = current_app._get_current_object()

    def add(self, k: str, v: str):
        """
        Add a new entry with key `k` and value `v` into the database. If the entry with key `k` exists,
        update its value with `v`. **This will not immediately write the underlying database.**
        """

        with self.__lock:
            self.__cache_dict[k] = (v, False)
            self.__chain_utils.add_async(self.__account, k, v)
        socketio.emit('persistence change', k)

    def delete(self, k: str):
        """
        Delete an entry in database with key `k`. If the key does not exist, an exception `KeyError` will be thrown.
        **This will not immediately write the underlying database.**
        """
        with self.__lock:
            if k in self.__cache_dict:
                del self.__cache_dict[k]
            else:
                raise KeyError(k)
            self.__chain_utils.add_async(self.__account, k)

    def get(self, k: str, check_persistence: bool = False) -> Union[Optional[str], Tuple[Optional[str], bool]]:
        """
        Get an existing entry with key `k` in the database. If the entry with key `k` exists, return its value.
        If the key does not exist, return `None`. If `check_persistence` is `True`,
        returns a tuple like `(value, True)`, where the second element shows whether this key-value pair has been
        `store`d into the underlying database. If `check_persistence` is `True` and the key does not exist, return
        `(None, None)`.
        """

        result = self.__cache_dict.get(k, (None, None))
        if check_persistence:
            return result
        else:
            return result[0]

    def get_all(self) -> dict:
        """
        Return all keys with their values and persistence in the database. The returned value should have a structure
        like this:

        {
            key: (value, persistence)
        }

        """
        return self.__cache_dict

    def store(self):
        """
        Synchronize the changes with underlying database.
        """

        pass

    def estimate_cost(self, args: dict) -> int:
        """
        Estimates the cost of the storage operation with arguments `args`.
        """
        key = args['key']
        value = args['value']
        return self.__chain_utils.estimate_add_cost(self.__account, key, value)

    def calculate_total_cost(self) -> int:
        """
        Calculates the cost of currently cached storage operations.
        """
        # TODO: not available
        return 0

    def balance(self) -> int:
        """
        Returns the balance (remaining storage space) of current user.
        """
        return self.__chain_utils.get_balance(self.__account.public_key)

    def get_constructor_arguments(self) -> PublicKey:
        """
        Returns the arguments list to pass to the constructor.
        """
        return self.__account.public_key

    def size(self) -> int:
        return len(self.__cache_dict)

    def __setitem__(self, key, value):
        self.add(key, value)

    def __delitem__(self, key):
        self.delete(key)

    def __getitem__(self, item):
        self.get(item)

    def __len__(self):
        return self.size()

    def load_key_value(self, k: str, v: str):
        self.__blockchain.append((k, v))
        if v == '':
            del self.__cache_dict[k]
            if not k.startswith('__'):
                KeyLookupTable.query.filter_by(key=k).delete()
        else:
            self.__cache_dict[k] = (v, True)
            if not k.startswith('__'):
                socketio.emit('persistence change', k)
                old_entry = KeyLookupTable.query.get(k)
                if old_entry:
                    old_entry.meta_data = ''
                else:
                    new_entry = KeyLookupTable(key=k, meta_data='', hidden=False)
                    KeyLookupTable.query.session.add(new_entry)

    def load_worker(self):
        while True:
            try:
                if self.__terminating:
                    return
                storage = self.__chain_utils.get_storage(self.__account.public_key)
                new_length = len(storage)
                print('load', self.__blockchain_length, new_length)
                if new_length > self.__blockchain_length:
                    with self.__lock:
                        with self.__app.app_context():
                            for k, v in storage[self.__blockchain_length:]:
                                print('loading:', k, v)
                                self.load_key_value(k, v)

                            self.__blockchain_length = new_length
                            KeyLookupTable.query.session.commit()
                            Settings().blockchain_length = new_length
                            Settings().blockchain = self.__blockchain
                            Settings().write()
                    socketio.emit('refresh password')

            except Exception as e:
                print(e)
            finally:
                self.__loaded = True
                gevent.sleep(self.__load_interval)

    def terminate(self):
        self.__terminating = True
        self.__load_thread.join()

    def __del__(self):
        self.terminate()

    @property
    def loaded(self):
        return self.__loaded
