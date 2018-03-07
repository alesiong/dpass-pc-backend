import unittest
import os

from app.utils.master_password import MasterPassword
from app.utils.settings import Settings


class TestMasterPassword(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Settings('db/tmp/config.json')

    @classmethod
    def tearDownClass(cls):
        os.remove('db/tmp/config.json')

    def test_verify(self):
        MasterPassword.new_password('password')
        self.assertIsNotNone(MasterPassword.verify('password'))
        self.assertIsNone(MasterPassword.verify('pass'))
