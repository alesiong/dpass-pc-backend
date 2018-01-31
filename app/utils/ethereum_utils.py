import hashlib
import time
from functools import partial
from typing import Callable, Optional

from web3 import Web3
from web3.contract import Contract
from web3.eth import Eth
from web3.miner import Miner
from web3.personal import Personal

from app.utils.decorators import set_state, check_state, check_and_unset_state
from app.utils.misc import Singleton, HashType, Address


class EthereumUtils(metaclass=Singleton):
    def __init__(self, web3: Web3 = None):
        self.__web3 = web3
        self.__eth: Eth = web3.eth
        self.__personal: Personal = web3.personal
        self.__miner: Miner = web3.miner

        self.__is_mining = False
        self.__storage_factory: Contract = None
        self.__storage_abi = None

        self._contracts_initialized = False
        self._account_unlocked = False

    # Mining Operations

    def start_mining(self, account, num_threads=1):
        self.__miner.setEtherBase(account)
        self.__miner.start(num_threads)
        self.__is_mining = True

    def stop_mining(self):
        self.__miner.stop()
        self.__is_mining = False

    @property
    def is_mining(self):
        return self.__is_mining

    # Contracts Operations

    @set_state('_contracts_initialized')
    def init_contracts(self, storage_factory_address, storage_factory_abi, storage_abi):
        self.__storage_factory = self.__eth.contract(address=storage_factory_address, abi=storage_factory_abi)
        self.__storage_abi = storage_abi

    @check_state('_contracts_initialized')
    @check_state('_account_unlocked')
    def new_storage(self, account: Address, timeout: int = 60):
        """
        Creates a new `Storage` contract for the `account`
        :return: None if the transaction is mined within the time, or transaction hash if timeout
        """
        transaction_hash = self.__storage_factory.transact({'from': account}).new_storage()
        return self.__wait_transaction(transaction_hash, timeout)

    @check_state('_contracts_initialized')
    @check_state('_account_unlocked')
    def add(self, account: Address, key: str, value: str = '', timeout: int = 60) -> Optional[HashType]:
        """
        Store data to the ethereum network in a synchronous manner
        For deletion, set `value` to ''

        :return: None if the transaction is mined within the time, or transaction hash if timeout
        """
        transaction_hash = self.__storage_factory.transact({'from': account}).add(key, value)
        return self.__wait_transaction(transaction_hash, timeout)

    @check_state('_contracts_initialized')
    @check_state('_account_unlocked')
    def add_async(self, account: HashType, key: str, value: str = '') -> HashType:
        """
        Store data to the ethereum network in a asynchronous manner
        For deletion, set `value` to ''

        :return: transaction hash
        """
        transaction_hash = self.__storage_factory.transact({'from': account}).add(key, value)
        return transaction_hash

    @check_state('_contracts_initialized')
    def get_storage(self, account: Address) -> Contract:
        """
        Returns the `Storage` contract of the `account`
        """
        storage_address = self.__storage_factory.call().storage_address(account)
        return self.__eth.contract(address=storage_address, abi=self.__storage_abi)

    @check_state('_contracts_initialized')
    def get_element(self, account: Address, index: int, kv: int, storage: Contract = None) -> str:
        if storage is None:
            storage = self.get_storage(account)
        return storage.call().data(index, kv)

    @check_state('_contracts_initialized')
    def get_length(self, account: Address, storage: Contract = None) -> int:
        if storage is None:
            storage = self.get_storage(account)
        return storage.call().length()

    @check_state('_contracts_initialized')
    def get_history(self, account: Address, from_: int = 0, storage: Contract = None):
        if storage is None:
            storage = self.get_storage(account)
        length = self.get_length(account, storage)
        data = []
        for i in range(from_, length):
            key = self.get_element(account, i, 0, storage)
            value = self.get_element(account, i, 1, storage)
            data.append((key, value))
        return data

    @check_state('_contracts_initialized')
    def estimate_new_storage_cost(self, account: Address) -> int:
        return self.__storage_factory.estimateGas({'from': account}).new_storage()

    @check_state('_contracts_initialized')
    def estimate_add_cost(self, account: Address, key: str, value: str = '') -> int:
        return self.__storage_factory.estimateGas({'from': account}).add(key, value)

    # Account operations

    def new_account(self, password: str) -> Address:
        return self.__personal.newAccount(hashlib.sha256(password.encode()).hexdigest())

    # TODO: maybe better to manage the duration ourselves (i.e. set duration to 0)
    @set_state('_account_unlocked', 'duration', 600)
    def unlock_account(self, account: Address, password: str, guard=None, duration: int = 600):
        # guard=None here ensures duration must be passed as keyword arguments
        if guard is not None:
            raise ValueError('Must use keyword argument to pass duration')
        self.__personal.unlockAccount(account, password, duration)

    def lock_account(self, account: Address):
        self.__personal.lockAccount(account)

    # Utilities

    def get_transaction_receipt(self, transaction_hash):
        return self.__eth.getTransactionReceipt(transaction_hash)

    def __wait_transaction(self, transaction_hash: HashType, timeout: int):
        i = 0
        sleep_time = 0.1
        while True:
            if self.__eth.getTransactionReceipt(transaction_hash):
                return
            time.sleep(sleep_time)
            i += 1
            if i > timeout * (1 / sleep_time):
                return transaction_hash
