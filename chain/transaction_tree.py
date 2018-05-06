from binascii import unhexlify, hexlify
from typing import List

from merkletools import MerkleTools

from chain.transaction import Transaction
from chain.utils import chain_hash_object


class TransactionTree:
    def __init__(self, transactions: List[Transaction]):
        self.merkle = MerkleTools()
        self.merkle.hash_function = chain_hash_object  # hack to use D-sha3-512
        self.transactions = transactions

        if len(transactions) == 0:
            self.root = b''
            return

        self.merkle.add_leaf([hexlify(t.hash()).decode() for t in transactions])
        self.merkle.make_tree()
        self.root: bytes = unhexlify(self.merkle.get_merkle_root())

    def __len__(self):
        return len(self.transactions)
