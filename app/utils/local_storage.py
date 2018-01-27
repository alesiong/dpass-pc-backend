import ctypes
import json
import os
import platform
import sys

from app.utils.misc import hash_dict


class LocalStorage:
    def __init__(self):
        self.__blockchain = []
        self.__blockchain.append({
            "pre_block": "",
            "operation": "Genesis",
            "arguments": {
                "key": "the answer to the life, the universe and everything",
                "value": "42"
            }
        })

    def add(self, k: str, v: str):
        """
        Add a new entry with key `k` and value `v` into the database.
        If the entry with key `k` exists, update its value with `v`.
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
        Delete an entry in database with key `k`. If the key does not exist, an exception will be thrown.
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

    def get(self, k: str) -> str:
        """
        Get an existing entry with key `k` in the database. If the entry with key `k` exists, return its value with `v`.
        If the key does not exist, return `None`.
        """
        pass

    def get_all(self) -> dict:
        """
        Return all keys with their values in the database.
        """
        pass

    def store(self):
        """
        Synchronize the changes with underlying database.
        :return:
        """
        pass

    def calculate_cost(self, op: str, args: dict) -> int:
        """
        Calculates the cost of the storage operation with operation `op` and arguments `args`.
        :param op:
        :param args:
        :return:
        """
        block = {
            "pre_block": "",
            "operation": op,
            "arguments": args
        }
        return len(json.dumps(block)) + 64

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
