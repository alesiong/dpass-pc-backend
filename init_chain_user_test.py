import os
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

    print('Linking the static-nodes.json')
    os.symlink('./ethereum_private/static-nodes.json', './ethereum_private/data/geth/static-nodes.json')
    print(bcolors.OKGREEN + 'Please edit the static-nodes.json to add more static peers later.' + bcolors.ENDC)

    os.system(get_executable('./geth', 'geth') +
              'makedag --datadir ./ethereum_private/data/ init ./ethereum_private/genesis.json')

    # print('Start the geth process')
    # geth = subprocess.Popen([get_executable('./geth', 'geth'),
    #                          '--datadir',
    #                          './ethereum_private/data/',
    #                          '--ethash.dagdir',
    #                          './ethereum_private/data/ethash',
    #                          '--networkid',
    #                          '1042',
    #                          '--targetgaslimit',
    #                          '4000000'
    #                          ],
    #                         stdout=subprocess.DEVNULL,
    #                         stderr=subprocess.DEVNULL
    #                         )
    #
    # # wait for geth to start
    # time.sleep(5)
    #
    # try:
    #     web3 = Web3(IPCProvider('./ethereum_private/data/geth.ipc'))
    #     web3.miner.startAutoDAG()
    #
    #     print('It will take a lot of time to generate DAG (~3 min)...')
    #     input()
    # finally:
    #     geth.terminate()
