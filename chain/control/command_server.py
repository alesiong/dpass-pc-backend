import gevent
from coincurve import PrivateKey, PublicKey
from rlp.utils import big_endian_to_int

from chain.blockchain import Blockchain
from chain.miner import Miner
from chain.network.synchronizer import Synchronizer
from chain.state import State
from chain.transaction import Transaction
from chain.transaction_pool import TransactionPool
from chain.utils import router
from p2p.log import get_logger

log = get_logger('chain.control.command_server')


@router.route('bootstrap/peers')
def get_peers():
    from chain.control.main import DPChainApp
    peers = DPChainApp().services.peermanager.peers
    ips = []
    for p in peers:
        try:
            ips.append(p.connection.getpeername()[0])
        except gevent.socket.error:
            pass
    return peers


@router.route('miner/start')
def start_miner():
    miner = Miner()
    if State().miner is None:
        log.warning('No miner, cannot start mining')
        return False
    if Synchronizer().synchronizing:
        log.warning('Synchronizing, cannot start mining')
        return False
    log.info('Mining started')
    miner.start()
    return True


@router.route('miner/stop')
def stop_miner():
    miner = Miner()
    log.info('Mining stopped')
    miner.stop()


@router.route('miner/account')
def set_miner_account(account: bytes):
    State().miner = PublicKey(account)


@router.route('block/get_latest')
def get_latest_block():
    return Blockchain().latest_block.encode(), Blockchain().latest_block.encode_transactions()


@router.route('block/get')
def get_block(hash: bytes):
    hash = hash.decode()
    blocks = Blockchain().get_block(hash)
    return [(b.encode(), b.encode_transactions()) for b in blocks]


@router.route('account/next_serial')
def get_next_serial(account: bytes):
    state = State()
    pool = TransactionPool()
    from_state = -1
    from_pool = -1
    try:
        _, serial = state.get_transactions_and_serial(account)
        from_state = max(serial)
    except (KeyError, ValueError):
        pass
    try:
        from_pool = max(pool.serials(account))
    except (KeyError, ValueError):
        pass
    return max(from_state, from_pool) + 1


@router.route('account/balance')
def get_balance(account: bytes):
    state = State()
    return state.get_balance(account)


@router.route('account/transactions')
def get_transactions(account: bytes):
    state = State()
    transactions, _ = state.get_transactions_and_serial(account)
    transactions = sorted(transactions, key=lambda e: e[0])
    return [(t[1], t[2]) for t in transactions]


@router.route('transaction/new')
def new_transaction(key: bytes, value: bytes, private_key: bytes, serial: bytes):
    serial = big_endian_to_int(serial)
    owner = PrivateKey.from_hex(private_key.decode())
    transaction = Transaction.new_transaction(owner, serial, key.decode(), value.decode())
    TransactionPool().add(transaction)
    from chain.control.main import DPChainApp
    DPChainApp().services.chain.broadcast_transaction(transaction.encode())

    return transaction.hash()


@router.route('transaction/in_pool')
def is_transaction_in_pool(transaction_hash: bytes):
    for t in TransactionPool().pool():
        if transaction_hash == t.hash():
            return False
    return True


@router.route('debug/get_pool')
def get_pool():
    transactions = list(TransactionPool().pool())
    return [t.encode() for t in transactions]
