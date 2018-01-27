class LocalStorage:
    def __init__(self):
        self.__blockchain = []

    def add(self, k: str, v: str):
        pass

    def delete(self, k: str):
        pass

    def get(self, k: str) -> str:
        dic = self.get_all()
        return dic.get(k)

    def get_all(self) -> dict:
        dic = {}
        for i in range(1, len(self.__blockchain)):
            element = self.__blockchain[i]
            if element["arguments"]["operation"] == "add":
                dic[element["arguments"]["key"]] = element["arguments"]["value"]
            if element["arguments"]["operation"] == "del":
                del dic["arguments"]["key"]
        return dic

    def store(self):
        pass

    def calculate_cost(self, op: str, args: dict) -> int:
        pass

    def balance(self) -> int:
        pass
