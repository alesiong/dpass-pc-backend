from app.utils.misc import hash_dict


import ctypes
import os
import platform
import sys
import json


class LocalStorage:
    def __init__(self):
        self.__blockchain = []
        self.__blockchain.append({
            "pre_block": "42",
            "operation": "Genesis",
            "arguments": {
                "key": "42",
                "value": "42"
            }
        })

    def add(self, k: str, v: str):
        """
        Add a new entry with key `k` and value `v` into the database.
        If the entry with key `k` exists, update its value with `v`.
        """
        self.__blockchain.append( {
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
        pass

    def get_all(self) -> dict:
        pass

    def store(self):
        pass

    def calculate_cost(self, op: str, args: dict) -> int:
        block = {
            "pre_block": "",
            "operation": op,
            "arguments":
                args
        }
        size = len(json.dumps(block)) + 64
        return size

    def balance(self) -> int:
        if platform.system() == 'Windows':
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(sys.path[0][0:3]), None, None,
                                                       ctypes.pointer(free_bytes))
            return free_bytes.value * 8
        else:
            st = os.statvfs('/')
            return st.f_bavail * st.f_frsize * 8 * 1024







