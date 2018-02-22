import unittest

import time

from app.utils.local_storage import LocalStorage


class TestLocalStorage(unittest.TestCase):
    def setUp(self):
        self.storage = LocalStorage('tmp.db')

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
        test_times = 100000
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
        storage = LocalStorage()
        filename = storage.get_constructor_arguments()
        storage.add('a', '1')
        self.assertFalse(storage.get('a', True)[1])
        storage.store()
        self.assertTrue(storage.get('a', True)[1])

        storage = LocalStorage(filename)
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

        storage = LocalStorage(filename)
        self.assertIsNone(storage.get('a'))
