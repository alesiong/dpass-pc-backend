import binascii
from typing import Tuple

import rlp
from coincurve import PublicKey
from rlp.utils import int_to_big_endian, big_endian_to_int

from chain.transaction_pool import TransactionPool
from chain.transaction_tree import TransactionTree
from chain.utils import chain_hash, timestamp, mine, get_target
from p2p.log import get_logger

log = get_logger('chain.block')

MAX_TRANSACTION_NUM = 64


class Block:
    def __init__(self):
        self.height: int = None
        self.timestamp: int = None
        self.difficulty: int = None
        self.previous_hash: bytes = None
        self.miner: bytes = None
        self.reward: int = None
        self.transaction_root: bytes = None
        self.nonce: bytes = None

        self.transactions: TransactionTree = None
        self.previous: 'Block' = None
        self.real_difficulty: int = None

        self.__hash = None
        self.__mined = False

    @classmethod
    def create(cls, previous: 'Block', miner: PublicKey) -> 'Block':
        block = cls()

        block.timestamp = timestamp()
        block.height = previous.height + 1
        block.previous_hash = previous.hash()

        block.previous = previous
        block.miner = miner.format()

        transactions = TransactionPool().pop(MAX_TRANSACTION_NUM)
        invalid = []
        valid = []
        from chain.state import State
        balance = {}
        while True:
            invalid_len_this_round = 0
            for t in transactions:
                if t.owner == block.miner:
                    valid.append(t)
                else:
                    if t.owner not in balance:
                        balance[t.owner] = State().get_balance(t.owner)
                    if t.simple_verify() and t.cost <= balance.get(t.owner, 0):
                        valid.append(t)
                        balance[t.owner] -= t.cost
                    else:
                        invalid.append(t)
                        invalid_len_this_round += 1
            if len(valid) >= MAX_TRANSACTION_NUM:
                break
            transactions = TransactionPool().pop(invalid_len_this_round)
            if not transactions:
                break

        TransactionPool().add_back(invalid)

        block.transactions = TransactionTree(valid)
        block.transaction_root = block.transactions.root

        block.real_difficulty, time_punishment = block.calculate_difficulty()
        block.difficulty = block.previous.difficulty + time_punishment

        block.reward = block.calculate_reward()

        log.info('New block created', diff=block.real_difficulty, as_sec=block.real_difficulty // 30000)

        return block

    @classmethod
    def from_dict(cls, dict_) -> 'Block':
        block = cls()
        block.height = dict_['height']
        block.timestamp = dict_['timestamp']
        block.transaction_root = dict_['transactionRoot']
        block.difficulty = dict_['difficulty']
        block.nonce = dict_['nonce']
        block.previous_hash = dict_['previousHash']
        block.miner = dict_['miner']
        block.reward = dict_['reward']

        block.transactions = TransactionTree([])

        return block

    def to_dict(self) -> dict:
        return {
            'height': self.height,
            'timestamp': self.timestamp,
            'transactionRoot': binascii.hexlify(self.transaction_root).decode(),
            'difficulty': self.difficulty,
            'nonce': binascii.hexlify(self.nonce).decode(),
            'previousHash': binascii.hexlify(self.previous_hash).decode(),
            'miner': binascii.hexlify(self.miner).decode(),
            'reward': self.reward
        }

    @classmethod
    def genesis(cls) -> 'Block':
        # TODO: put into config
        return cls.from_dict({
            'height': 0,
            'timestamp': 0,
            'transactionRoot': b'',
            'difficulty': 300000,
            'nonce': b'42',
            'previousHash': b'',
            'miner': b'',
            'reward': 0
        })

    @classmethod
    def decode(cls, header: bytes, transactions: bytes, decode_alone=False) -> 'Block':
        header = rlp.decode(header)

        block = cls()
        block.height = big_endian_to_int(header[0])
        block.timestamp = big_endian_to_int(header[1])
        block.difficulty = big_endian_to_int(header[2])
        block.previous_hash = header[3]
        block.miner = header[4]
        block.reward = big_endian_to_int(header[5])
        block.transaction_root = header[6]
        block.nonce = header[7]
        block.__mined = True

        if not decode_alone:
            from chain.blockchain import Blockchain
            try:
                previous = Blockchain().block_mapping[block.previous_hash]
            except KeyError:
                raise ValueError('Previous block does not exist')
            block.previous = previous

        from chain.storage import Storage
        transactions = rlp.decode(transactions)

        if not decode_alone:
            storage = Storage()
            transaction_objects = []
            for t in transactions:
                transaction_objects.append(storage.load_transaction(t))
            block.transactions = TransactionTree(transaction_objects)

        return block

    def encode(self) -> bytes:
        return rlp.encode(
            [int_to_big_endian(self.height), int_to_big_endian(self.timestamp),
             int_to_big_endian(self.difficulty),
             self.previous_hash, self.miner,
             int_to_big_endian(self.reward),
             self.transaction_root, self.nonce])

    def encode_data(self) -> bytes:
        return rlp.encode(
            [int_to_big_endian(self.height), int_to_big_endian(self.timestamp),
             int_to_big_endian(self.difficulty),
             self.previous_hash, self.miner,
             int_to_big_endian(self.reward),
             self.transaction_root])

    def encode_transactions(self) -> bytes:
        return rlp.encode([t.hash() for t in self.transactions.transactions])

    def hash(self) -> bytes:
        if not self.__mined:
            return b''
        if self.__hash is None:
            self.__hash = chain_hash(self.encode_data() + chain_hash(self.nonce))
        return self.__hash

    def calculate_difficulty(self) -> Tuple[int, int]:
        def continual_miner_punishment():
            sum_ = 0
            block = self.previous
            for _ in range(5):
                if block is None:
                    break
                if block.miner == self.miner:
                    sum_ += 1
                block = block.previous

            return int(2 ** sum_)

        def transaction_number_punishment():
            num = 0
            for t in self.transactions.transactions:
                if t.owner != self.miner:
                    num += 1
            return MAX_TRANSACTION_NUM - num

        def timestamp_punishment():
            if self.previous.timestamp == 0:
                # previous is genesis
                return self.previous.difficulty

            if self.previous.previous:
                old_difficulty = self.previous.previous.difficulty
            else:
                old_difficulty = 0
            old_difficulty = self.previous.difficulty - old_difficulty
            time_diff = self.timestamp - self.previous.timestamp

            change = 10000 / time_diff
            change = max(0.5, change)
            change = min(2.0, change)
            new_difficulty = change * old_difficulty

            return int(new_difficulty)

        time_punishment = timestamp_punishment()

        # FIXME: should be 10000
        return ((continual_miner_punishment() * 1000 +
                 transaction_number_punishment() * 1000 +
                 time_punishment),
                time_punishment)

    def miner_data_provider(self, nonce: bytes) -> bytes:
        self.nonce = nonce
        return self.encode()

    def mine(self):
        log.info('Mining new block', block=self)
        miner = mine(get_target(self.real_difficulty), self.miner_data_provider)
        while True:
            result = next(miner)
            if result:
                self.__mined = True
                log.debug('Mined new block!!!', block=self)
                yield True
                return
            yield

    def calculate_reward(self) -> int:
        block_reward = 1024 * 8  # 1KB

        transaction_reward = sum(t.cost for t in self.transactions.transactions)

        confirmation_reward = 0
        coefficients = [0.5, 0.25, 0.125, 0.0625, 0.03125]
        previous = self.previous
        for i in range(5):
            if previous is None:
                break
            if previous.miner != self.miner:
                confirmation_reward += int(coefficients[i] * previous.reward)
            previous = previous.previous

        return block_reward + transaction_reward + confirmation_reward

    def verify(self, state=None):
        if state is None:
            from chain.state import State
            state = State()

        # verify time
        if self.timestamp > timestamp():
            return False

        # verify reward & difficulty
        if self.calculate_reward() != self.reward:
            return False

        real_difficulty, time_punishment = self.calculate_difficulty()

        if self.previous.difficulty + time_punishment != self.difficulty:
            return False

        # verify proof of work
        target = get_target(real_difficulty)
        mined_hash = big_endian_to_int(chain_hash(self.encode()))
        if mined_hash >= target:
            return False

        # verify transaction
        if self.transactions.root != self.transaction_root:
            return False

        balance = {}

        for t in self.transactions.transactions:
            if t.owner == self.miner and not t.simple_verify(state):
                return False
            if t.owner != self.miner:
                if t.owner not in balance:
                    balance[t.owner] = state.get_balance(t.owner)
                if not t.simple_verify() or t.cost > balance.get(t.owner, 0):
                    return False
                balance[t.owner] -= t.cost

        log.debug('Block verified', block=self)

        return True

    def __repr__(self):
        return f'<Block #{self.height}: {binascii.hexlify(self.hash()).decode()}>'
