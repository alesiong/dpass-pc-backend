import json


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
        block = {
            "pre_block": "",
            "operation": op,
            "arguments":
                args
        }
        size = len(json.dumps(block)) + 64
        return size

    def balance(self) -> int:
        pass
