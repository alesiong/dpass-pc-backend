import time
import json
# from solc import compile_files
from web3 import Web3, IPCProvider

web3 = Web3(IPCProvider('./ethereum_private/data/geth.ipc'))


# web3 = Web3(HTTPProvider('http://127.0.0.1:8545'))

# need : 9066942000000000 wei 503719 gas
# compiled_contract = compile_files(['./ethereum_private/storage.sol'])
# storage_factory_compiled = compiled_contract['./ethereum_private/storage.sol:StorageFactory']
# storage_compiled = compiled_contract['./ethereum_private/storage.sol:Storage']
#
# json.dump(storage_compiled['abi'], open('storage.abi.json', 'w'))
# json.dump(storage_factory_compiled['abi'], open('storage_factory.abi.json', 'w'))

# contract = web3.eth.contract(abi=compiled_contract['abi'], bytecode=compiled_contract['bin'])

# account = web3.eth.accounts[1]
# web3.eth.defaultAccount = account
#
# print(web3.eth.getBalance(account))
#
# web3.personal.unlockAccount(account, 'Alesiong')

# contract_hash = contract.deploy(transaction={'from': account})

# contract = web3.eth.contract(address='0x40F2b5cEC3c436F66690ed48E01a48F6Da9Bad17', abi=storage_factory_compiled['abi'])

# print(contract_hash)
# contract_hash = '0x66ed6f13f1f42a52f03486bbd31447d65fdb1bdfe46175f52f71c717bd3d93dc'
# print(web3.eth.getBalance(account))
# print(web3.eth.getTransactionReceipt(contract_hash)['contractAddress'])

# print(contract_hash)


# print(contract.estimateGas().add('a', 'b') * web3.eth.gasPrice)
# contract.transact().new_storage()

# storage_address = contract.call().storage_address(account)
# print(storage_address)

# storage = web3.eth.contract(address=storage_address, abi=storage_compiled['abi'])

# contract.transact().add('a', 'b')

# print(storage.call().length())
# print(storage.call().data(0, 0))


# print(contract.call({'from': account, 'gas': 3000000}).add('d', 'c'))

# print(contract.transact().add('e', 'f'))


def init_only_once(account, abi, bytecode):
    storage_factory = web3.eth.contract(abi=abi, bytecode=bytecode)
    transaction_hash = storage_factory.deploy(transaction={'from': account})
    while True:
        time.sleep(1)
        receipt = web3.eth.getTransactionReceipt(transaction_hash)
        if receipt:
            return receipt['contractAddress']


def new_storage(account, address, abi):
    storage_factory = web3.eth.contract(address=address, abi=abi)
    storage_factory.transact({'from': account}).new_storage()
    while True:
        time.sleep(1)
        print(storage_factory.call().storage_address(account))


def add(account, address, abi_factory, abi_storage, key, value):
    storage_factory = web3.eth.contract(address=address, abi=abi_factory)
    storage_address = storage_factory.call().storage_address(account)
    storage = web3.eth.contract(address=storage_address, abi=abi_storage)
    storage_factory.transact({'from': account}).add(key, value)
    while True:
        time.sleep(1)
        print(storage.call().length())


if __name__ == '__main__':
    account = '0x8ad64a818797ee9735357d4c9f8bb66b9a775e65'
    web3.personal.unlockAccount(account, 'password')
    address = '0x40F2b5cEC3c436F66690ed48E01a48F6Da9Bad17'
    storage_factory_abi = json.load(open('storage_factory.abi.json'))
    storage_abi = json.load(open('storage.abi.json'))
    add(account, address, storage_factory_abi, storage_abi, 'a', 'b')
    # new_storage(account, address, storage_factory_abi)
