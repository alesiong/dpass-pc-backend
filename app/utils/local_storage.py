import ctypes
import json
import os
import platform
import sys
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

        # FIXME: we can use cache_dict with dirty bits to log what is added, but we must log what is deleted in other places
        self.__delete_list = []

    def add(self, k: str, v: str):
        """
        Add a new entry with key `k` and value `v` into the database. If the entry with key `k` exists,
        update its value with `v`. **This will not immediately write the underlying database.**
        """
        self.__blockchain.append({
            "pre_block": hash_dict(self.__blockchain[-1]),
            "operation": "add",
            "arguments": {
                "key": k,
                "value": v
            }
        })

    def delete(self, k: str):
        """
        Delete an entry in database with key `k`. If the key does not exist, an exception `KeyError` will be thrown.
        **This will not immediately write the underlying database.**
        """
        if self.get(k) is not None:
            self.__blockchain.append({
                "pre_block": hash_dict(self.__blockchain[-1]),
                "operation": "del",
                "arguments": {
                    "key": k,
                }
            })
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

        # TODO: logics maybe like this:
        # 1. filter the dirty items in the cache_dict (persistence == False), these are `add` operation
        # 2. items in delete_list are `del` operation
        # TODO: things may gets tricky is I add a new key and then delete it
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

    # TODO: add size

    def __setitem__(self, key, value):
        self.add(key, value)

    def __delitem__(self, key):
        self.delete(key)

    def __getitem__(self, item):
        self.get(item)

    @staticmethod
    class Database:
        # FIXME: this is just an example, feel free to modify all those below

        def __init__(self, filename):
            if filename:
                self._filename = filename
            else:
                self._filename = ''  # TODO: generate a name for tmp file

        def write(self):
            pass

        def read(self):
            pass
