import base64
import binascii
import os
from pathlib import Path
from unqlite import UnQLite

import rlp
from coincurve import PrivateKey
from rlp.utils import int_to_big_endian, big_endian_to_int

from chain.block import Block
from chain.blockchain import Blockchain
from chain.state import State
from chain.transaction import Transaction
from chain.utils import Singleton


def base64encode(data) -> str:
    if isinstance(data, str):
        data = data.encode()
    return base64.encodebytes(data).decode().replace('\n', '')


def base64decode(data: str) -> bytes:
    return base64.decodebytes(data.encode())


def hex_encode(data) -> str:
    if isinstance(data, str):
        data = data.encode()
    return binascii.hexlify(data).decode()


class Storage(metaclass=Singleton):
    def __init__(self, data=None):
        assert data is not None
        databases = ['block', 'transaction', 'state']
        for f in databases:
            filename = data + '/' + f
            if not os.path.exists(filename):
                directory = Path(filename[:filename.rfind('/')])
                directory.mkdir(parents=True, exist_ok=True)

        self.__block = UnQLite(data + '/block')
        self.__transaction = UnQLite(data + '/transaction')
        self.__state = UnQLite(data + '/state')

        if not self.__state.exists('blockchain'):
            self.__state['blockchain'] = base64encode(rlp.encode([]))
            self.__state.commit()

    def store_block(self, block: Block):
        prefix = hex_encode(block.hash()) + '_'
        header = base64encode(block.encode())
        transaction = base64encode(block.encode_transactions())
        self.__block[prefix + 'header'] = header
        self.__block[prefix + 'transaction'] = transaction
        self.__block.commit()

    def store_transaction(self, transaction: Transaction):
        key = hex_encode(transaction.hash())
        data = base64encode(transaction.encode())
        self.__transaction[key] = data
        self.__transaction.commit()

    def store_state(self):
        state = State()
        chain = Blockchain()
        chain_data = rlp.encode([block.hash() for block in chain.chain])
        self.__state['blockchain'] = base64encode(chain_data)
        self.__state['node_key'] = state.node_key.to_hex()

        # any account that has balance must have corresponding storage
        for account in state.balance:
            prefix = base64encode(account) + '_'
            balance = base64encode(int_to_big_endian(state.balance[account]))
            self.__state[prefix + 'balance'] = balance
            try:
                transaction = base64encode(rlp.encode(state.transactions[account]))
                self.__state[prefix + 'transaction'] = transaction
                transaction_serial = base64encode(
                    rlp.encode([int_to_big_endian(s) for s in state.transaction_serial[account]]))
                self.__state[prefix + 'transaction_serial'] = transaction_serial
            except KeyError:
                pass

        self.__state.commit()

    def revert_block(self, block_hash: bytes):
        prefix = hex_encode(block_hash) + '_'
        self.__block.delete(prefix + 'header')
        self.__block.delete(prefix + 'transaction')

    def revert_transaction(self, transaction_hash: bytes):
        self.__transaction.delete(hex_encode(transaction_hash))
        self.__transaction.commit()

    def init_load(self):
        state = State()
        if 'node_key' in self.__state:
            state.node_key = PrivateKey.from_hex(self.__state['node_key'])
        self.load_chain()

    def load_chain(self):
        chain = rlp.decode(base64decode(self.__state['blockchain']))
        blockchain = Blockchain()
        for i in range(1, len(chain)):
            block_hash = chain[i]
            block = self.load_block(block_hash)
            blockchain.chain.append(block)
            blockchain.block_mapping[block_hash] = block

    def load_block(self, block_hash) -> Block:
        prefix = hex_encode(block_hash) + '_'
        header = base64decode(dict(self.__block.items())[prefix + 'header'])
        transaction = base64decode(dict(self.__block.items())[prefix + 'transaction'])
        return Block.decode(header, transaction)

    def load_raw_transaction(self, transaction_hash) -> bytes:
        key = hex_encode(transaction_hash)
        return base64decode(self.__transaction[key])

    def load_transaction(self, transaction_hash) -> Transaction:
        return Transaction.decode(self.load_raw_transaction(transaction_hash))

    def load_balance(self, account):
        prefix = base64encode(account) + '_'
        try:
            return big_endian_to_int(base64decode(self.__state[prefix + 'balance']))
        except KeyError:
            return 0

    def load_state(self, account, state=None):
        prefix = base64encode(account) + '_'
        if state is None:
            state = State()

        balance = self.load_balance(account)
        state.balance[account] = balance
        try:
            transaction = rlp.decode(base64decode(self.__state[prefix + 'transaction']))
            state.transactions[account] = [(big_endian_to_int(s), k, v) for s, k, v in transaction]

            transaction_serial = [big_endian_to_int(s)
                                  for s in rlp.decode(base64decode(self.__state[prefix + 'transaction_serial']))]

            state.transaction_serial[account] = set(transaction_serial)
        except KeyError:
            raise ValueError
