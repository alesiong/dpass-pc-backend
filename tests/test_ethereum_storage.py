import json
import subprocess
import time
import unittest

from web3 import Web3, IPCProvider

from app.utils.ethereum_storage import EthereumStorage
from app.utils.ethereum_utils import EthereumUtils
from app.utils.misc import get_executable, get_env


class TestEthereumStorage(unittest.TestCase):
    account = get_env()['ETH_ACC']
    password = get_env()['ETH_PASS']

    @classmethod
    def setUpClass(cls):
        cls.geth = subprocess.Popen([get_executable('./geth', 'geth'),
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
        ethereum_utils.init_contracts(get_env()['ETH_STORAGE'], storage_factory_abi, storage_abi)
        ethereum_utils.start_mining(get_env()['ETH_ACC'])

    @classmethod
    def tearDownClass(cls):
        cls.geth.terminate()

    def setUp(self):
        self.storage = EthereumStorage(self.account, self.password)

    def test_add_get(self):
        size = len(self.storage)
        self.storage.add('a', '1')
        self.assertEqual(len(self.storage), size + 1)
        self.assertEqual(self.storage.get('a'), '1')

        self.storage.add('a', '2')
        self.assertEqual(self.storage.get('a'), '2')

    def test_delete(self):
        size = len(self.storage)
        self.storage.add('a', '1')
        self.assertEqual(self.storage.get('a'), '1')
        self.assertEqual(len(self.storage), size + 1)

        self.storage.delete('a')
        self.assertIsNone(self.storage.get('a'))
        self.assertEqual(len(self.storage), size)

        with self.assertRaises(KeyError):
            self.storage.delete('a')

        self.storage.add('a', '2')
        self.assertEqual(self.storage.get('a'), '2')

    def test_get_time_complexity(self):
        test_times = 1000
        dummy_elements = 1000

        self.storage.add('a', '1')

        start = time.time()
        for i in range(test_times):
            self.storage.get('a')
        time1 = time.time() - start

        for i in range(dummy_elements):
            self.storage.add('a', '1')

        start = time.time()
        for i in range(test_times):
            self.storage.get('a')
        time2 = time.time() - start

        self.assertLess(time2 / time1, 2)  # should take similar time

    def test_persistent_storage(self):
        storage = EthereumStorage(self.account, self.password)
        storage.add('a', '1')
        self.assertFalse(storage.get('a', True)[1])
        storage.store()
        self.assertTrue(storage.get('a', True)[1])

        storage = EthereumStorage(self.account, self.password)
        self.assertEqual(storage.get('a'), '1')
        self.assertTrue(storage.get('a', True)[1])
        dic = storage.get_all()  # should be {'a': ('1', True)}
        self.assertIn('a', dic)
        self.assertEqual(dic['a'][0], '1')
        self.assertTrue(dic['a'][1])

        storage.delete('a')
        self.assertIsNone(storage.get('a'))
        self.assertIsNone(storage.get('a', True)[1])
        storage.store()

        storage = EthereumStorage(self.account, self.password)
        self.assertIsNone(storage.get('a'))
