import binascii

import rlp
from coincurve import PrivateKey, PublicKey
from rlp.utils import int_to_big_endian, big_endian_to_int

from chain.utils import chain_hash, normalize_signature
from p2p.log import get_logger

log = get_logger('chain.transaction')


class Transaction:
    def __init__(self):
        self.owner: bytes = None
        self.serial: int = None
        self.key: bytes = None
        self.value: bytes = None
        self.signature: bytes = None

        self.cost: int = None
        self.__hash = None

    @classmethod
    def new_transaction(cls, owner: PrivateKey, serial: int, key: str,
                        value: str) -> 'Transaction':
        transaction = cls()
        transaction.key = key.encode()
        transaction.value = value.encode()
        transaction.owner = owner.public_key.format()
        transaction.serial = serial
        transaction.signature = owner.sign(transaction.encode_data())

        transaction.cost = len(transaction.encode()) * 8

        log.debug('New transaction', transaction=transaction)

        return transaction

    @classmethod
    def decode(cls, data: bytes) -> 'Transaction':
        transaction = cls()
        transaction.cost = len(data) * 8

        data = rlp.decode(data)
        transaction.owner = data[0]
        transaction.serial = big_endian_to_int(data[1])
        transaction.key = data[2]
        transaction.value = data[3]
        transaction.signature = data[4]

        return transaction

    def encode(self) -> bytes:
        assert self.signature is not None
        return rlp.encode(
            [self.owner, int_to_big_endian(self.serial), self.key, self.value,
             self.signature])

    def hash(self):
        if self.__hash is None:
            self.__hash = chain_hash(self.encode())
        return self.__hash

    def encode_data(self) -> bytes:
        return chain_hash(rlp.encode(
            [self.owner, int_to_big_endian(self.serial), self.key, self.value]))

    # def verify(self, state=None) -> bool:
    #     # xTODO: the balance change should accumulate as a block
    #     if not self.simple_verify(state):
    #         return False
    #
    #     if state is None:
    #         from chain.state import State
    #         state = State()
    #
    #     try:
    #         return self.cost <= state.balance[self.owner]
    #     except KeyError:
    #         return False

    def simple_verify(self, state=None) -> bool:
        """
        verify without balance check
        """
        if state is None:
            from chain.state import State
            state = State()

        pk = PublicKey(self.owner)
        if not pk.verify(self.signature, self.encode_data()):
            signature = normalize_signature(pk, self.signature)
            if signature is None or not pk.verify(signature, self.encode_data()):
                log.warning('Transaction signature wrong', t=self)
                return False

        try:
            if self.serial in state.transaction_serial[self.owner]:
                return False
        except KeyError:
            pass
        return True

    def __hash__(self):
        return hash(self.hash())

    def __eq__(self, other):
        return isinstance(other, Transaction) and self.hash() == other.hash()

    def __repr__(self):
        return f'<Transaction {binascii.hexlify(self.hash()).decode()} serial={self.serial} ' \
               f'owner={binascii.hexlify(self.owner).decode()}'
