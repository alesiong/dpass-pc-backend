import time
from typing import Optional

from coincurve import PublicKey, PrivateKey

from app.utils.misc import Singleton
from chain.control.controller import Controller
from chain.transaction import Transaction


class ChainUtils(metaclass=Singleton):
    def __init__(self, controller: Controller = None):
        assert controller is not None
        self.__controller = controller

        self.__is_mining = False

    # Mining Operations
    def start_mining(self, account: PublicKey):
        self.__controller.set_miner(account)
        self.__controller.start_miner()
        self.__is_mining = True

    def stop_mining(self):
        self.__controller.stop_miner()
        self.__is_mining = False

    @property
    def is_mining(self):
        return self.__is_mining

    # Storage Operations

    def add(self, account: PrivateKey, key: str, value: str = '', timeout: int = 60) -> Optional[bytes]:
        serial = self.__controller.get_next_serial(account.public_key)
        transaction_hash = self.__controller.new_transaction(key, value, account, serial)
        return self.__wait_transaction(transaction_hash, timeout)

    def add_async(self, account: PrivateKey, key: str, value: str = '') -> bytes:
        serial = self.__controller.get_next_serial(account.public_key)
        transaction_hash = self.__controller.new_transaction(key, value, account, serial)
        return transaction_hash

    def estimate_add_cost(self, account: PrivateKey, key: str, value: str = '') -> int:
        serial = self.__controller.get_next_serial(account.public_key)
        return Transaction.new_transaction(account, serial, key, value).cost

    def get_storage(self, account: PublicKey):
        return self.__controller.get_transactions(account)

    # Account Operations
    def new_account(self, master_password_in_memory: str) -> PublicKey:
        # TODO
        pass

    def get_balance(self, account: PublicKey) -> int:
        return self.__controller.get_balance(account)

    # Utilities

    def __wait_transaction(self, transaction_hash: bytes, timeout: int):
        i = 0
        sleep_time = 0.1
        while True:
            if not self.__controller.is_transaction_in_pool(transaction_hash):
                return
            time.sleep(sleep_time)
            i += 1
            if i > timeout * (1 / sleep_time):
                return transaction_hash
