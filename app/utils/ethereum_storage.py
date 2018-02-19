from typing import Optional, Union, Tuple, Generator, Dict, Set

from app.utils.ethereum_utils import EthereumUtils
from app.utils.misc import Address


class EthereumStorage:
    def __init__(self, account: Address, password: str):
        """
        Load the ethereum storage for `account`. `password` should also be provided.

        **Assumptions**:

        1. Singleton class EthereumUtils has been initialized before
        2. Contracts has been initialized (EthereumUtils.init_contracts)
        3. Storage contract for `account` has been created (EthereumUtils.new_storage)
        """
        self.__cache_dict: Dict[str, Tuple[str, bool]] = {}

        self.__change_set: Set[str] = set()
        self.__delete_set: Set[str] = set()

        self.__ethereum_utils = EthereumUtils()
        self.__account = account
        self.__password = password
        self.__storage = self.__ethereum_utils.get_storage(account)

        # TODO: load the blockchain
        # TODO: if we cache the blockchain on the disk, don't forget to do it at `store`

        for k, v in self.__ethereum_utils.get_history(account, 0, self.__storage):
            if v == "":
                del self.__cache_dict[k]
            else:
                self.__cache_dict[k] = (v, True)

        # TODO: current state model for CRUD may need to change to fit the ethereum model:
        # TODO: i.e.: store method cannot return immediately, or the data cannot be put on the chain immediately
        # TODO: also need to consider how/when to update(download/sync) data from blockchain

    def add(self, k: str, v: str):
        """
        Add a new entry with key `k` and value `v` into the database. If the entry with key `k` exists,
        update its value with `v`. **This will not immediately write the underlying database.**
        """

        if k in self.__cache_dict and self.__cache_dict[k][1]:
            self.__change_set.add(k)
        elif k in self.__delete_set:
            self.__delete_set.remove(k)
            self.__change_set.add(k)
        self.__cache_dict[k] = (v, False)

    def delete(self, k: str):
        """
        Delete an entry in database with key `k`. If the key does not exist, an exception `KeyError` will be thrown.
        **This will not immediately write the underlying database.**
        """

        if k in self.__cache_dict:
            if not self.__cache_dict[k][1]:
                if k in self.__change_set:
                    # changed in cache
                    self.__delete_set.add(k)
                    del self.__cache_dict[k]
                    self.__change_set.remove(k)
                else:
                    # new in cache, not changed in cache
                    del self.__cache_dict[k]
            else:
                self.__delete_set.add(k)
                del self.__cache_dict[k]
        else:
            raise KeyError(k)

    def get(self, k: str, check_persistence: bool = False) -> Union[Optional[str], Tuple[Optional[str], bool]]:
        """
        Get an existing entry with key `k` in the database. If the entry with key `k` exists, return its value.
        If the key does not exist, return `None`. If `check_persistence` is `True`,
        returns a tuple like `(value, True)`, where the second element shows whether this key-value pair has been
        `store`d into the underlying database. If `check_persistence` is `True` and the key does not exist, return
        `(None, None)`.
        """

        result = self.__cache_dict.get(k, (None, None))
        if check_persistence:
            return result
        else:
            return result[0]

    def get_all(self) -> dict:
        """
        Return all keys with their values and persistence in the database. The returned value should have a structure
        like this:

        {
            key: (value, persistence)
        }

        """
        return self.__cache_dict

    def __get_all_add(self) -> Generator[Tuple[str, str], None, None]:
        return ((k, v[0]) for k, v in self.__cache_dict.items() if not v[1])

    def __get_all_del(self) -> Generator[str, None, None]:
        return (k for k in self.__delete_set)

    def store(self):
        """
        Synchronize the changes with underlying database.
        """

        # FIXME: unlock account first
        self.__ethereum_utils.unlock_account(self.__account, self.__password, duration=2)

        # FIXME: use async add
        # TODO: how to determine if a key is really stored? only update persistence if transaction mined?
        for k, v in self.__get_all_add():
            self.__ethereum_utils.add(self.__account, k, v)
            self.__cache_dict[k] = (v, True)

        for k in self.__get_all_del():
            self.__ethereum_utils.add(self.__account, k)
        self.__change_set = set()
        self.__delete_set = set()

    def estimate_cost(self, args: dict) -> int:
        """
        Estimates the cost of the storage operation with arguments `args`.
        """
        # FIXME: it returns gas count (gas count * gas price = cost in wei)
        key = args['key']
        value = args['value']
        return self.__ethereum_utils.estimate_add_cost(self.__account, key, value)

    def calculate_total_cost(self) -> int:
        """
        Calculates the cost of currently cached storage operations.
        """
        # FIXME: it returns gas count (gas count * gas price = cost in wei)
        s = 0
        for k, v in self.__get_all_add():
            s += self.__ethereum_utils.estimate_add_cost(self.__account, k, v)
        for k in self.__get_all_del():
            s += self.__ethereum_utils.estimate_add_cost(self.__account, k)
        return s

    def balance(self) -> int:
        """
        Returns the balance (remaining storage space) of current user.
        """
        # FIXME: it returns wei
        return self.__ethereum_utils.get_balance(self.__account)

    def get_constructor_arguments(self) -> Address:
        """
        Returns the arguments list to pass to the constructor.
        """
        # TODO: is it necessary to return password?
        return self.__account

    def size(self) -> int:
        return len(self.__cache_dict)

    def __setitem__(self, key, value):
        self.add(key, value)

    def __delitem__(self, key):
        self.delete(key)

    def __getitem__(self, item):
        self.get(item)

    def __len__(self):
        return self.size()