import collections
import struct
from math import ceil

import rlp
from rlp.utils import encode_hex, str_to_bytes, bytes_to_str, decode_hex

int_to_big_endian = rlp.sedes.big_endian_int.serialize


def big_endian_to_int(s):
    return rlp.sedes.big_endian_int.deserialize(s.lstrip(b'\x00'))


def int_to_big_endian4(integer):
    ''' 4 bytes big endian integer'''
    return struct.pack('>I', integer)


def int_to_little_endian(value, byte_length=None):
    if byte_length is None:
        byte_length = max(ceil(value.bit_length() / 8), 1)
    return (value).to_bytes(byte_length, byteorder='little')


def little_endian_to_int(value):
    return int.from_bytes(value, byteorder='little')


def update_config_with_defaults(config, default_config):
    for k, v in default_config.items():
        if isinstance(v, collections.Mapping):
            r = update_config_with_defaults(config.get(k, {}), v)
            config[k] = r
        elif k not in config:
            config[k] = default_config[k]
    return config


node_uri_scheme = 'dpchain://'


def host_port_pubkey_to_uri(host, port, pubkey):
    assert len(pubkey) == 512 // 8
    uri = '{}{}@{}:{}'.format(node_uri_scheme,
                              bytes_to_str(encode_hex(pubkey)),
                              str(host), port)
    return str_to_bytes(uri)


def host_port_pubkey_from_uri(uri):
    b_node_uri_scheme = str_to_bytes(node_uri_scheme)
    b_uri = str_to_bytes(uri)
    assert b_uri.startswith(b_node_uri_scheme) and \
           b'@' in b_uri and b':' in b_uri, b_uri
    pubkey_hex, ip_port = b_uri[len(b_node_uri_scheme):].split(b'@')
    assert len(pubkey_hex) == 2 * 512 // 8
    ip, port = ip_port.split(b':')
    return ip, port, decode_hex(pubkey_hex)
