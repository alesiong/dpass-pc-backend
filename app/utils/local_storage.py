from app.utils.misc import hash_dict


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
        pass

    def balance(self) -> int:
        pass
