import struct
from hashlib import sha256

import bitcoin
from Crypto.Cipher import AES
from Crypto.Hash import SHA3_256, HMAC, SHA256
from Crypto.Util import Padding
from coincurve import PublicKey, PrivateKey
from rlp.utils import str_to_bytes, ascii_chr

from p2p.exceptions import ECIESDecryptionError


def hmac_sha256(k, m):
    h = HMAC.new(k, digestmod=SHA256)
    h.update(m)
    return h.digest()


def sha3(seed):
    seed = str_to_bytes(seed)
    return SHA3_256.new(data=seed).digest()


def mk_privkey(seed):
    seed = str_to_bytes(seed)
    return sha3(seed)


def ecdsa_verify(pubkey, signature, message):
    assert len(pubkey) == 64
    pk = PublicKey.from_signature_and_message(signature, message, hasher=None)
    return pk.format(compressed=False) == b'\04' + pubkey


verify = ecdsa_verify


def ecdsa_sign(msghash, privkey):
    pk = PrivateKey(privkey)
    return pk.sign_recoverable(msghash, hasher=None)


sign = ecdsa_sign


def ecdsa_recover(message, signature):
    assert len(signature) == 65
    pk = PublicKey.from_signature_and_message(signature, message, hasher=None)
    return pk.format(compressed=False)[1:]


recover = ecdsa_recover


def privtopub(raw_privkey):
    raw_pubkey = bitcoin.encode_pubkey(bitcoin.privtopub(raw_privkey),
                                       'bin_electrum')
    assert len(raw_pubkey) == 64
    return raw_pubkey


class ECCx:
    """
    Modified to work with raw_pubkey format used in RLPx
    and binding default curve and cipher
    """
    curve = 'secp256r1'
    ecies_encrypt_overhead_length = 113

    def __init__(self, raw_pubkey=None, raw_privkey=None):
        self.vk = None
        self.pk = None
        if raw_privkey:
            assert not raw_pubkey
            self.vk = PrivateKey(raw_privkey)
            self.pk = self.vk.public_key
        elif raw_pubkey:
            assert len(raw_pubkey) == 64
            self.pk = PublicKey(b'\x04' + raw_pubkey)
        else:
            self.vk = PrivateKey()
            self.pk = self.vk.public_key

    @property
    def raw_pubkey(self):
        return self.pk.format(False)[1:]

    @classmethod
    def _decode_pubkey(cls, raw_pubkey):
        assert len(raw_pubkey) == 64
        pubkey_x = raw_pubkey[:32]
        pubkey_y = raw_pubkey[32:]
        return cls.curve, pubkey_x, pubkey_y, 64

    def get_ecdh_key(self, raw_pubkey):
        "Compute public key with the local private key and returns a 256bits shared key"
        ecc_pub = PublicKey(b'\x04' + raw_pubkey)
        point = ecc_pub.multiply(self.vk.secret)
        key = point.format(False)[1:33]
        assert len(key) == 32
        return key

    @property
    def raw_privkey(self):
        if self.vk:
            return self.vk.secret
        return None

    def is_valid_key(self, raw_pubkey, raw_privkey=None):
        failed = False
        try:
            assert len(raw_pubkey) == 64
            if raw_privkey:
                PrivateKey(raw_privkey)
            else:
                PublicKey(b'\x04' + raw_pubkey)

        except (AssertionError, Exception):
            failed = True
        return not failed

    @classmethod
    def ecies_encrypt(cls, data, raw_pubkey, shared_mac_data=''):
        """
        ECIES Encrypt, where P = recipient public key is:
        1) generate r = random value
        2) generate shared-secret = kdf( ecdhAgree(r, P) )
        3) generate R = rG [same op as generating a public key]
        4) send 0x04 || R || AsymmetricEncrypt(shared-secret, plaintext) || tag


        currently used by go:
        ECIES_AES128_SHA256 = &ECIESParams{
            Hash: sha256.New,
            hashAlgo: crypto.SHA256,
            Cipher: aes.NewCipher,
            BlockSize: aes.BlockSize,
            KeyLen: 16,
            }

        """
        # 1) generate r = random value
        data = str_to_bytes(data)

        ephem = ECCx()

        # 2) generate shared-secret = kdf( ecdhAgree(r, P) )
        # ecc_pub = PublicKey(b'\x04' + raw_pubkey)
        # point = ecc_pub.multiply(ephem.secret)
        key_material = ephem.get_ecdh_key(raw_pubkey)
        # key_material = bytes(point.public_key.data)[:32]

        assert len(key_material) == 32
        key = eciesKDF(key_material, 32)
        assert len(key) == 32
        key_enc, key_mac = key[:16], key[16:]

        key_mac = sha256(key_mac).digest()  # !!!
        assert len(key_mac) == 32
        # 3) generate R = rG [same op as generating a public key]
        ephem_pubkey = ephem.pk.format(False)[1:]

        cipher = AES.new(key_enc, AES.MODE_CTR)

        # encrypt
        iv = Padding.pad(cipher.nonce, 16)
        assert len(iv) == 16

        ciphertext = cipher.encrypt(data)
        assert len(ciphertext) == len(data)

        # 4) send 0x04 || R || AsymmetricEncrypt(shared-secret, plaintext) || tag
        msg = ascii_chr(0x04) + ephem_pubkey + iv + ciphertext

        # the MAC of a message (called the tag) as per SEC 1, 3.5.
        tag = hmac_sha256(key_mac, msg[1 + 64:] + str_to_bytes(shared_mac_data))
        assert len(tag) == 32
        msg += tag

        assert len(msg) == 1 + 64 + 16 + 32 + len(data) == 113 + len(data)
        assert len(msg) - cls.ecies_encrypt_overhead_length == len(data)
        return msg

    def ecies_decrypt(self, data, shared_mac_data=b''):
        """
        Decrypt data with ECIES method using the local private key

        ECIES Decrypt (performed by recipient):
        1) generate shared-secret = kdf( ecdhAgree(myPrivKey, msg[1:65]) )
        2) verify tag
        3) decrypt

        ecdhAgree(r, recipientPublic) == ecdhAgree(recipientPrivate, R)
        [where R = r*G, and recipientPublic = recipientPrivate*G]

        """
        data = str_to_bytes(data)

        if data[:1] != b'\x04':
            raise ECIESDecryptionError("wrong ecies header")

        #  1) generate shared-secret = kdf( ecdhAgree(myPrivKey, msg[1:65]) )
        _shared = data[1:1 + 64]
        # FIXME, check that _shared_pub is a valid one (on curve)

        key_material = self.get_ecdh_key(_shared)

        assert len(key_material) == 32
        key = eciesKDF(key_material, 32)
        assert len(key) == 32
        key_enc, key_mac = key[:16], key[16:]

        key_mac = sha256(key_mac).digest()
        assert len(key_mac) == 32

        tag = data[-32:]
        assert len(tag) == 32

        # 2) verify tag
        if hmac_sha256(key_mac, data[1 + 64:- 32] + shared_mac_data) != tag:
            raise ECIESDecryptionError("Fail to verify data")

        # 3) decrypt
        blocksize = 16
        iv = data[1 + 64:1 + 64 + blocksize]
        assert len(iv) == 16

        ciphertext = data[1 + 64 + blocksize:- 32]
        assert 1 + len(_shared) + len(iv) + len(ciphertext) + len(tag) == len(
            data)
        cipher = AES.new(key_enc, AES.MODE_CTR, nonce=Padding.unpad(iv, 16))
        return cipher.decrypt(ciphertext)

    encrypt = ecies_encrypt
    decrypt = ecies_decrypt

    def sign(self, data):
        signature = ecdsa_sign(data, self.raw_privkey)
        assert len(signature) == 65
        return signature

    def verify(self, signature, message):
        assert len(signature) == 65
        return ecdsa_verify(self.raw_pubkey, signature, message)


def eciesKDF(key_material, key_len):
    """
    interop w/go ecies implementation

    for sha3, blocksize is 136 bytes
    for sha256, blocksize is 64 bytes

    NIST SP 800-56a Concatenation Key Derivation Function (see section 5.8.1).
    """
    s1 = b""
    key = b""
    hash_blocksize = 64
    reps = ((key_len + 7) * 8) / (hash_blocksize * 8)
    counter = 0
    while counter <= reps:
        counter += 1
        ctx = sha256()
        ctx.update(struct.pack('>I', counter))
        ctx.update(key_material)
        ctx.update(s1)
        key += ctx.digest()
    return key[:key_len]


def encrypt(data, raw_pubkey):
    """
    Encrypt data with ECIES method using the public key of the recipient.
    """
    assert len(raw_pubkey) == 64, 'invalid pubkey of len {}'.format(
        len(raw_pubkey))
    return ECCx.encrypt(data, raw_pubkey)
