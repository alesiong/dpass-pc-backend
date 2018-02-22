import unittest

from app.utils.cipher import salted_hash, encrypt, decrypt, encrypt_and_authenticate, decrypt_and_verify


class TestCipher(unittest.TestCase):
    def setUp(self):
        self.encrypted = b'\xa2\xcf\xcf.i\xbe\xdd?\x07oL\xd9\x00@G\xec'
        self.iv = b'*\xfe\xce\xa09\xdep+\x14\xd7SvY6\xcd\xa3'
        self.hmac_encrypted = b'\xa2\xcf\xcf.i\xbe\xdd?\x07oL\xd9\x00@G\xec'
        self.hmac = b'\x8ch,q\x8eHDkV\x90\x87N\x02\x9b\x8b\xb6\xc7ik\xc0sO\x95+\x82\xd8\x96q\xad\xbc\xdc\xa9'

    def test_salted_hash(self):
        hash_ = b'O\x9d\xfc\xc7"_\xcd\x9cdA\xbe\xff\x08\xea\xf3\xcd\x8d\x7f\r\xa9\x15C!\xd7\x8e\xf1\x83\xdagJ\x86\x8bF\xf6\xbcV\xdf\xa9e\x84F\xe5V9\x01}\\\x86\xec\xea\xb0r\x0c\x87\xed:\xa8Z\x8f\xf4\xff\x81\x90\x19/\xae\x8f?\xffY\xfb\x04t]f\xf0\xd6\x8e\xa5\xb8kw\x90\xf0/\xbd$a\x94?~s)\x8c1\x96\xcc/\x1aI\xe6\t\x10w\xc4\x02\xf8\xe3\x9f\x872\x80O3\xbf\xd9\x9f\xe1A\x14,\x96XC\xcc\x9e\xa0\xd4'
        salt = b'/\xae\x8f?\xffY\xfb\x04t]f\xf0\xd6\x8e\xa5\xb8kw\x90\xf0/\xbd$a\x94?~s)\x8c1\x96\xcc/\x1aI\xe6\t\x10w\xc4\x02\xf8\xe3\x9f\x872\x80O3\xbf\xd9\x9f\xe1A\x14,\x96XC\xcc\x9e\xa0\xd4'
        self.assertEqual(salted_hash('test', salt), (hash_, salt))

        hash_, salt = salted_hash('test')
        self.assertEqual(salted_hash('test', salt), (hash_, salt))

    def test_encrypt(self):
        self.assertEqual(encrypt(b'test', b'0123456789abcdef', self.iv), self.encrypted)

    def test_decrypt(self):
        self.assertEqual(decrypt(self.encrypted, b'0123456789abcdef', self.iv), b'test')

    def test_encrypt_and_authenticate(self):
        self.assertEqual(encrypt_and_authenticate(b'test', b'0123456789abcdef'),
                         (self.hmac_encrypted, self.hmac))

    def test_decrypt_and_verify(self):
        self.assertEqual(decrypt_and_verify(self.hmac_encrypted, self.hmac, b'0123456789abcdef'), b'test')
        self.assertIsNone(decrypt_and_verify(self.hmac_encrypted, b'1234', b'0123456789abcdef'), b'test')
        self.assertIsNone(decrypt_and_verify(b'1234', self.hmac, b'0123456789abcdef'), b'test')
