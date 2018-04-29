import ipaddress
import re

from rlp.utils import is_integer, str_to_bytes, bytes_to_str

from p2p import kademlia, utils
from p2p.log import get_logger

log = get_logger('node_discovery.utils')

enc_port = lambda p: utils.int_to_big_endian4(p)[-2:]
dec_port = utils.big_endian_to_int
ip_pattern = re.compile(
    b"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|([0-9a-f]{0,4}:)*([0-9a-f]{0,4})?$")


class Address(object):
    """
    Extend later, but make sure we deal with objects
    Multiaddress
    https://github.com/haypo/python-ipy
    """

    def __init__(self, ip, udp_port, tcp_port=0, from_binary=False):
        tcp_port = tcp_port or udp_port
        if from_binary:
            self.udp_port = dec_port(udp_port)
            self.tcp_port = dec_port(tcp_port)
        else:
            assert is_integer(udp_port)
            assert is_integer(tcp_port)
            self.udp_port = udp_port
            self.tcp_port = tcp_port
        try:
            # `ip` could be in binary or ascii format, independent of
            # from_binary's truthy. We use ad-hoc regexp to determine format
            _ip = str_to_bytes(ip)
            _ip = bytes_to_str(ip) if ip_pattern.match(_ip) else _ip
            self._ip = ipaddress.ip_address(_ip)
        except ipaddress.AddressValueError as e:
            log.debug("failed to parse ip", error=e, ip=ip)
            raise e

    @property
    def ip(self):
        return str(self._ip)

    def update(self, addr):
        if not self.tcp_port:
            self.tcp_port = addr.tcp_port

    def __eq__(self, other):
        # addresses equal if they share ip and udp_port
        return (self.ip, self.udp_port) == (other.ip, other.udp_port)

    def __repr__(self):
        return 'Address(%s:%s)' % (self.ip, self.udp_port)

    def to_dict(self):
        return dict(ip=self.ip, udp_port=self.udp_port, tcp_port=self.tcp_port)

    def to_binary(self):
        """
        struct Endpoint
            unsigned address; // BE encoded 32-bit or 128-bit unsigned (layer3 address; size determins ipv4 vs ipv6)
            unsigned udpPort; // BE encoded 16-bit unsigned
            unsigned tcpPort; // BE encoded 16-bit unsigned        }
        """
        return list(
            (self._ip.packed, enc_port(self.udp_port), enc_port(self.tcp_port)))

    to_endpoint = to_binary

    @classmethod
    def from_binary(cls, ip, udp_port, tcp_port='\x00\x00'):
        return cls(ip, udp_port, tcp_port, from_binary=True)

    from_endpoint = from_binary


class Node(kademlia.Node):

    def __init__(self, pubkey, address=None):
        kademlia.Node.__init__(self, pubkey)
        assert address is None or isinstance(address, Address)
        self.address = address
        self.reputation = 0
        self.rlpx_version = 0

    @classmethod
    def from_uri(cls, uri):
        ip, port, pubkey = utils.host_port_pubkey_from_uri(uri)
        return cls(pubkey, Address(ip, int(port)))

    def to_uri(self):
        return utils.host_port_pubkey_to_uri(str_to_bytes(self.address.ip),
                                             self.address.udp_port, self.pubkey)
