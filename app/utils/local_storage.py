import ctypes
import json
import os
import platform
import sys
import time
from typing import Optional, Union, Tuple

from app.utils.misc import hash_dict


class LocalStorage:
    def __init__(self, filename=None):
        """
        Initialize the storage. If `filename` is not set or the targeting file does not exist,
        create a new database with empty storage, also create a new file for persistent storage.
        Otherwise load the contents from that file.
        """
        self.__cache_dict = {}

        self.__change_set = set()
        self.__delete_set = set()

        self.__database = LocalStorage.Database(filename)
        blockchain = self.__database.read()
        # Block 0 is the Genesis
        for i in range(1, len(blockchain)):
            element = blockchain[i]
            if element["arguments"]["value"] == "":
                del self.__cache_dict[element["arguments"]["key"]]
            else:
                self.__cache_dict[element["arguments"]["key"]] = (element["arguments"]["value"], True)
        self.__blockchain = blockchain

    def add(self, k: str, v: str):
        """
        Add a new entry with key `k` and value `v` into the database. If the entry with key `k` exists,
        update its value with `v`. **This will not immediately write the underlying database.**
        """

        if k in self.__cache_dict and self.__cache_dict[k][1]:
            self.__change_set.add(k)
        elif k in self.__delete_set:
            self.__delete_set.remove(k)
            self.__change_set.add(k)
        self.__cache_dict[k] = (v, False)

    def delete(self, k: str):
        """
        Delete an entry in database with key `k`. If the key does not exist, an exception `KeyError` will be thrown.
        **This will not immediately write the underlying database.**
        """

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

    def store(self):
        """
        Synchronize the changes with underlying database.
        """

        # 1. filter the dirty items in the cache_dict (persistence == False), these are `add` operation
        for k, v in self.__cache_dict.items():
            if not v[1]:
                self.__blockchain.append({
                    "pre_block": hash_dict(self.__blockchain[-1]),
                    "arguments": {
                        "key": k,
                        "value": v[0]
                    }
                })
                self.__cache_dict[k] = (v[0], True)

        # 2. items in delete_list are `del` operation
        for k in self.__delete_set:
            self.__blockchain.append({
                "pre_block": hash_dict(self.__blockchain[-1]),
                "arguments": {
                    "key": k,
                    "value": ""
                }
            })
        self.__database.write(self.__blockchain)
        self.__change_set = set()
        self.__delete_set = set()

    def estimate_cost(self, args: dict) -> int:
        """
        Estimates the cost of the storage operation with arguments `args`.
        """
        block = {
            "pre_block": "",
            "arguments": args
        }
        return (len(json.dumps(block)) + 64) * 8

    def calculate_total_cost(self) -> int:
        """
        Calculates the cost of currently cached storage operations.
        """
        fixed = len(json.dumps({
            "pre_block": '',
            "arguments": {
                "key": '',
                "value": ''
            }
        })) + 64
        s = 0
        for k, v in self.__cache_dict.items():
            if not v[1]:
                s += fixed + len(k) + len(v[0])

        for k in self.__delete_set:
            s += fixed + len(k)
        return s

    def balance(self) -> int:
        """
        Returns the balance (remaining storage space) of current user.
        """
        if platform.system() == 'Windows':
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(sys.path[0][:3]), None, None,
                                                       ctypes.pointer(free_bytes))
            return free_bytes.value * 8
        else:
            st = os.statvfs('/')
            return st.f_bavail * st.f_frsize * 8

    def get_constructor_arguments(self) -> str:
        """
        Returns the arguments list to pass to the constructor.
        """
        return self.__database.filename

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

    @staticmethod
    class Database:
        def __init__(self, filename):
            """
            Initialize the database. If `filename` is `None`, use the current time as the name for file.
            Otherwise, use `filename` for the file.
            """
            if filename:
                self.__filename = filename
            else:
                self.__filename = str(int(time.time() * 1000))  # current millisecond
            if not os.path.exists('./db/%s.json' % self.__filename):
                with open('./db/%s.json' % self.__filename, 'w') as f:
                    json.dump([{
                        "pre_block": "",
                        "arguments": {
                            "key": "the answer to the life, the universe and everything",
                            "value": "42"
                        }
                    }], f)

        def write(self, data: list):
            """
            Writes the data to the json file. If the file doesn't exist, produce a new file and write to it.
            """
            with open('./db/%s.json' % self.__filename, 'w') as f:
                json.dump(data, f)

        def read(self) -> list:
            """
            Returns the data in the json file.
            """
            with open('./db/%s.json' % self.__filename, 'r') as f:
                data = json.load(f)
            return data

        @property
        def filename(self):
            return self.__filename
