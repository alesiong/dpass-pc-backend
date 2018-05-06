import random
from multiprocessing import Queue
from typing import Dict, Callable

import gevent
import rlp
from gevent import Greenlet, queue
from gevent.event import AsyncResult
from rlp.utils import big_endian_to_int

from chain.utils import Singleton
from p2p.log import get_logger

log = get_logger('chain.utils.multiplexer')

RESPONSE_TAG = b'\0\0\0'


class Multiplexer(Greenlet, metaclass=Singleton):
    def __init__(self, read_queue: Queue = None, write_queue: Queue = None):
        super().__init__()

        assert read_queue is not None
        assert write_queue is not None
        self.__read_queue = read_queue
        self.__write_queue = write_queue

        self.__sequence_number = set()
        self.__response_listener: Dict[int, Callable] = {}

        self.__listener: Dict[bytes, Callable] = {}
        self.__cached_messages = queue.Queue()

    def send(self, message: bytes, tag: bytes, need_response=True, response_seq=None):
        if need_response:
            seq = self.generate_seq()
            self.__sequence_number.add(seq)
        else:
            if response_seq is not None:
                seq = response_seq
            else:
                seq = 0
        msg = rlp.encode([tag, seq, message])
        if self.__write_queue.full():
            self.__cached_messages.put(msg)
        else:
            self.__write_queue.put(msg)
        if need_response:
            result = AsyncResult()

            def listener(v):
                result.set(v)

            self.__response_listener[seq] = listener
            return result

    def register(self, tag: bytes, listener: Callable):
        self.__listener[tag] = listener

    def __get_messages(self):
        if self.__read_queue.empty():
            return
        msg = self.__read_queue.get()
        tag, seq, message = rlp.decode(msg)
        seq = big_endian_to_int(seq)

        if tag == RESPONSE_TAG:
            # message is response from server
            self.__sequence_number.remove(seq)
            gevent.spawn(self.__response_listener[seq], message)
        else:
            try:
                def get_response():
                    response = self.__listener[tag](message)
                    if seq != 0:
                        self.send(response, RESPONSE_TAG, False, seq)

                gevent.spawn(get_response)
            except KeyError:
                log.warning('No matching listener', tag=tag, msg=message, seq=seq)

    def __send_cached_messages(self):
        if not self.__write_queue.full() and not self.__cached_messages.empty():
            msg = self.__cached_messages.get()
            self.__write_queue.put(msg)

    def stop(self):
        self.kill()

    def _run(self):
        while True:
            self.__get_messages()
            gevent.sleep(0.005)
            self.__send_cached_messages()
            gevent.sleep(0.005)

    def generate_seq(self):
        while True:
            seq = random.randint(1, 1 << 32)
            if seq not in self.__sequence_number:
                return seq
