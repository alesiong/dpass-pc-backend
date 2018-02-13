import os
import shutil
import subprocess
import time
from pathlib import Path

from web3 import Web3, IPCProvider

from app.utils.misc import get_executable


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


if __name__ == '__main__':
    cwd = Path('ethereum_private')

    if (cwd / 'data').exists():
        print(bcolors.FAIL + 'A private chain exists, exiting...' + bcolors.ENDC)
        exit()
    if not ((cwd / 'genesis.json').exists() and (cwd / 'static-nodes.json').exists()):
        print(bcolors.FAIL + 'genesis.json and static-nodes.json should be under ethereum_private' + bcolors.ENDC)
        exit()

    os.system(get_executable('./geth', 'geth') +
              ' --datadir ./ethereum_private/data/ init ./ethereum_private/genesis.json')

    print('Copying the static-nodes.json')
    shutil.copyfile('./ethereum_private/static-nodes.json', './ethereum_private/data/geth/static-nodes.json')

    os.system(get_executable('./geth', 'geth') +
              ' makedag 10 ./ethereum_private/data/ethash')
