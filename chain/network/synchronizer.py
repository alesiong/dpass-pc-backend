from typing import List

import gevent
from gevent.lock import BoundedSemaphore
import rlp

from chain.block import Block
from chain.blockchain import Blockchain
from chain.miner import Miner
from chain.storage import Storage
from chain.transaction import Transaction
from chain.transaction_pool import TransactionPool
from chain.transaction_tree import TransactionTree
from chain.transient_state import TransientState
from chain.utils import Singleton
from p2p.log import get_logger

log = get_logger('chain.network.synchronizer')


class Synchronizer(metaclass=Singleton):
    def __init__(self):
        self.__synchronizing = False
        self.__current_task = dummy_task
        self.__is_mining = False

    @property
    def synchronizing(self):
        return self.__synchronizing

    def synchronize(self, remote_pubkey, difficulty, proto, block=None, transaction_hashes=None):
        if difficulty < self.__current_task.difficulty:
            return
        self.__current_task.stop()
        self.__is_mining = Miner().is_mining
        Miner().stop()
        self.__synchronizing = True
        log.info('Synchronizing from', remote=proto.peer)
        self.__current_task = Task(remote_pubkey, difficulty, proto, block, transaction_hashes)

    def synchronize_with_block(self, remote_pubkey, latest_block_h, latest_block_t, proto):
        latest_block = Block.decode(latest_block_h, latest_block_t, True)
        difficulty = latest_block.difficulty
        if latest_block.previous_hash in Blockchain().block_mapping:
            # only sync the new block
            self.synchronize(remote_pubkey, difficulty, proto, latest_block, latest_block_t)
        else:
            self.synchronize(remote_pubkey, difficulty, proto)

    def finish(self):
        self.__synchronizing = False
        self.__current_task = dummy_task
        if self.__is_mining:
            Miner().start()

    # delegate methods
    def receive_chain(self, chain: List[bytes], key):
        if self.__current_task.difficulty != 0:
            self.__current_task.receive_chain(chain, key)

    def receive_blocks(self, blocks, key):
        if self.__current_task.difficulty != 0:
            self.__current_task.receive_blocks(blocks, key)

    def receive_transactions(self, transactions, id, key):
        if self.__current_task.difficulty != 0:
            self.__current_task.receive_transactions(transactions, id, key)


class Task:
    def __init__(self, remote_pubkey, difficulty, proto, block=None, transaction_hashes=None):
        self.key = remote_pubkey
        self.difficulty = difficulty
        self.__timeout = 10
        self.__timer = None
        self.__chain = Blockchain().chain.copy()
        self.__proto = proto

        self.__remain_synchronizing = 0
        self.__remain_synchronizing_lock = BoundedSemaphore()
        self.__original_length = len(self.__chain)

        self.__stopped = False

        if difficulty == 0:
            return

        self.state = TransientState()

        if block:
            block.previous = self.__chain[block.height - 1]
            self.__chain.append(block)
            transactions = rlp.decode(transaction_hashes)
            self.__remain_synchronizing = 1
            if transactions:
                self.__proto.send_request_transactions(transactions, block.height)
            else:
                block.transactions = TransactionTree([])
                self.finish_sync_block()
        else:
            proto.send_request_chain()

        self.time()

    def receive_chain(self, chain: List[bytes], key):
        if self.__stopped:
            return
        if key != self.key:
            return
        self.time()

        log.info('Received chain', len=len(chain))

        # determine the branching point
        i = 0
        for i in range(len(chain)):
            if i >= len(self.__chain):
                break
            if chain[i] != self.__chain[i].hash():
                break
        assert i >= 1
        if i < len(self.__chain):
            log.info('Branching detected, revert from', id=i)
            for b in self.__chain[-1:i - 1:-1]:  # [i, len(self.__chain))
                self.state.revert_block(b)
            self.__chain = self.__chain[:i]
            self.__original_length = i

        self.__proto.send_request_blocks(i)

    def receive_blocks(self, blocks, key):
        if self.__stopped:
            return
        if key != self.key:
            return
        self.time()

        log.info('Received blocks', len=len(blocks))
        self.__remain_synchronizing = len(blocks)

        try:
            for h, t in blocks:
                new_block = Block.decode(h, t, True)
                new_block.previous = self.__chain[new_block.height - 1]
                self.__chain.append(new_block)
                transactions = rlp.decode(t)
                if transactions:
                    self.__proto.send_request_transactions(transactions, new_block.height)
                else:
                    new_block.transactions = TransactionTree([])
                    self.finish_sync_block()
        except Exception as e:
            log.exception('Error when receiving blocks', e)
            self.stop()

    def receive_transactions(self, transactions, id, key):
        if self.__stopped:
            return
        if key != self.key:
            return
        self.time()

        log.info('Received transactions', id=id)

        block = self.__chain[id]
        transactions = TransactionTree([Transaction.decode(t) for t in transactions])
        block.transactions = transactions
        self.finish_sync_block()

    def finish_sync_block(self):
        if self.__stopped:
            return

        with self.__remain_synchronizing_lock:
            self.__remain_synchronizing -= 1
            if self.__remain_synchronizing == 0:
                self.finish()

    def finish(self):
        if self.__stopped:
            return
        assert self.difficulty != 0

        for i in range(self.__original_length, len(self.__chain)):
            block = self.__chain[i]
            if not block.verify(self.state):
                log.warning('Received block not valid', block=block)
                self.stop()
                return
            self.state.new_block(block)

        self.state.save()

        blockchain = Blockchain()
        blockchain.chain = self.__chain
        blockchain.rebuild_mapping()

        storage = Storage()

        for i in range(self.__original_length, len(self.__chain)):
            new_block = self.__chain[i]
            storage.store_block(new_block)
            for t in new_block.transactions.transactions:
                storage.store_transaction(t)
                TransactionPool().remove(t)

        storage.store_state()

        Synchronizer().finish()
        log.info('Synchronizing finished')

    def stop(self):
        self.__stopped = True
        if not self.difficulty != 0:
            Synchronizer().finish()

    def time(self):
        if self.__timer:
            self.__timer.kill()
        self.__timer = gevent.spawn_later(self.__timeout, self.stop)


dummy_task = Task(None, 0, None)
