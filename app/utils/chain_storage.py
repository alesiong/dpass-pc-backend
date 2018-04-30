import time
from threading import Thread, Lock, Event
from typing import Optional, Union, Tuple, Generator, Dict, Set

from coincurve import PrivateKey, PublicKey
from flask import current_app
from web3.exceptions import BadFunctionCallOutput

from app import socketio
from app.models import KeyLookupTable
from app.utils.chain_utils import ChainUtils
from app.utils.misc import Address
from app.utils.settings import Settings


class ChainStorage:
    def __init__(self, account: PrivateKey):
        """
        **Assumptions**:

        1. Singleton class ChainUtils has been initialized before
        """
        self.__cache_dict: Dict[str, Tuple[str, bool]] = {}

        self.__change_set: Set[str] = set()
        self.__delete_set: Set[str] = set()

        self.__chain_utils = ChainUtils()
        self.__account = account

        self.__lock = Lock()
        self.__terminating = False

        self.__store_interval = 15
        self.__load_interval = 5
        self.__store_event = Event()
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

        self.__load_thread = Thread(target=self.load_worker, daemon=True)
        self.__store_thread = Thread(target=self.store_worker, daemon=True)
        self.__load_thread.start()
        self.__store_thread.start()

        self.__loaded = False

        self.__app = current_app._get_current_object()

    def add(self, k: str, v: str):
        """
        Add a new entry with key `k` and value `v` into the database. If the entry with key `k` exists,
        update its value with `v`. **This will not immediately write the underlying database.**
        """

        with self.__lock:
            if k in self.__cache_dict and self.__cache_dict[k][1]:
                self.__change_set.add(k)
            elif k in self.__delete_set:
                self.__delete_set.remove(k)
                self.__change_set.add(k)
            self.__cache_dict[k] = (v, False)
        socketio.emit('persistence change', k)

    def delete(self, k: str):
        """
        Delete an entry in database with key `k`. If the key does not exist, an exception `KeyError` will be thrown.
        **This will not immediately write the underlying database.**
        """
        with self.__lock:
            if k in self.__cache_dict:
                if not self.__cache_dict[k][1]:
                    if k in self.__change_set:
                        # changed in cache
                        self.__delete_set.add(k)
                        del self.__cache_dict[k]
                        self.__change_set.remove(k)
                    else:
                        # new in cache, not changed in cache
                        del self.__cache_dict[k]
                else:
                    self.__delete_set.add(k)
                    del self.__cache_dict[k]
            else:
                raise KeyError(k)

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

    def __get_all_add(self) -> Generator[Tuple[str, str], None, None]:
        return ((k, v[0]) for k, v in self.__cache_dict.items() if not v[1])

    def __get_all_del(self) -> Generator[str, None, None]:
        return (k for k in self.__delete_set)

    def store(self):
        """
        Synchronize the changes with underlying database.
        """

        # FIXME: use async add
        # TODO: how to determine if a key is really stored? only update persistence if transaction mined?
        add_list = []
        with self.__lock:
            for k, v in self.__get_all_add():
                print('adding:', k, v)
                add_list.append((k, v, self.__chain_utils.add_async(self.__account, k, v)))

            for k in self.__get_all_del():
                print('deleting:', k)
                add_list.append((None, None, self.__chain_utils.add_async(self.__account, k)))

            self.__change_set = set()
            self.__delete_set = set()

        return add_list

    def estimate_cost(self, args: dict) -> int:
        """
        Estimates the cost of the storage operation with arguments `args`.
        """
        # FIXME: it returns gas count (gas count * gas price = cost in wei)
        key = args['key']
        value = args['value']
        return self.__chain_utils.estimate_add_cost(self.__account, key, value)

    def calculate_total_cost(self) -> int:
        """
        Calculates the cost of currently cached storage operations.
        """
        # FIXME: it returns gas count (gas count * gas price = cost in wei)
        s = 0
        for k, v in self.__get_all_add():
            s += self.__chain_utils.estimate_add_cost(self.__account, k, v)
        for k in self.__get_all_del():
            s += self.__chain_utils.estimate_add_cost(self.__account, k)
        return s

    def balance(self) -> int:
        """
        Returns the balance (remaining storage space) of current user.
        """
        # FIXME: it returns wei
        return self.__chain_utils.get_balance(self.__account.public_key)

    def get_constructor_arguments(self) -> PublicKey:
        """
        Returns the arguments list to pass to the constructor.
        """
        # TODO: is it necessary to return password?
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

    def store_worker(self):
        while True:
            try:
                self.__store_event.set()

                add_list = self.store()

                if self.__terminating:
                    # Terminating, hopefully someone will mine our transaction :)
                    return

                finished = set()
                while len(finished) < len(add_list):
                    for k, v, h in add_list:
                        if h not in finished and self.__chain_utils.is_transaction_mined(h):
                            finished.add(h)
                            if k:
                                with self.__lock:
                                    if self.__cache_dict.get(k)[0] == v:
                                        self.__cache_dict[k] = (v, True)
                                socketio.emit('persistence change', k)
                    time.sleep(0.01)

                self.__store_event.clear()
                time.sleep(self.__store_interval)
            except Exception as e:
                print(e)
                time.sleep(self.__store_interval)

    def load_key_value(self, k: str, v: str):
        self.__blockchain.append((k, v))
        if v == '':
            del self.__cache_dict[k]
            if not k.startswith('__'):
                KeyLookupTable.query.filter_by(key=k).delete()
        else:
            self.__cache_dict[k] = (v, True)
            if not k.startswith('__'):
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
                    self.__store_event.wait()
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

            except BadFunctionCallOutput:
                break
            except Exception as e:
                print(e)
            finally:
                self.__loaded = True
                time.sleep(self.__load_interval)

    def terminate(self):
        self.__terminating = True
        self.__load_thread.join()
        self.__store_thread.join()

    def __del__(self):
        self.terminate()

    @property
    def loaded(self):
        return self.__loaded
