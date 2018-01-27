import unittest

from app.utils.local_storage import LocalStorage


class TestLocalStorage(unittest.TestCase):
    def setUp(self):
        self.storage = LocalStorage()

    def test_add_get(self):
        # size = len(self.storage)
        self.storage.add('a', '1')
        # TODO: implement the size
        # assert len(self.storage) == size + 1
        # assert self.storage.size() == size + 1
        self.assertEqual(self.storage.get('a'), '1')

        self.storage.add('a', '2')
        self.assertEqual(self.storage.get('a'), '2')

    def test_delete(self):
        self.storage.add('a', '1')
        self.assertEqual(self.storage.get('a'), '1')

        self.storage.delete('a')
        self.assertIsNone(self.storage.get('a'))

        with self.assertRaises(KeyError):
            self.storage.delete('a')

        self.storage.add('a', '2')
        self.assertEqual(self.storage.get('a'), '2')
