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
    def __init__(self, web3: Web3):
        self.__web3 = web3
        self.__eth: Eth = web3.eth
        self.__personal: Personal = web3.personal
        self.__miner: Miner = web3.miner

        self.__is_mining = False
        self.__storage_factory = None
        self.__storage_abi = None

        self._contracts_initialized = False
        self._account_unlocked = False

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

    @set_state('_contracts_initialized')
    def init_contracts(self, storage_factory_address, storage_factory_abi, storage_abi):
        self.__storage_factory = self.__eth.contract(address=storage_factory_address, abi=storage_factory_abi)
        self.__storage_abi = storage_abi

    @check_state('_contracts_initialized')
    @check_and_unset_state('_account_unlocked')
    def new_storage(self, account: Address, timeout: int = 60):
        transaction_hash = self.__storage_factory.transact({'from': account}).new_storage()
        return self.__wait_transaction(transaction_hash, timeout)

    @check_state('_contracts_initialized')
    @check_and_unset_state('_account_unlocked')
    def add(self, account: Address, key: str, value: str = '', timeout: int = 60) -> Optional[HashType]:
        """
        Store data to the ethereum network in a synchronized manner
        Set `value` to '' is just delete

        :return: None if the transaction is mined within the time, or transaction hash if timeout
        """
        transaction_hash = self.__storage_factory.transact({'from': account}).add(key, value)
        return self.__wait_transaction(transaction_hash, timeout)

    @check_state('_contracts_initialized')
    @check_and_unset_state('_account_unlocked')
    def add_async(self, account: HashType, key: str, value: str = '') -> Callable:
        transaction_hash = self.__storage_factory.transact({'from': account}).add(key, value)
        return partial(self.__eth.getTransactionReceipt, transaction_hash)

    def __wait_transaction(self, transaction_hash: HashType, timeout: int):
        i = 0
        sleep_time = 0.1
        while True:
            if self.__eth.getTransactionReceipt(transaction_hash):
                return
            time.sleep(sleep_time)
            i += 1
            if i * (1 / sleep_time) > timeout:
                return transaction_hash

    @check_state('_contracts_initialized')
    def get_storage(self, account: Address) -> Contract:
        storage_address = self.__storage_factory.call().storage_address(account)
        return self.__eth.contract(address=storage_address, abi=self.__storage_abi)

    @check_state('_contracts_initialized')
    def get_element(self, account: Address, index: int, kv: int, storage: Contract = None) -> str:
        if storage is None:
            storage_address = self.__storage_factory.call().storage_address(account)
            storage = self.__eth.contract(address=storage_address, abi=self.__storage_abi)
        return storage.call().data(index, kv)

    @check_state('_contracts_initialized')
    def get_length(self, account: Address, storage: Contract = None) -> int:
        if storage is None:
            storage_address = self.__storage_factory.call().storage_address(account)
            storage = self.__eth.contract(address=storage_address, abi=self.__storage_abi)
        return storage.call().length()

    # Account related operations
    def new_account(self, password: str) -> Address:
        return self.__personal.newAccount(hashlib.sha256(password.encode()).hexdigest())

    @set_state('_account_unlocked')
    def unlock_account(self, account: Address, password: str, duration: int = 600):
        self.__personal.unlockAccount(account, password, duration)
