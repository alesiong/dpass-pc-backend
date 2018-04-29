import binascii
from typing import List

from chain.block import Block
from chain.utils import Singleton


class Blockchain(metaclass=Singleton):
    def __init__(self):
        self.chain: List[Block] = [Block.genesis()]
        self.genesis = self.chain[0]

        self.block_mapping = {self.genesis.hash(): self.genesis}

    # def mine(self):
    #     i = 0
    #     s = 0
    #     print('No\tHash    \tDiff\tPeriod\tMean')
    #     for i in range(len(self.chain)):
    #         print(i, hexlify(self.chain[i].hash()).decode()[:8],
    #               self.chain[i].difficulty, sep='\t')
    #     while True:
    #         now = time.time()
    #         new_block = Block.create(self.chain[i], State().miner)
    #         try:
    #             new_block.mine()
    #             while new_block.timestamp > timestamp():
    #                 time.sleep(0.1)
    #         except KeyboardInterrupt:
    #             raise
    #
    #         self.new_block(new_block)
    #
    #         s += time.time() - now
    #         print(i + 1, hexlify(new_block.hash()).decode()[:8],
    #               new_block.difficulty, round(time.time() - now, 2),
    #               round(s / (i + 1), 2), sep='\t')
    #         i += 1

    def new_block(self, block: Block):
        from chain.state import State

        # block verifying should happen when receiving a block from remote
        self.chain.append(block)
        State().new_block(block)
        self.block_mapping[block.hash()] = block

    def get_block(self, hash_prefix: str) -> List[Block]:
        result = []
        for k, v in self.block_mapping.items():
            if binascii.hexlify(k).decode().startswith(hash_prefix):
                result.append(v)
        return result

    def rebuild_mapping(self):
        self.block_mapping = {b.hash(): b for b in self.chain}

    @property
    def latest_block(self) -> Block:
        return self.chain[-1]

    @property
    def length(self):
        return len(self.chain)

    @property
    def difficulty(self):
        return self.latest_block.difficulty
