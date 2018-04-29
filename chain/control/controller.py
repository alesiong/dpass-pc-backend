import rlp
from coincurve import PrivateKey, PublicKey
from rlp.utils import big_endian_to_int

from chain.block import Block
from chain.transaction import Transaction
from chain.utils.multiplexer import Multiplexer

rlp_blank = b'\x80'


class Controller:
    def __init__(self, mx: Multiplexer):
        self.__multiplexer = mx

    def start_miner(self):
        return bool(self.__multiplexer.send(rlp_blank, b'miner/start').get())

    def stop_miner(self):
        self.__multiplexer.send(rlp_blank, b'miner/stop', False)

    def set_miner(self, account: PublicKey):
        self.__multiplexer.send(rlp.encode(account.format()), b'miner/account', False)

    def latest_block(self):
        return Block.decode(*rlp.decode(self.__multiplexer.send(rlp_blank, b'block/get_latest').get()),
                            decode_alone=True).to_dict()

    def get_block(self, hash: str):
        blocks = rlp.decode(self.__multiplexer.send(rlp.encode(hash), b'block/get').get())
        return [Block.decode(*b, decode_alone=True).to_dict() for b in blocks]

    def get_next_serial(self, account: PublicKey):
        result = big_endian_to_int(
            rlp.decode(self.__multiplexer.send(rlp.encode(account.format()), b'account/next_serial').get()))
        return result

    def new_transaction(self, key: str, value: str, account: PrivateKey, serial: int):
        self.__multiplexer.send(rlp.encode([key, value, account.to_hex(), serial]), b'transaction/new', False)

    def get_transaction_pool(self):
        transactions = rlp.decode(self.__multiplexer.send(rlp_blank, b'debug/get_pool').get())
        return [Transaction.decode(t) for t in transactions]

    def get_balance(self, account: PublicKey):
        result = big_endian_to_int(
            rlp.decode(self.__multiplexer.send(rlp.encode(account.format()), b'account/balance').get()))
        return result