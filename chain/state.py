from typing import Dict, List, Set

from coincurve import PrivateKey, PublicKey

from chain.block import Block
from chain.transaction import Transaction
from chain.utils import Singleton


class State(metaclass=Singleton):
    def __init__(self):
        self.transactions: Dict[bytes, List[tuple]] = {}
        self.balance: Dict[bytes, int] = {}
        self.transaction_serial: Dict[bytes, Set[int]] = {}

        self.node_key = PrivateKey()
        self.miner: PublicKey = None

    def new_block(self, block: Block):
        from chain.storage import Storage
        miner = block.miner
        if miner not in self.balance:
            self.balance[miner] = Storage().load_balance(miner)

        self.balance[miner] += block.reward

        for t in block.transactions.transactions:
            self.new_transaction(t)

    def new_transaction(self, transaction: Transaction):
        from chain.storage import Storage
        owner = transaction.owner
        if owner not in self.transactions:
            try:
                Storage().load_state(owner, self)
            except ValueError:
                self.transactions[owner] = []

        self.transactions[owner].append((transaction.serial, transaction.key, transaction.value))

        if owner not in self.transaction_serial:
            self.transaction_serial[owner] = set()

        self.transaction_serial[owner].add(transaction.serial)

        # if balance[owner] not exist, the transaction is not valid
        self.balance[owner] -= transaction.cost

    def get_balance(self, account: bytes):
        from chain.storage import Storage
        if account not in self.balance:
            self.balance[account] = Storage().load_balance(account)
        return self.balance[account]
