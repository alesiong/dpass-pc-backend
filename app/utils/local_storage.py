import ctypes
import os
import platform
import sys

class LocalStorage:
    def __init__(self):
        self.__blockchain = []

    def add(self, k: str, v: str):
        pass

    def delete(self, k: str):
        pass

    def get(self, k: str) -> str:
        pass

    def get_all(self) -> dict:
        pass

    def store(self):
        pass

    def calculate_cost(self, op: str, args: dict) -> int:
        pass

    def balance(self) -> int:
        if platform.system() == 'Windows':
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(sys.path[0][0:3]), None, None,
                                                       ctypes.pointer(free_bytes))

            return free_bytes.value * 8
        else:
            st = os.statvfs('/')
            return st.f_bavail * st.f_frsize * 8 * 1024







