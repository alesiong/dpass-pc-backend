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
        self.__blockchain = []
        self.__blockchain.append({
            "pre_block": "",
            "operation": "Genesis",
            "arguments": {
                "key": "the answer to the life, the universe and everything",
                "value": "42"
            }
        })

        self.__database = LocalStorage.Database(filename)

        # structure maybe like this {'a': ('b', False)}, which is {key: (value, persistence)}
        self.__cache_dict = {}


        self.__change_set = set()
        self.__delete_set = set()

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
        return self.get_all().get(k)

    def get_all(self) -> dict:
        """
        Return all keys with their values and persistence in the database. The returned value should have a structure
        like this:

        {
            key: (value, persistence)
        }

        """
        dic = {}
        # Block 0 is the Genesis
        for i in range(1, len(self.__blockchain)):
            element = self.__blockchain[i]
            if element["operation"] == "add":
                dic[element["arguments"]["key"]] = element["arguments"]["value"]
            elif element["operation"] == "del":
                del dic[element["arguments"]["key"]]
        return dic

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
                        "value": self.__cache_dict.get(k)
                    }
                })
        for k in self.__delete_set:
            self.__blockchain.append({
                "pre_block": hash_dict(self.__blockchain[-1]),
                "arguments": {
                    "key": k,
                    "value": ""
                }
            })
        self.__database.write(self.__blockchain)
        # 2. items in delete_list are `del` operation

        pass

    def estimate_cost(self, op: str, args: dict) -> int:
        """
        Estimates the cost of the storage operation with operation `op` and arguments `args`.
        """
        block = {
            "pre_block": "",
            "operation": op,
            "arguments": args
        }
        return (len(json.dumps(block)) + 64) * 8

    def calculate_total_cost(self) -> int:
        """
        Calculates the cost of currently cached storage operations.
        """
        pass

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
        return self.__database._filename



    def __setitem__(self, key, value):
        self.add(key, value)

    def __delitem__(self, key):
        self.delete(key)

    def __getitem__(self, item):
        self.get(item)

    @staticmethod
    class Database:
        def __init__(self, filename):
            """
            Initialize the database. If `filename` is `None`, use the current time as the name for file.
            Otherwise, use `filename` for the file.
            """
            if filename:
                self._filename = filename
            else:
                self._filename = str(int(time.time() * 1000))  # current millisecond
            if not os.path.exists(self._filename):
                with open('./db/%s.json' % self._filename, 'w') as f:
                    json.dump([], f)

        def write(self, data: list):
            """
            Writes the data to the json file. If the file doesn't exist, produce a new file and write to it.
            """
            with open('./db/%s.json' % (self._filename), 'w') as f:
                json.dump(data, f)

        def read(self) -> list:
            """
            Returns the data in the json file.
            """
            with open('./db/%s.json' % (self._filename), 'r') as f:
                data = json.load(f)
            return data


