from app.utils.ethereum_storage import EthereumStorage

import json

from web3 import Web3, IPCProvider

from app.utils.ethereum_utils import EthereumUtils
from app.utils.misc import get_executable, get_env, get_ipc


if __name__ == '__main__':
    ethereum_utils = EthereumUtils(Web3(IPCProvider(get_ipc('./ethereum_private/data', 'geth.ipc'))))
    storage_factory_abi = json.load(open('./ethereum_private/contracts/storage_factory.abi.json'))
    storage_abi = json.load(open('./ethereum_private/contracts/storage.abi.json'))
    ethereum_utils.init_contracts('0x40F2b5cEC3c436F66690ed48E01a48F6Da9Bad17', storage_factory_abi, storage_abi)

    account = "0x48b8b406b7039a48b10ad6f075307d0ea59dcbbf"
    password = "password"
    storage = EthereumStorage(account, password)
    while True:
        wait = input('start?')
        print(storage.get_all())