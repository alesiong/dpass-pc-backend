"""
Init the ethereum private chain. This script should be run only once for each unique private chain.
This script is for administrator, as it will deploy the factory contract to the chain.
Chain initialization for end user is run when the server starts.
You need to have `geth` in PATH.
This script may not work on windows

If you need to compile the contracts, you need to also have `solc` in PATH and `solc` python package installed
"""
import argparse
import getpass
import json
import os
import subprocess
from pathlib import Path

import time

from web3 import Web3, IPCProvider


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def create_storage_factory(web3, account, abi, bytecode):
    storage_factory = web3.eth.contract(abi=abi, bytecode=bytecode)
    transaction_hash = storage_factory.deploy(transaction={'from': account})
    while True:
        time.sleep(0.1)
        receipt = web3.eth.getTransactionReceipt(transaction_hash)
        if receipt:
            return receipt['contractAddress']


def compile_sol(filename, contract):
    from solc import compile_files
    compiled_contract = compile_files([filename])
    compiled_contract = compiled_contract['%s:%s' % (filename, contract)]
    return compiled_contract['abi'], compiled_contract['bin']


if __name__ == '__main__':
    cwd = Path('.')
    parser = argparse.ArgumentParser(
        description='Admin tools to generate a new ethereum private chain and deploy the storage factory contract')
    parser.add_argument('--compile', action='store_true', help='Use `solc` to compile the storage.sol')
    args = parser.parse_args()

    print('This tool is for administrator to generate a new ethereum private chain and then deploy'
          ' the storage factory contract, type YES if you want to continue:', end='')
    inp = input()
    if inp != 'YES':
        exit()
    if os.path.exists('data'):
        print(bcolors.FAIL + 'A private chain exists, exiting...' + bcolors.ENDC)
        exit()
    if not (os.path.exists('genesis.json.template') and os.path.exists('static-nodes.json') and os.path.exists('contracts')):
        print(bcolors.FAIL + 'genesis.json.template, static-nodes.json, and contracts/ should be in this folder'
              + bcolors.ENDC)
        exit()

    print(bcolors.OKGREEN + 'Creating the initial account, please remember the password' + bcolors.ENDC)
    os.system('geth account new --datadir . --keystore .')
    key_file_name = list(cwd.glob('UTC--*'))[0].name
    init_address = key_file_name[key_file_name.rfind('--') + 2:]
    inp = input('Type YES to confirm the initial account address ' + init_address + ':')
    if inp != 'YES':
        os.remove(key_file_name)
        exit()
    with open('tmp.json', 'w') as f:
        print(open('./genesis.json.template').read().replace('<initial account>', init_address), file=f)

    print('Initiating the private blockchain, will assign 10K ETH to the initial account')
    os.system('geth --datadir ./data/ init ./tmp.json')
    os.rename(key_file_name, './data/keystore/' + key_file_name)
    os.remove('tmp.json')

    print('Linking the static-nodes.json')
    os.symlink('../../static-nodes.json', './data/geth/static-nodes.json')
    print(bcolors.OKGREEN + 'Please edit the static-nodes.json to add more static peers later.' + bcolors.ENDC)

    print('Start the geth process')
    geth = subprocess.Popen(['geth',
                             '--datadir',
                             './data/',
                             '--ethash.dagdir',
                             './data/ethash',
                             '--networkid',
                             '1042',
                             '--targetgaslimit',
                             '4000000'
                             ],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                            )

    # wait for geth to start
    time.sleep(5)

    try:
        web3 = Web3(IPCProvider('./data/geth.ipc'))
        web3.miner.start(1)
        init_address = '0x' + init_address
        password = getpass.getpass('Please input the password for the initial account:')
        web3.personal.unlockAccount(init_address, password)

        print('Deploying storage factory contract...')
        print('Also start mining, it will take a lot of time to generate DAG (~3 min)...')
        if args.compile:
            storage_factory_abi, storage_factory_bin = compile_sol('./contracts/storage.sol', 'StorageFactory')
            json.dump(storage_factory_abi, open('contracts/storage_factory.abi.json', 'w'))
            json.dump(storage_factory_bin, open('contracts/storage_factory.bin', 'w'))
        else:
            storage_factory_abi = json.load(open('contracts/storage_factory.abi.json'))
            storage_factory_bin = open('contracts/storage_factory.bin').read().strip()
        factory_address = create_storage_factory(web3, init_address, storage_factory_abi, storage_factory_bin)
        print(bcolors.OKGREEN + 'The storage factory address is ' + factory_address + bcolors.ENDC)
    finally:
        geth.terminate()
