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
        dic1 = {}
        dic2 = {}
        for i in range(1, len(self.__blockchain)):
            deletion = self.__blockchain[i]
            if deletion["operation"] == "del":
                dic2.append(deletion["arguments"]["key"])

        for i in range(1, len(self.__blockchain)):
            element = self.__blockchain[i]
            if element["arguments"]["key"] not in dic2:
                dic1[element["arguments"]["key"]] = element["arguments"]["value"]
        return dic1



    def store(self):
        pass

    def calculate_cost(self, op: str, args: dict) -> int:
        pass

    def balance(self) -> int:
        pass
