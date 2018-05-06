import gevent

from gevent import Greenlet

from chain.block import Block
from chain.blockchain import Blockchain
from chain.state import State
from chain.storage import Storage
from chain.utils import Singleton
from p2p.log import get_logger

log = get_logger('chain.miner')


class Miner(Greenlet, metaclass=Singleton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__is_mining = False

    def start(self):
        self.__is_mining = True
        super(Miner, self).start()

    def stop(self):
        self.__is_mining = False

    @property
    def is_mining(self):
        return self.__is_mining

    def _run(self):
        blockchain = Blockchain()
        storage = Storage()
        while True:
            if not self.__is_mining:
                gevent.sleep(0.1)
                continue

            parent = blockchain.latest_block
            new_block = Block.create(parent, State().miner)
            r = None
            for r in new_block.mine():
                if not self.__is_mining:
                    break
                gevent.sleep()
            if r:
                blockchain.new_block(new_block)
                storage.store_block(new_block)
                for t in new_block.transactions.transactions:
                    storage.store_transaction(t)
                storage.store_state()

                from chain.control.main import DPChainApp
                DPChainApp().services.chain.broadcast_block(new_block.encode(), new_block.encode_transactions())
                log.info('Mined new block', num=new_block.height, block=new_block)
