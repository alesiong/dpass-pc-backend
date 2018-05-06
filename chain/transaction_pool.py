from typing import Set, List

from chain.transaction import Transaction
from chain.utils import Singleton
from p2p.log import get_logger

log = get_logger('chain.transaction_pool')


class TransactionPool(metaclass=Singleton):
    def __init__(self):
        self.__transactions: Set[Transaction] = set()
        self.__serials = {}

    def add(self, transaction: Transaction):
        if not transaction.simple_verify():
            return False
        if transaction.owner not in self.__serials:
            self.__serials[transaction.owner] = set()
        if transaction.serial in self.__serials[transaction.owner]:
            return False
        self.__serials[transaction.owner].add(transaction.serial)
        self.__transactions.add(transaction)

        log.info('Added transaction to pool', transaction=transaction)

        return True

    def pop(self, num: int):
        # FIXME: the time between pop and transactions mined may cause the verification stale
        # TODO: remove very old entries

        def key(t: Transaction):
            return -t.cost

        transactions = list(self.__transactions)
        transactions.sort(key=key)
        result = transactions[:num]
        for t in result:
            self.__transactions.remove(t)
        return result

    def add_back(self, transactions: List[Transaction]):
        self.__transactions.update(set(transactions))

    def remove(self, transaction: Transaction):
        if transaction in self.__transactions:
            self.__transactions.remove(transaction)

    def serials(self, owner: bytes):
        return self.__serials[owner]

    def pool(self):
        return self.__transactions
