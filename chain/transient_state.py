from copy import deepcopy

from chain.block import Block
from chain.state import State
from chain.storage import Storage
from chain.transaction import Transaction
from chain.transaction_pool import TransactionPool


class TransientState:
    def __init__(self):
        # copy current state
        state = State()
        self.transactions = deepcopy(state.transactions)
        self.balance = deepcopy(state.balance)
        self.transaction_serial = deepcopy(state.transaction_serial)

        self.reverted_block = []
        self.reverted_transaction = set()

    def save(self):
        state = State()
        state.transactions = self.transactions
        state.balance = self.balance
        state.transaction_serial = self.transaction_serial

        storage = Storage()
        for b in self.reverted_block:
            storage.revert_block(b)
        for t in self.reverted_transaction:
            storage.revert_transaction(t)

        # call storage.store_state when sync finished

    def new_block(self, block: Block):
        State.new_block(self, block)

    def new_transaction(self, transaction: Transaction):
        h = transaction.hash()
        if h in self.reverted_transaction:
            self.reverted_transaction.remove(h)
        State.new_transaction(self, transaction)

    def revert_block(self, block: Block):
        self.reverted_block.append(block.hash())
        if block.miner not in self.balance:
            try:
                Storage().load_state(block.miner, self)
            except ValueError:
                if block.miner not in self.balance:
                    raise
        self.balance[block.miner] -= block.reward
        for t in block.transactions.transactions:
            self.revert_transaction(t)
        TransactionPool().add_back(block.transactions.transactions)

    def revert_transaction(self, transaction: Transaction):
        if transaction.owner not in self.transactions:
            try:
                Storage().load_state(transaction.owner, self)
            except ValueError:
                raise
        self.reverted_transaction.add(transaction.hash())
        self.transactions[transaction.owner].remove((transaction.serial, transaction.key, transaction.value))
        self.transaction_serial[transaction.owner].remove(transaction.serial)
        self.balance[transaction.owner] += transaction.cost

    def get_balance(self, account: bytes):
        return State.get_balance(self, account)
