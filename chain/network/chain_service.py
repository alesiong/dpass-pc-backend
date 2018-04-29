from chain.block import Block
from chain.blockchain import Blockchain
from chain.network.chain_protocol import ChainProtocol
from chain.network.synchronizer import Synchronizer
from chain.storage import Storage
from chain.transaction import Transaction
from chain.transaction_pool import TransactionPool
from p2p.log import get_logger
from p2p.service import WiredService

log = get_logger('chain.network.chain_service')


class ChainService(WiredService):
    name = 'chain'
    wire_protocol = ChainProtocol

    def __init__(self, app):
        self.config = app.config
        super(ChainService, self).__init__(app)

    def new_transaction(self, transaction: Transaction):
        self.broadcast_transaction(transaction.encode())

    def new_block(self, block: Block):
        self.broadcast_block(block.encode(), block.encode_transactions())

    def broadcast_transaction(self, encoded_transaction: bytes):
        log.debug('Broadcasting transaction')
        self.app.services.peermanager.broadcast(ChainProtocol, 'new_transaction', args=(encoded_transaction,))

    def broadcast_block(self, block_header: bytes, block_transaction: bytes):
        log.debug('Broadcasting block')
        self.app.services.peermanager.broadcast(ChainProtocol, 'new_block',
                                                args=(block_header, block_transaction))

    def on_wire_protocol_start(self, proto):
        assert isinstance(proto, self.wire_protocol)

        proto.receive_status_callbacks.append(self.on_status)
        proto.receive_new_transaction_callbacks.append(self.on_new_transaction)
        proto.receive_new_block_callbacks.append(self.on_new_block)
        proto.receive_request_chain_callbacks.append(self.on_request_chain)
        proto.receive_chain_callbacks.append(self.on_chain)
        proto.receive_request_blocks_callbacks.append(self.on_request_blocks)
        proto.receive_blocks_callbacks.append(self.on_blocks)
        proto.receive_request_transactions_callbacks.append(self.on_request_transactions)
        proto.receive_transactions_callbacks.append(self.on_transactions)

        chain = Blockchain()
        proto.send_status(capabilities=(
            self.app.config['capabilities']['miner'],
            self.app.config['capabilities']['bootstrap'],
            self.app.config['capabilities']['lightserver'],
            self.app.config['capabilities']['chainnode'],
        ),
            genesis_hash=chain.genesis.hash(),
            difficulty=chain.difficulty, latest_hash=chain.latest_block.hash())

    def on_status(self, proto, capabilities, genesis_hash, difficulty, latest_hash):
        chain = Blockchain()
        if genesis_hash != chain.genesis.hash():
            proto.send_disconnect(proto.disconnect.reason.useless_peer)
        if difficulty > chain.difficulty:
            Synchronizer().synchronize(proto.peer.remote_pubkey, difficulty, proto)

    def on_new_transaction(self, proto, encoded_transaction):
        log.debug('Receiving transaction')
        try:
            transaction = Transaction.decode(encoded_transaction)
        except Exception as e:
            log.exception('Error when receiving new transaction', e)
            return

        if not TransactionPool().add(transaction):
            log.warning('Received invalid transaction')

    def on_new_block(self, proto, header, transactions):
        Synchronizer().synchronize_with_block(proto.peer.remote_pubkey, header, transactions, proto)

    def on_request_chain(self, proto):
        blockchain = Blockchain()
        chain = [b.hash() for b in blockchain.chain]
        proto.send_chain(chain)

    def on_chain(self, proto, chain):
        Synchronizer().receive_chain(chain, proto.peer.remote_pubkey)

    def on_request_blocks(self, proto, from_index):
        chain = Blockchain()
        blocks = []
        for i in range(from_index, chain.length):
            blocks.append((chain.chain[i].encode(), chain.chain[i].encode_transactions()))

        proto.send_blocks(blocks)

    def on_blocks(self, proto, blocks):
        Synchronizer().receive_blocks(blocks, proto.peer.remote_pubkey)

    def on_request_transactions(self, proto, transaction_hashes, id):
        transactions = []
        storage = Storage()
        try:
            for th in transaction_hashes:
                transactions.append(storage.load_raw_transaction(th))
        except KeyError:
            return
        proto.send_transactions(transactions, id)

    def on_transactions(self, proto, transactions, id):
        Synchronizer().receive_transactions(transactions, id, proto.peer.remote_pubkey)
