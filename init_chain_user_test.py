import getpass
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

from web3 import Web3, IPCProvider

from app import EthereumUtils
from app.utils.ethereum_utils import initialize_ethereum_account
from app.utils.misc import get_executable, get_env

if __name__ == '__main__':
    cwd = Path('ethereum_private')

    if (cwd / 'data').exists():
        print('A private chain exists, exiting...')
        exit()
    if not ((cwd / 'genesis.json').exists() and (cwd / 'static-nodes.json').exists()):
        print('genesis.json and static-nodes.json should be under ethereum_private')
        exit()

    os.system(get_executable('./geth', 'geth') +
              ' --datadir ./ethereum_private/data/ init ./ethereum_private/genesis.json')

    print('Copying the static-nodes.json')
    shutil.copyfile('./ethereum_private/static-nodes.json', './ethereum_private/data/geth/static-nodes.json')

    os.system(get_executable('./geth', 'geth') +
              ' makedag 10 ./ethereum_private/data/ethash')

    print('Start the geth process')
    geth = subprocess.Popen([get_executable('./geth', 'geth'),
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
        ethereum_utils = EthereumUtils(Web3(IPCProvider('./ethereum_private/data/geth.ipc')))
        storage_factory_abi = json.load(open('./ethereum_private/contracts/storage_factory.abi.json'))
        storage_abi = json.load(open('./ethereum_private/contracts/storage.abi.json'))
        ethereum_utils.init_contracts(get_env()['ETH_STORAGE'], storage_factory_abi, storage_abi)
        password = getpass.getpass('Please input the password for the new account:')
        account = initialize_ethereum_account(password)
        print('Please remember this account: ', account)
        print('along with the password')
    finally:
        geth.terminate()
