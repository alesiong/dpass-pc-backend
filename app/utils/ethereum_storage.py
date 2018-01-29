from solc import compile_files
from web3 import Web3, IPCProvider, HTTPProvider

web3 = Web3(IPCProvider('./ethereum_private/data/geth.ipc'))

# web3 = Web3(HTTPProvider('http://127.0.0.1:8545'))

# need : 9066942000000000 wei 503719 gas
compiled_contract = compile_files(['./ethereum_private/storage.sol'])['./ethereum_private/storage.sol:Storage']

# contract = web3.eth.contract(abi=compiled_contract['abi'], bytecode=compiled_contract['bin'])

account = web3.eth.accounts[1]

print(web3.eth.getBalance(account))

web3.personal.unlockAccount(account, 'password')

# contract_hash = contract.deploy(transaction={'from': account})
contract_hash = '0xb41b887b40b5899adace4313cab6dced01b110244ee18f7040bfb66ccd9a1e4d'
address = '0xa0E90C340bdE048cB66eeF7729B63a202d6e4e39'

contract = web3.eth.contract(address='0xa0E90C340bdE048cB66eeF7729B63a202d6e4e39', abi=compiled_contract['abi'])
web3.eth.defaultAccount = account

# print(web3.eth.getBalance(account))

# print(contract_hash)

# print(web3.eth.getTransactionReceipt(contract_hash))

# print(contract.estimateGas().add('a', 'b'))
# print(contract.call({'from': account}).data(0, 0))

# print(contract.call({'from': account, 'gas': 3000000}).add('d', 'c'))
# func = contract.call(transaction={'from': account, 'gas': 3000000}).add

# func('e', 'f')

print(contract.transact().add('e', 'f'))
