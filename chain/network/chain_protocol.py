import rlp

from p2p.protocol import BaseProtocol


class ChainProtocol(BaseProtocol):
    protocol_id = 1
    name = 'chain_protocol'
    max_cmd_id = 10

    def __init__(self, peer, service):
        self.config = peer.config
        super(ChainProtocol, self).__init__(peer, service)

    class status(BaseProtocol.command):
        cmd_id = 0
        structure = [('capabilities', rlp.sedes.CountableList(rlp.sedes.big_endian_int)),
                     ('genesis_hash', rlp.sedes.binary),
                     ('difficulty', rlp.sedes.big_endian_int),
                     ('latest_hash', rlp.sedes.binary)]

    class new_transaction(BaseProtocol.command):
        cmd_id = 1
        structure = [('encoded_transaction', rlp.sedes.binary)]

    class new_block(BaseProtocol.command):
        cmd_id = 2
        structure = [('header', rlp.sedes.binary), ('transactions', rlp.sedes.binary)]

    class request_chain(BaseProtocol.command):
        cmd_id = 3

    class chain(BaseProtocol.command):
        cmd_id = 4
        structure = [('chain', rlp.sedes.CountableList(rlp.sedes.binary))]

    class request_blocks(BaseProtocol.command):
        cmd_id = 5
        structure = [('from_index', rlp.sedes.big_endian_int)]

    class blocks(BaseProtocol.command):
        cmd_id = 6
        structure = [('blocks', rlp.sedes.CountableList(rlp.sedes.List([rlp.sedes.binary, rlp.sedes.binary])))]

    class request_transactions(BaseProtocol.command):
        cmd_id = 7
        structure = [('transaction_hashes', rlp.sedes.CountableList(rlp.sedes.binary)),
                     ('id', rlp.sedes.big_endian_int)]

    class transactions(BaseProtocol.command):
        cmd_id = 8
        structure = [('transactions', rlp.sedes.CountableList(rlp.sedes.binary)), ('id', rlp.sedes.big_endian_int)]
