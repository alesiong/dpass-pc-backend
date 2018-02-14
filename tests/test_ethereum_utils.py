import json
import subprocess
import time
import unittest

from web3 import Web3, IPCProvider

from app.utils.ethereum_utils import EthereumUtils
from app.utils.exceptions import StateError


class TestEthereumUtils(unittest.TestCase):
    account = '0x8ad64a818797ee9735357d4c9f8bb66b9a775e65'
    password = 'password'

    @classmethod
    def setUpClass(cls):
        cls.geth = subprocess.Popen(['geth',
                                     '--datadir',
                                     './ethereum_private/data/',
                                     '--ethash.dagdir',
                                     './ethereum_private/data/ethash',
                                     '--networkid',
                                     '1042',
                                     '--targetgaslimit',
                                     '4000000'
                                     ],
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
        time.sleep(5)
        ethereum_utils = EthereumUtils(Web3(IPCProvider('./ethereum_private/data/geth.ipc')))
        storage_factory_abi = json.load(open('./ethereum_private/contracts/storage_factory.abi.json'))
        storage_abi = json.load(open('./ethereum_private/contracts/storage.abi.json'))
        ethereum_utils.init_contracts('0x40F2b5cEC3c436F66690ed48E01a48F6Da9Bad17', storage_factory_abi, storage_abi)

    @classmethod
    def tearDownClass(cls):
        cls.geth.terminate()

    def setUp(self):
        self.ethereum_utils = EthereumUtils()

    @unittest.skip
    def test_unlock_account(self):
        self.ethereum_utils.unlock_account(self.account, self.password, duration=2)
        time.sleep(2.5)
        with self.assertRaises(StateError):
            self.ethereum_utils.add(self.account, 'x', 'y')
